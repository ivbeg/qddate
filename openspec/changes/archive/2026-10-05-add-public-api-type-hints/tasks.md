# Tasks: Add type hints to the public API

## Annotate `DateParser`

- [ ] In `qddate/qdparser.py`, add a `from __future__ import annotations` line
      (PEP 563 — postpones evaluation, keeps runtime cost zero).
- [ ] Add type hints to `DateParser.__init__`.
- [ ] Add type hints to `DateParser.parse`, `match`, `match_all`,
      `match_typed`, `parse_many`.
- [ ] Add type hints to `DateParser.format_date`.
- [ ] If needed, add `TYPE_CHECKING` imports for `DateMatch`, `dict`, `list`,
      etc.

## Annotate `DateMatch`

- [ ] Add hints to the dataclass fields: `datetime: datetime`,
      `pattern_key: str`, `language: str | None`, `format: str`,
      `raw: str`.
- [ ] Annotate `to_dict()` return type.

## Verify

- [ ] `pytest tests/` passes 100%.
- [ ] `mypy qddate` runs without errors on the public API (best-effort; do
      not add `mypy --strict`).
- [ ] `ruff check qddate tests scripts` is clean.