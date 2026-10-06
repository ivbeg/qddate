# Tasks: Add format_date helper for round-trip normalization

## Implementation

- [ ] In `qddate/qdparser.py`, add `format_date(dt, pattern_key)` function:
      resolves `pattern_key` against `ALL_PATTERNS`, looks up the
      corresponding `format` strftime string, and calls `dt.strftime(format)`.
- [ ] On `ValueError` if the pattern key is not in `ALL_PATTERNS`.
- [ ] Add `format_date(dt, pattern_key)` instance method on `DateParser` that
      delegates to the standalone function.
- [ ] Add `format_date()` instance method on `DateMatch` that uses
      `self.format` and `self.datetime`.
- [ ] Re-export `format_date` from `qddate/__init__.py` so it is part of the
      public API.

## Documentation

- [ ] Add a brief section to `docs/docs/api/dateparser.md` documenting the new
      helper.
- [ ] Add a small example to `README.md` ("Format a parsed date back to a
      locale-aware string").

## Verification

- [ ] Add `tests/test_format_date.py` with:
      - Round-trip test: `format_date(parse("6 Jan 2009").datetime,
        pattern_key="dt:date:date_eng1_short") == "6 Jan 2009"`.
      - Unknown pattern key raises `ValueError`.
      - `DateMatch.format_date()` works without explicit pattern key.
      - Locale preservation: a Russian date string round-trips with
        `dt:date:date_rus1_short`.
- [ ] `pytest tests/` passes 100%.
- [ ] `pytest --cov=qddate --cov-fail-under=85` passes (no coverage drop).
- [ ] `ruff check qddate tests scripts` is clean.