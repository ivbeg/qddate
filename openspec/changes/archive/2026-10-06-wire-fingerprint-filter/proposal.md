# Wire fingerprint index into `_filter_patterns_hierarchical`

## Why

The data layer for the fingerprint index shipped in round 6
(`fingerprint-based-matcher` change, archived). What remained was to wire
the intersection into the hot path so the 6-level filter pipeline can
collapse into one operation.

This change does **not** delete the existing pipeline. It adds a
`use_fingerprint=True` constructor flag (default-off so existing behaviour
is preserved bit-for-bit), runs the fingerprint-based path on every input,
and asserts the candidate set is **equal** to the legacy 6-level path on a
representative set of probe strings. Once parity is locked, a future change
flips the default.

## Scope

**In scope (this change):**
- New `DateParser.__init__` parameter `use_fingerprint: bool = False`.
- New method `_filter_patterns_fingerprint(text, n, ...)` that calls
  `candidate_keys_for(...)` from `qddate.patterns.fingerprint` and returns
  the candidate pattern dicts (not just keys).
- When `use_fingerprint=True`, `match()` / `match_all()` / `parse()`
  route through the new method. When `False`, the existing pipeline runs.
- New parity test `tests/test_fingerprint_parity.py` asserting that for
  every probe string in the existing reachability corpus, the
  fingerprint-based path produces a **superset-or-equal** of the legacy
  path's candidate set. (Superset, not equal, is the conservative target —
  fewer false negatives is the only safety property that matters for
  matching; superset means we won't drop a pattern the existing pipeline
  kept.)
- Documentation note in `_filter_patterns_hierarchical` and the new method.

**Out of scope (future change):**
- Defaulting `use_fingerprint` to `True`. Requires running the full
  test corpus and confirming exact (not just superset) equivalence.
- Removing the existing 6-level pipeline. Belt-and-braces: keep both
  pipelines as long as either is the default.
- Performance optimizations that change the call signature.

## Acceptance criteria

- `pytest tests/test_fingerprint_parity.py -v`: every probe string yields
  fingerprint_candidates ⊇ legacy_candidates.
- `pytest tests/`: existing 371 tests pass with `use_fingerprint=False`
  (default). When the test is run with `use_fingerprint=True`, parity
  holds on every probe string.
- `ruff check qddate tests scripts openspec`: clean.
- `mypy qddate/__init__.py qddate/qdparser.py`: clean.
- Coverage of the new method ≥ 90%.
- No change to `qddate.__version__` (constructor parameter is additive;
  default behaviour is unchanged).

## Rollback plan

`use_fingerprint=False` is the default, so disabling the new path is the
default. No data migration, no schema change. Rollback is `git revert`.