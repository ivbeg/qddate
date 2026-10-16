# Design: Fix dirty.py bucket drift

Implementation notes for `changes/fix-dirty-py-bucket-drift/`. This is a
behavior-preserving refactor (the externally observable contract is unchanged).
This file captures the *how*.

## Current state (before)

`dirty.py` defines ~15 hand-synced basekey lists:

```python
_ALPHA_ENGLISH_BASEKEYS = ["dt:date:date_eng2", ...]
_DE_BASEKEYS = ["dt:date:de_base", ...]
_DOT_SEPARATOR_BASEKEYS = ["dt:date:date_2", ...]
# etc.

_ALPHA_ENGLISH_FULL = tuple(_ALPHA_ENGLISH_BASEKEYS + _PT_BASEKEYS + ...)
_DOT_SEPARATOR_FULL = tuple(_DOT_SEPARATOR_BASEKEYS + _DE_BASEKEYS)
# etc.
```

`matchPrefix(text)` reads these tuples to decide which patterns are eligible
based on the input's leading characters.

## Target state (after)

A single derivation pass over `_PATTERN_METADATA` produces the same logical
groups, plus a few that the hand-synced lists lack (because every basekey is in
exactly one bucket by construction — no manual union needed).

```python
# At import time, after annotate_patterns(ALL_PATTERNS):
from .patterns import ALL_PATTERNS

def _build_buckets():
    """Group pattern basekeys by (separator, language) using stamped metadata.

    The grouping strategy:
    - Numeric language-neutral keys are bucketed by separator (slash/dot/dash/none).
    - Language-tagged keys are bucketed by separator AND language.
    - Mixed-fallback bucket holds anything not yet classified (defensive).
    """
    by_sep = {}      # separator -> set[str]
    by_lang = {}     # language  -> set[str]
    for p in ALL_PATTERNS:
        sep = p.get("separator", "mixed")
        lang = p.get("language")
        by_sep.setdefault(sep, set()).add(p["key"])
        if lang:
            by_lang.setdefault(lang, set()).add(p["key"])

    # Combined view used by matchPrefix.
    return {
        # separator-only views (used for digit-prefixed inputs)
        "dot":       tuple(sorted(by_sep.get("dot",   set()))),
        "slash":     tuple(sorted(by_sep.get("slash", set()))),
        "dash":      tuple(sorted(by_sep.get("dash",  set()))),
        "none":      tuple(sorted(by_sep.get("none",  set()))),
        "space":     tuple(sorted(by_sep.get("space", set()))),
        # language views (used for alpha-prefixed inputs)
        "alpha_en":  tuple(sorted(by_lang.get("en", set()))),
        "alpha_de":  tuple(sorted(by_lang.get("de", set()))),
        "alpha_es":  tuple(sorted(by_lang.get("es", set()))),
        # ...
    }
```

`matchPrefix` then reads these derived tuples, sorted the same way the
hand-synced lists were sorted (lexicographic for stable test output).

## Migration strategy

1. **Add the derived buckets alongside the hand-synced ones**, behind a flag
   (default off). Add a parity test that asserts both code paths return the
   same candidate set for a corpus of probe strings.
2. **Flip the flag to default-on.** Verify all existing tests still pass;
   verify the reachability oracle passes with the existing probe corpus.
3. **Delete the hand-synced lists and the flag.** Update the safety-net test
   to target the derived buckets directly.

## Safety net

- **Parity test:** snapshot `matchPrefix(text[:6])` for a corpus of ~100 inputs
  covering every language/separator combination. Run against the old code path
  first, store the snapshot. After each migration step, re-run and assert
  identical results.
- **Existing oracle:** `test_every_pattern_matches_some_probe` already catches
  net losses; the new derived buckets must keep every probe passing.
- **Existing coverage test:** `test_every_pattern_key_in_some_prefix_bucket`
  gets rewritten to scan the derived buckets instead of the hand-synced ones.

## Risks

- **Disagreement with hand-synced lists.** If the derivation produces a
  *different* bucket than the author intended (e.g. an author excluded a pattern
  from a bucket deliberately), the parity test will catch it. Mitigation:
  investigate each disagreement before flipping the flag.
- **Performance.** Dict lookups are O(1) but introduce cache misses compared to
  pre-bound tuple locals. Mitigation: bind the derived tuples to module-level
  names so `matchPrefix` reads a local.

## What we deliberately do NOT do

- **Do not** try to deduplicate the buckets. The hand-synced lists intentionally
  contain keys in multiple buckets (e.g. `date_1` appears in both
  `_SLASH_SEPARATOR_BASEKEYS` and `_EXTENDED_DIGIT_BASEKEYS`). The derivation
  just needs to *contain* them in the same combined views; de-dup is done by
  `matchPrefix` itself.
- **Do not** remove the `_NUMERIC_PATTERN_KEYS` set from `qdparser.py`. That
  set is used by `_infer_char_sets`, not by `dirty.py`, and is a separate
  concern.