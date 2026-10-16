# OpenSpec Change: Add relative date parsing

`qddate` excels at absolute dates (`"6 Jan 2009"`, `"28. Juli 2015"`) but
treats relative phrases (`"today"`, `"yesterday"`, `"3 days ago"`) as
non-matches. This change adds opt-in support for the most common English and
Russian relative-date phrases via a new `parse_relative()` method and a
`relative=True` constructor flag.

## Why

The README has "Limitations" called out and explicitly mentions that
`qdate`-class libraries handle "today/yesterday/N days ago" while `qddate`
does not. The gap is real and small to close for the most common cases
(English + Russian), which covers the bulk of scraped content the library
sees in practice.

The proposal deliberately limits scope: only English and Russian for v1; only
"today"/"yesterday"/"tomorrow"/"N days ago"/"N days from now"/"N weeks ago"/"N
weeks from now"/"N months ago"/"N months from now"; no business-day
arithmetic, no holidays, no timezone arithmetic.

## What changes

**`parse_relative(text, *, reference=None)`**
- New `DateParser` instance method that returns a `datetime.datetime` (or
  `None`) by combining absolute parsing (via `parse()`) and relative-date
  phrase parsing.
- `reference` defaults to `datetime.datetime.now()`; callers can pin the
  reference for deterministic tests or for scraping historic content where
  "today" should mean the article's publish date.

**Relative phrase grammar**
- English: `today`, `yesterday`, `tomorrow`, `N days ago`, `N days from now`,
  `N weeks ago`, `N weeks from now`, `N months ago`, `N months from now`,
  `N years ago`, `N years from now`.
- Russian: `сегодня`, `вчера`, `завтра`, `N дней назад`, `N дней назад`,
  `N недель назад`, `N месяцев назад`, `N лет назад`, `через N дней`,
  `через N недель`, `через N месяцев`, `через N лет`.
- Numbers: both word ("forty-two") and digit ("42").

**`relative=True` constructor flag (opt-in)**
- From: `parse("today")` returns `None`.
- To: `DateParser(relative=True).parse("today")` returns today's date when
  called; `parse("yesterday")` returns yesterday's.
- Reason: Keeps the default behaviour unchanged; relative parsing is opt-in
  for callers who need it.
- Impact: Non-breaking.

**`parse_relative(text, *, reference=None)` always works**
- Independent of `relative=True`: explicit calls always try the relative
  grammar.

## Out of scope

- Other languages (German, French, etc.) — can be added one-by-one.
- Business-day arithmetic, holidays, fiscal quarters.
- Timezone-aware relative math (handled by `tz_aware` for absolute dates).
- "Last week" / "next month" (fuzzy phrases; would need calendar logic).

## Impact

- **Breaking?** No. The default behaviour is unchanged; relative support is
  opt-in via `relative=True` or explicit `parse_relative()` calls.
- **Affected:** Anyone who scrapes content that uses relative dates.
- **Risk:** "today" matches against a non-date input that happens to
  contain the word. Mitigation: relative grammar only fires on
  whitespace-separated word matches, and `parse_relative` is an explicit
  opt-in method.
- **Rollback:** Drop the new method.