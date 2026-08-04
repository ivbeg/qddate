# Tasks: Add datetime semantics

## Timezone

- [ ] Extend `pat:time:full` result capture to retain the parsed offset as a result
      field (currently suppressed).
- [ ] Add `tz=` / `default_tz=` parameter to `parse()` (and `match()` where relevant).
- [ ] When an offset is present and tz handling is enabled, return a tz-aware
      `datetime` (`datetime.timezone(...)`).
- [ ] When no offset is present, return a naive datetime (status quo) unless
      `default_tz` is given.
- [ ] Tests: `+0530` offset round-trips; offset of `+0000` yields UTC-aware; naive
      path unchanged when parameter omitted.

## 2-digit-year pivot

- [ ] Add `pivot_year` constructor parameter to `DateParser` (default `None` =
      legacy passthrough for 1.x).
- [ ] When set, post-process any `yearshort`-pattern result: `yy < break → 20yy`,
      else `19yy`.
- [ ] Default the break at `68` when `pivot_year` is enabled (configurable).
- [ ] Tests: `05/16/99 → 1999`, `05/16/20 → 2020`, boundary at the configured break,
      and legacy behavior (no pivot) returns the raw 2-digit year.

## Docs

- [ ] Document both parameters in the docstrings and README usage section.
- [ ] Note the 2.0 intent to flip the pivot default in CHANGELOG.

## Verification

- [ ] `pytest -q` green; new tz/pivot tests pass.
- [ ] Existing tests (no new params) unchanged → confirms opt-in is non-breaking.
