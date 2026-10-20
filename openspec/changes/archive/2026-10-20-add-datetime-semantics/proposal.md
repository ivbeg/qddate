# OpenSpec Change: Add datetime semantics (timezone + 2-digit-year pivot)

Two related capability additions to `date-parsing`: timezone-aware results and a sane
2-digit-year interpretation. From `IMPROVEMENT_PLAN.md` §7.1, §7.2, §3.4.

## Why

- **Timezone.** `pat:time:full` already parses a `+HHMM` numeric offset but silently
  discards it. Scraped news timestamps routinely carry offsets; losing them (or
  returning a naive datetime that looks local) is a real correctness issue for
  downstream aggregation.
- **2-digit years.** `parse("05/16/99")` currently returns `datetime.datetime(99, 5,
  16)` — year 99 AD. For a scraping tool this is almost never intended. Python's `%y`
  does no pivot; qddate inherits that gap.

## What changes

**Timezone-aware parsing (opt-in)**
- From: A parsed `+HHMM` offset is discarded; `parse()` always returns a naive
  `datetime`.
- To: `parse()` accepts an optional `tz=` / `assume_tz=` behavior. When an offset is
  present in the input and tz handling is enabled, the returned `datetime` SHALL be
  timezone-aware, carrying the parsed offset. When no offset is present, behavior is
  unchanged (naive datetime) unless an explicit `default_tz` is supplied.
- Reason: Preserve scraped timestamp fidelity.
- Impact: **Potentially breaking** if naively defaulted. Therefore opt-in: the default
  remains naive datetimes so existing callers see no change. A future major release
  may flip the default.

**2-digit-year pivot**
- From: 2-digit years pass through `datetime`'s `%y` behavior, yielding e.g. year 99.
- To: A configurable `pivot_year` (default `1968`, i.e. break at 68) interprets
  2-digit years: `00–67 → 20xx`, `68–99 → 19xx`. So `05/16/99 → 1999`,
  `05/16/20 → 2020`.
- Reason: Year-99 AD results are never useful for scraping.
- Impact: **Behavior change**, but to the *correct* value. To stay non-breaking in
  1.x, the pivot is opt-in via a constructor parameter (`pivot_year=`); the eventual
  2.0 default flips to the pivot. Documented in the changelog.

## Impact

- **Breaking?** No by default in 1.x — both features are opt-in. The 2.0 roadmap
  commits to making the pivot the default.
- **Affected:** Callers who want correct offsets/years opt in; everyone else unchanged.
- **Rollback:** Feature-flagged; remove the parameters.
