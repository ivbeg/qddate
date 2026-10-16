# Tasks: Migrate pyparsing 3 legacy API names

## Migration

- [ ] Run a search-and-replace across `qddate/patterns/*.py`:
      - `setResultsName(` → `set_results_name(`
      - `oneOf(` → `one_of(`
      - `setParseAction(` → `set_parse_action(`
- [ ] Audit `qddate/qdparser.py` and `qddate/dirty.py` for the same legacy
      names; migrate if found.
- [ ] Audit any test fixtures.

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `pytest -W error::DeprecationWarning tests/` does not raise on the
      migrated files.
- [ ] `ruff check qddate tests scripts` clean.
- [ ] `mypy qddate/__init__.py qddate/qdparser.py` clean.