# Design: Refactor pattern metadata

Implementation notes for `changes/refactor-pattern-metadata/`. This change is
behavior-preserving, so there is **no delta spec** — the externally observable
contract is unchanged. This file captures the *how*.

## Target pattern shape

```python
{
    "key": "dt:date:de_base",
    "language": "de",          # NEW; None for language-neutral numeric patterns
    "separator": "space",      # NEW: slash|dot|dash|space|none|mixed
    "pattern": <pyparsing expr>,
    "length": {"min": 11, "max": 22},
    "format": "%d %m %Y",
    "filter": 1,
}
```

## Migration strategy

1. **Add fields, don't remove inference yet.** First pass: backfill `language` and
   `separator` on every pattern while keeping the old substring inference alive. This
   keeps the tree green at every commit and lets the differential test (below) validate
   the new fields against the old logic.
2. **Swap consumers one at a time.** Replace each of the three inference sites
   (`_infer_char_sets`, `_build_language_index`, `_build_separator_index`) individually,
   running the differential test after each swap.
3. **Delete the dead code.** Once all consumers use the fields, remove the substring
   branches and the `dirty.py` basekey lists.

## dirty.py derivation

Group patterns once at import:

```python
_BY_SEPARATOR = {}   # separator -> tuple of basekeys
_BY_LANGUAGE  = {}   # language  -> tuple of basekeys
for p in ALL_PATTERNS:
    _BY_SEPARATOR.setdefault(p["separator"], []).append(p["key"])
    if p.get("language"):
        _BY_LANGUAGE.setdefault(p["language"], []).append(p["key"])
```

`matchPrefix()` then reads these dicts instead of the hand-maintained `_XX_BASEKEYS`.
If benchmarks show the dict lookups are slower than the frozen tuples, freeze the
results into module-level constants computed once at import — same values, no manual
maintenance.

## Month/weekday helper

```python
def month_table(full, *, lc=None, short=None, genitive=None):
    """Build a oneOf month matcher and a name->number map.

    Returns (parser_element, name_to_number). Each variant list, if given, is
    indexed in calendar order so month numbers are correct.
    """
```

Each `patterns/xx.py` then reduces to a few calls and a list of pattern dicts that
only differ in structure, not in boilerplate.

## Differential test (safety net)

Before any deletion, snapshot `matchPrefix(text[:6])` and the full filtered candidate
set for a large corpus of real inputs (reuse `benchmarks/` test data). After each
swap, assert byte-identical candidate sets. This is the gate that proves the refactor
is behavior-preserving.

## Risks

- **Perf regression** from dict-of-lists vs. frozen tuples. Mitigated by freezing at
  import if needed; verified by `benchmarks/bench.py`.
- **Missed a pattern** during backfill. Mitigated by the coverage test (every key
  reachable through every index).
