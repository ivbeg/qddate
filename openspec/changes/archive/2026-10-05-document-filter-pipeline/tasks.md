# Tasks: Document the six-level filter pipeline

## Documentation

- [ ] Create `docs/docs/api/filter-pipeline.md` documenting each filter
      level (length, separator, year format, language, charset, prefix).
- [ ] Add a section on the cost of disabling each filter.
- [ ] Link the page from `docs/docs/api/match.md` and `docs/docs/api/parse.md`.
- [ ] Add a reference in `docs/sidebars.js` so the page appears in the docs
      sidebar under "API Reference".

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `mypy qddate/__init__.py qddate/qdparser.py` clean.
- [ ] `ruff check qddate tests scripts` clean.
- [ ] Docusaurus build (if run locally) succeeds.