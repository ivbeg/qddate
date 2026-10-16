# Tasks

## 1. Implement deprecation warning

- [ ] Add `import warnings` to `qddate/qdparser.py` if not already imported
- [ ] In `DateParser.__init__`, emit `DeprecationWarning("use_fingerprint=False is deprecated; the legacy 6-level filter will be removed in v2.0.0")` when the caller explicitly passes `False`
- [ ] Update docstring on `use_fingerprint` parameter

## 2. Tests

- [ ] `tests/test_fingerprint_parity.py`: wrap the legacy fixture with `pytest.warns(DeprecationWarning)` so the deprecation is expected
- [ ] Add `tests/test_deprecations.py` (or extend existing) asserting `use_fingerprint=False` produces a warning
- [ ] Existing 536 tests still pass

## 3. Version bump + changelog

- [ ] `qddate/__init__.py`: bump to `1.0.15`
- [ ] `pyproject.toml`: bump to `1.0.15`
- [ ] `docs/docs/development/deprecation-policy.md`: add the new deprecation entry under "Active deprecations"
- [ ] `CHANGELOG.md`: add `## 1.0.15` section
- [ ] `IMPROVEMENT_PLAN.md` §6.3: note removal target

## 4. Verification

- [ ] `pytest tests/ --cov=qddate --cov-fail-under=85 -q`: 536+ tests pass
- [ ] `pytest -W error::DeprecationWarning tests/test_deprecations.py`: passes
- [ ] `ruff check qddate tests scripts openspec`: clean
- [ ] `mypy qddate/__init__.py qddate/qdparser.py`: clean
- [ ] `python -c "import qddate; print(qddate.__version__)"` → `1.0.15`

## 5. Archive

- [ ] `openspec validate deprecate-legacy-filter-path`
- [ ] `openspec archive deprecate-legacy-filter-path -y`