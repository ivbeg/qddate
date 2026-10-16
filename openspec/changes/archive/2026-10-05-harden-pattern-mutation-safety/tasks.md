# Tasks: Harden pattern mutation safety

## Move stamping

- [ ] Audit every `pat[...]= ...` write inside `__generate()` in
      `qddate/qdparser.py`.
- [ ] Move each write into `annotate_patterns()` in `qddate/patterns/__init__.py`,
      idempotently (e.g. `pat.setdefault("required_chars", ...)`).
- [ ] Verify that for any `pat` in `ALL_PATTERNS`, every field set by
      `annotate_patterns()` matches the field set by `__generate()` for the
      same `pat`.

## Add immutability snapshot test

- [ ] Add `tests/test_pattern_immutability.py` that snapshots the content of
      `qddate.patterns.ALL_PATTERNS` (deep copy), constructs 5 `DateParser()`
      instances, and asserts the snapshot is identical afterward.
- [ ] Add an explicit assertion that `__generate()` does not mutate
      `ALL_PATTERNS` (e.g. by checking that calling `__generate()` repeatedly
      leaves `ALL_PATTERNS[i]` byte-identical).

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `pytest --cov=qddate --cov-fail-under=85` passes.
- [ ] `ruff check qddate tests scripts` is clean.