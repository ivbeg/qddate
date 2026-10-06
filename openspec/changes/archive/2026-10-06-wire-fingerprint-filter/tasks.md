# Tasks

## 1. Design

- [x] Review the existing 6-level pipeline (`_filter_patterns_hierarchical`)
- [x] Identify which dimensions are already covered by `candidate_keys_for`
- [x] Identify the merge logic that lives in the existing pipeline
      (space+slash+mixed, noyear keep-when-not-4digit, language allow-list)
- [x] Decide on additive opt-in flag (`use_fingerprint=False`) to keep
      default behaviour unchanged

## 2. Implementation

- [ ] Add `use_fingerprint: bool = False` to `DateParser.__init__`
- [ ] Implement `_filter_patterns_fingerprint(text, n, noprefix=False, allow_no_year=True, nocharsetfilter=False, noseparatorfilter=False, noyearformatfilter=False, nolanguagefilter=False)` in `qddate/qdparser.py`
- [ ] Route `match()`, `match_all()`, `parse()` to the new method when `use_fingerprint=True`
- [ ] Document the method with reference to the parity test

## 3. Tests

- [ ] `tests/test_fingerprint_parity.py` — superset-of-legacy assertion on every probe string from the existing reachability corpus
- [ ] `tests/test_fingerprint_parity.py` — `use_fingerprint=False` produces the legacy candidate set exactly
- [ ] `tests/test_fingerprint_parity.py` — feature flag is honoured by `match()`, `match_all()`, `parse()`
- [ ] Existing 371 tests still pass

## 4. Documentation

- [ ] Module docstring on the new method explaining its scope
- [ ] Note in `IMPROVEMENT_PLAN.md` §6.3 marking the consumer wiring as
      "opt-in, parity locked"

## 5. Verification

- [ ] `pytest tests/ --cov=qddate --cov-fail-under=85 -q` — 371 + new tests pass
- [ ] `ruff check qddate tests scripts openspec` — clean
- [ ] `mypy qddate/__init__.py qddate/qdparser.py` — clean

## 6. Archive

- [ ] `openspec validate wire-fingerprint-filter`
- [ ] `openspec archive wire-fingerprint-filter -y`