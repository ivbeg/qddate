# Tasks: Add datetime semantics

> Archived 2026-10-20 after verification against the code. Shipped in 1.0.11 with a different API than proposed: `DateParser(tz_aware=True)` and `DateParser(pivot_year=1968)`. Unshipped items are left unchecked below.


## Timezone

- [x] Extend `pat:time:full` result capture to retain the parsed offset as a result
      field (currently suppressed).
- [ ] Add `tz=` / `default_tz=` parameter to `parse()` (and `match()` where relevant).
  - Not done as written: shipped as the constructor flag `DateParser(tz_aware=True)`; there is no per-call `tz=` and no `default_tz`.
- [x] When an offset is present and tz handling is enabled, return a tz-aware
      `datetime` (`datetime.timezone(...)`).
- [ ] When no offset is present, return a naive datetime (status quo) unless
      `default_tz` is given.
  - Partly: naive datetimes are returned; `default_tz` does not exist.
- [x] Tests: `+0530` offset round-trips; offset of `+0000` yields UTC-aware; naive
      path unchanged when parameter omitted.

## 2-digit-year pivot

- [x] Add `pivot_year` constructor parameter to `DateParser` (default `None` =
      legacy passthrough for 1.x).
- [x] When set, post-process any `yearshort`-pattern result: `yy < break → 20yy`,
      else `19yy`.
- [ ] Default the break at `68` when `pivot_year` is enabled (configurable).
  - Not done: `pivot_year` is an explicit 4-digit year (e.g. `1968`); there is no default break.
- [x] Tests: `05/16/99 → 1999`, `05/16/20 → 2020`, boundary at the configured break,
      and legacy behavior (no pivot) returns the raw 2-digit year.

## Docs

- [ ] Document both parameters in the docstrings and README usage section.
  - Partly: documented in docstrings and `docs/docs/api/dateparser.md`, not in the README.
- [ ] Note the 2.0 intent to flip the pivot default in CHANGELOG.
  - Not done: no decision to flip the default was recorded.

## Verification

- [x] `pytest -q` green; new tz/pivot tests pass.
- [x] Existing tests (no new params) unchanged → confirms opt-in is non-breaking.
