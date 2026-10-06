# Tasks: Rename `noyear=` to `allow_no_year=`

## Implementation

- [ ] In `qddate/qdparser.py`, rename the keyword in `parse`, `match`, and
      `match_all` from `noyear` to `allow_no_year`.
- [ ] Add a back-compat alias: accept `noyear` as a deprecated kwarg and
      issue `warnings.warn("noyear= is deprecated, use allow_no_year=",
      DeprecationWarning, stacklevel=2)` if it's the only deprecated name.
- [ ] Update `__init__` if it forwards `noyear` (currently it doesn't, but
      audit).
- [ ] Confirm `match_typed` and `parse_many` forward kwargs unchanged.

## Tests

- [ ] Add `tests/test_noyear_deprecation.py` with:
      - `test_noyear_param_emits_deprecation_warning` — calls
        `parse(..., noyear=True)` and asserts a `DeprecationWarning` is
        raised with the expected message.
      - `test_allow_no_year_default_unchanged` — asserts the default produces
        the same parse results as the old `noyear=True` (no behaviour
        change).
      - `test_allow_no_year_false_disables_no_year` — asserts `allow_no_year=False`
        returns `None` for `"05.12"` (the no-year pattern).

## Documentation

- [ ] Update `docs/docs/api/parse.md`, `docs/docs/api/match.md`, and
      `docs/docs/api/dateparser.md` to use `allow_no_year=`.
- [ ] Update `README.md` if it uses `noyear=`.
- [ ] Add a `deprecation-policy.md` (optional) explaining the
      2-releases-before-removal schedule.

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `python -W error::DeprecationWarning -c "import qddate; qddate.DateParser().parse('05.12')"` does not raise (no `noyear=` passed).
- [ ] `ruff check qddate tests scripts` clean.
- [ ] `mypy qddate/__init__.py qddate/qdparser.py` clean.