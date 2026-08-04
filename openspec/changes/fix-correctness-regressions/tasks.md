# Tasks: Fix correctness regressions

## Languages filter

- [ ] In `_filter_patterns_hierarchical` Level 4 (language filter), when a user
  allow-list is in effect, intersect detected languages with the allow-list and skip
  narrowing to a single language if that language is not in the allow-list.
- [ ] Add a regression test: `DateParser(languages=["en","de"]).parse("28. Juli 2015") == datetime(2015,7,28)`.
- [ ] Add a regression test for a shared-name case in the reverse direction
  (Dutch requested, German-like input should not leak in via detection).

## Drifted tests

- [ ] Move `14th April 2015:`, `15. Jul 2023`, `5. jan 2020` from
  `test_parse_returns_none_for_unsupported_text` into `test_parse_supported_text`
  with expected datetimes (`2015-04-14`, `2023-07-15`, `2020-01-05`).
- [ ] Confirm no other parametrized "None" case now returns a datetime (audit the
  full parametrize list against current behavior).

## Weekday typo

- [ ] Fix `ENG_WEEKDAYS`: `"Satuday"` → `"Saturday"` in `qddate/patterns/base.py`.
- [ ] Add a test: `parse("Saturday 4 April 2019") == datetime(2019,4,4)`.

## Broken `__main__` block

- [ ] Rewrite or delete the `if __name__ == "__main__"` block in `qddate/qdparser.py`.
- [ ] If kept, use `ind.parse(text)` and remove the unguarded `dateparser` reference.

## Verification

- [ ] `pytest -q` is fully green (0 failures).
- [ ] Add the new cases to CI so the regression cannot recur.
