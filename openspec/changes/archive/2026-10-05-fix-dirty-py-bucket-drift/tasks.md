# Tasks: Fix dirty.py bucket drift

## Snapshot current behavior

- [ ] Run the parser on the existing probe corpus and snapshot
      `matchPrefix(text[:6])` for each input. Store under
      `tests/fixtures/dirty_py_bucket_snapshot.json` for use in the parity test.

## Add derivation pass (default off)

- [ ] In `qddate/dirty.py`, add a `_build_buckets()` function that groups
      `ALL_PATTERNS` by `(separator, language)` using the stamped metadata.
- [ ] Wrap the existing `matchPrefix` body so that both the hand-synced buckets
      *and* the derived buckets exist; expose a `use_derived_buckets: bool = False`
      switch to the function.
- [ ] Add a parity test
      (`tests/test_regressions_2026_09.py::test_dirty_buckets_derive_to_same_set`)
      that asserts `matchPrefix(text[:6], use_derived=True) == matchPrefix(text[:6])`
      for every probe string.

## Flip the default

- [ ] Change the default to `use_derived_buckets=True`.
- [ ] Run `pytest tests/` — must be green (modulo any shadowed-pattern failures
      unrelated to this change).
- [ ] Run `pytest tests/test_regressions_2026_09.py::test_every_pattern_matches_some_probe`
      separately — must be green (or at least no worse than before).

## Remove the hand-synced lists

- [ ] Delete the `_ALPHA_*`, `_DE_*`, `_ES_*`, `_IT_*`, `_NL_*`, `_FR_*`,
      `_PT_*`, `_PL_*`, `_CZ_*`, `_RO_*`, `_UK_*`, `_BG_*`, `_TR_*`, `_SLASH_*`,
      `_DASH_*`, `_DOT_*`, `_RUS_*` lists from `dirty.py`.
- [ ] Delete the `_ALPHA_*_FULL` / `_DOT_SEPARATOR_FULL` / `_DEFAULT_DIGIT_FULL`
      tuples.
- [ ] Delete the `use_derived_buckets` switch (now always on).
- [ ] Keep `_NUMERIC_PATTERN_KEYS` (used elsewhere).

## Update the safety-net test

- [ ] Rewrite `test_every_pattern_key_in_some_prefix_bucket` to scan the
      derived buckets instead of `dir(dirty)`.
- [ ] Keep `test_bucket_keys_exist_in_metadata` as-is (still useful).
- [ ] Keep the new `test_dirty_buckets_derive_to_same_set` as the regression
      net for the derivation logic.

## Verification

- [ ] `pytest tests/` passes 100% (reachability oracle included).
- [ ] `python -m ruff check qddate/dirty.py` reports no new errors.
- [ ] Manual sanity check: `DateParser().parse("12.03.1999 Hello people")` still
      returns `datetime.datetime(1999, 3, 12)`.
- [ ] Manual sanity check: `DateParser(languages=["en","de"]).parse("28. Juli 2015")`
      still returns `datetime.datetime(2015, 7, 28)`.