# Tasks: Add relative date parsing

## Implementation

- [ ] In `qddate/relative.py` (new file), define the relative-date grammar:
      English and Russian phrases, with both word-form and digit-form numbers.
- [ ] Add `parse_relative(text, *, reference=None)` instance method on
      `DateParser`.
- [ ] Add `relative=True` constructor flag; when set, `parse()` also tries
      the relative grammar after the absolute grammar returns `None`.
- [ ] Default behaviour unchanged: `parse()` without `relative=True` does
      NOT match relative phrases.

## Tests

- [ ] `tests/test_relative_parsing.py`:
      - `test_parse_relative_today` — `parse_relative("today")` ≈ now.
      - `test_parse_relative_yesterday` — `parse_relative("yesterday")` ≈
        now − 1 day.
      - `test_parse_relative_tomorrow`.
      - `test_parse_relative_n_days_ago` — `parse_relative("3 days ago")` ≈
        now − 3 days.
      - `test_parse_relative_n_days_from_now` — `parse_relative("in 5 days")`
        ≈ now + 5 days.
      - `test_parse_relative_russian_today` — `parse_relative("сегодня")` ≈
        now.
      - `test_parse_relative_russian_n_days_ago` — `parse_relative("3 дня
        назад")` ≈ now − 3 days.
      - `test_parse_relative_with_pinned_reference` — `parse_relative("yesterday",
        reference=datetime(2020, 1, 2))` returns `datetime(2020, 1, 1)`.
      - `test_parse_does_not_match_relative_by_default` — `parse("today")`
        returns `None`.
      - `test_parse_matches_relative_when_relative_true` —
        `DateParser(relative=True).parse("yesterday")` ≈ now − 1 day.

## Documentation

- [ ] Add a "Relative dates" subsection to `docs/docs/api/dateparser.md`.

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `python -m mypy qddate/__init__.py qddate/qdparser.py` clean.
- [ ] `ruff check qddate tests scripts` clean.
- [ ] Default behaviour preserved: `parser.parse("today")` still returns `None`.