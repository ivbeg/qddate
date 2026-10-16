# Design — Fingerprint-based matcher

## 1. Background

`DateParser._filter_patterns_hierarchical()` runs six independent filter
passes in sequence:

| # | Pass              | Bucket source                                          | Dimension                                 |
|---|-------------------|--------------------------------------------------------|-------------------------------------------|
| 1 | Length            | `_patterns_by_length[n]`                               | `length_min ≤ len(text) ≤ length_max`     |
| 2 | Character set     | (inline linear scan)                                   | `required_chars ≤ text_char_sets`         |
| 3 | Separator         | `_patterns_by_separator[sep]`                          | separator in `{slash, dot, dash, …}`     |
| 4 | Language          | `_patterns_by_language[lang]`                          | detected language ∈ pattern language      |
| 5 | Year format       | `_patterns_by_year_format[bucket]`                     | year format ∈ {4digit, 2digit, noyear, any} |
| 6 | Prefix            | `_matchPrefix(text[:6])`                               | first 6 chars match a known prefix        |

Each bucket is built **per `DateParser` instance** (in `__init__`,
`_build_length_index()`, `_build_separator_index()`, …) and each pass has its
own branching logic. The custom merge rules ("when space detected, also
include slash + mixed", "when 4-digit year not detected, also include
noyear", …) live in the hot path. Total: ~200 lines of branching across
`_filter_patterns_hierarchical` + the four `_build_*_index` helpers.

## 2. Fingerprint key

```python
class FingerprintKey(NamedTuple):
    length_min: int
    length_max: int
    chars: frozenset[str]            # the pattern's required_chars (CHAR_SET_* flags)
    separator: str                   # one of 'slash', 'dot', 'dash', 'space', 'none', 'mixed', 'any'
    language: Optional[str]         # 'en', 'ru', … or None for language-agnostic
    year_format: str                # one of '4digit', '2digit', 'noyear', 'any'
```

`compute_pattern_fingerprint(pattern)` reads these off the pattern dict (and
its `_PATTERN_METADATA` basekey where separator/cover metadata is single-word).
The function is **pure** and **idempotent** (verified by test).

The index is built once at module import:

```python
_PATTERN_FINGERPRINTS: dict[FingerprintKey, frozenset[str]] = {}
for p in ALL_PATTERNS:
    fp = compute_pattern_fingerprint(p)
    bucket = _PATTERN_FINGERPRINTS.setdefault(fp, frozenset())
    _PATTERN_FINGERPRINTS[fp] = bucket | {p["key"]}
```

`ALL_PATTERNS` carries ~1,072 generated patterns → ~700 unique fingerprint
tuples (many generated variants share the same fingerprint).

## 3. Projections (the consumer round will use these)

For each of the six legacy buckets, the equivalent fingerprint projection:

```python
def patterns_by_length(n: int) -> set[str]:
    return {key for fp, keys in _PATTERN_FINGERPRINTS.items()
            if fp.length_min <= n <= fp.length_max
            for key in keys}
```

Equivalent helpers exist for `by_separator`, `by_language`, `by_year_format`.
The character-set filter is the only dimension that can't be a pure
projection — see next section.

## 4. Character-set handling

The current linear scan keeps patterns whose required set is a subset of the
text's char sets, with one substitution**: `CHAR_SET_ACCENTED` in the
required set is allowed when the text has `CHAR_SET_LATIN` instead (since
every accented Latin char has an unaccented counterpart).

Fingerprint model for char sets: the index is keyed by the **pattern's
required_chars**. At match time, the consumer builds the text's
`text_char_sets` (already done by `scan_char_sets`) and walks all buckets
whose key is `<= text_char_sets` (or `<= text_char_sets ∪ {LATIN}` when the
key contains ACCENTED). The union of those buckets is the candidate set.

This is still a single pass through the index (the linear scan is replaced
by an index lookup), but no longer a per-pattern loop.

## 5. Why split into two rounds

The fingerprint index is **pure data** and trivially testable. Replacing
the existing 6-level filter with an intersection of fingerprint buckets is
**behaviour logic** — every existing edge case (the
`space + slash + mixed` merge, the `noyear` keep-when-not-4digit rule, the
language-allow-list interaction with the German "Juli" regression fix)
needs to be re-derived.

This round ships the data + projection helpers + parity tests. A future
round wires `_filter_patterns_hierarchical` to call `intersect_fingerprints`
and asserts exact equivalence with the existing pipeline on the 345-test
corpus. If any divergence is found, fall back to the existing pipeline
under a feature flag.

## 6. Performance expectations (after the consumer round)

Today the per-input cost is roughly:

| Pass | Work                                    | Today             |
|------|----------------------------------------|-------------------|
| 1    | Dict lookup                            | O(1)              |
| 2    | Linear scan with set ops              | O(P · |chars|)    |
| 3    | Bucket lookup + small merge             | O(P_in_sep)       |
| 4    | Detect (O(L)) + bucket lookup         | O(L)              |
| 5    | Detect (O(L)) + bucket lookup         | O(L)              |
| 6    | Bucket lookup via `_matchPrefix`       | O(P_prefix)       |

P = number of candidates after each pass, P_in_X = patterns in bucket X,
L = text length, |chars| = number of distinct char-set flags (~4).

After the fingerprint intersection:

- Level 1 is implicit (the index doesn't carry patterns with a mismatched
  length range at all).
- Level 2 becomes a single index walk over `<= text_char_sets` buckets.
- Levels 3–5 collapse to one pass over the per-dimension projection.
- Level 6 stays.

Expected net effect: **fewer object allocations** (no list-of-patterns
copies after each pass) and **tighter inner loops** (single dict walk vs
six independent passes). Performance measurements on the existing
`tests/perf_smoke` corpus after the consumer round will quantify it.

## 7. Risk

- **Risk: charset substitution edge cases.** The `CHAR_SET_ACCENTED → LATIN`
  substitution must be preserved exactly. The parity test
  `test_fingerprint_subset_for_canonical_inputs` runs every canonical input
  from the existing probe corpus and asserts `intersect_fingerprints`
  returns a superset-or-equal of the current pipeline.
- **Risk: pattern mutation.** Same discipline as `required_chars` stamping:
  `annotate_patterns()` adds the fingerprint at import time; `_DateParser__generate`
  copies it into the per-instance pattern dict without recomputation.
- **Risk: language=None vs language="en".** Month-name patterns carry
  `language=...`. Language-agnostic numeric patterns have `language=None`.
  The intersection must treat "text language unknown" as a wildcard — the
  consumer round's filter logic handles this.
- **Risk: bucket explosion.** With ~1,072 patterns and 6 dimensions, the
  full Cartesian product is huge. In practice each pattern has one tuple,
  and the index has ~700 entries. We can add an `__index_size__` test to
  alarm if this grows past 1,500.