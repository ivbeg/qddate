# Specification: Date Parsing

The core date-parsing capability of qddate: turning a string extracted from scraped
HTML into a `datetime.datetime`, including left-aligned matching with trailing text
and date-component validation.

## Purpose

Define the externally observable behavior of `qddate.DateParser.parse()` and
`.match()` so that refactors and new features preserve (or intentionally change) the
contract.

---
## Requirements
### Requirement: Parse date into datetime

The parser SHALL accept any human-readable string and return a
`datetime.datetime` representing the parsed date when a supported date pattern matches
at the start of the string, otherwise return `None`.

#### Scenario: Supported numeric date
- **WHEN** `parse("01.12.2009")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 12, 1)`

#### Scenario: Unsupported string returns None
- **WHEN** `parse("totally invalid date")` is called
- **THEN** the result SHALL be `None`

#### Scenario: Empty or whitespace input
- **WHEN** `parse("")`, `parse("   ")`, or `parse("1")` is called
- **THEN** the result SHALL be `None` without raising

---

### Requirement: Left-aligned matching with trailing text

The parser SHALL match dates that appear at the start of the input and SHALL ignore
any trailing text after the matched date, so that scraped strings like
`12.03.1999 Hello people` parse successfully.

#### Scenario: Date followed by prose
- **WHEN** `parse("12.03.1999 Hello people")` is called
- **THEN** the result SHALL equal `datetime.datetime(1999, 3, 12)`

#### Scenario: Date followed by time label
- **WHEN** `parse("23 Jul 2015, 09:00 BST")` is called
- **THEN** the result SHALL equal `datetime.datetime(2015, 7, 23, 9, 0)`

---

### Requirement: Optional time-of-day suffix

The parser SHALL accept an optional time-of-day suffix in `HH:MM`, `HH:MM:SS`
or `HHhMM` (`14h30`, `14 h 30`) form after a date, separated from it by a space,
`,`, `|` or the ISO `T`, and SHALL populate the hour, minute, and (when
present) second fields of the returned `datetime`. The `HHhMM` form SHALL
require the minutes.

The suffix MAY be preceded by the word the date's language writes before a
time: `в` (ru), `at` (en), `à` (fr), `um` (de), `a las` (es), `alle` (it),
`om` (nl), `às` (pt). A word SHALL NOT be accepted after a month-name date of
another language. A language-neutral numeric date SHALL accept the word of
every language.

#### Scenario: Date with minutes
- **WHEN** `parse("16 May 2009 14:10")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 5, 16, 14, 10)`

#### Scenario: Date with full time
- **WHEN** `parse("01.03.2009 14:53:12")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 3, 1, 14, 53, 12)`

#### Scenario: Bracketed time
- **WHEN** `parse("9 Июля 2015 [11:23]")` is called
- **THEN** the result SHALL equal `datetime.datetime(2015, 7, 9, 11, 23)`

#### Scenario: Russian time after "в"
- **WHEN** `parse("4 Сентября 2020 в 04:06:33")` is called
- **THEN** the result SHALL equal `datetime.datetime(2020, 9, 4, 4, 6, 33)`

#### Scenario: Word of another language
- **WHEN** `parse("16 May 2009 в 14:10")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 5, 16)`

#### Scenario: Numeric date accepts every language's word
- **WHEN** `parse("05.05.2022 в 12:30")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 12, 30)`

#### Scenario: French time with "h"
- **WHEN** `parse("le 5 mai 2022 à 14h30")` or `parse("05/05/2022 14h30")` is
  called
- **THEN** the result SHALL have hour `14` and minute `30`

#### Scenario: Pipe before minutes
- **WHEN** `parse("21 September 1994 | 11:08")` is called
- **THEN** the result SHALL equal `datetime.datetime(1994, 9, 21, 11, 8)`

---

### Requirement: English abbreviations and dashed dates

The parser SHALL read an abbreviated English month followed by a dot
(`Sept. 5, 2022`, `Dec. 25, 2022`), an abbreviated month before an ordinal
day (`Sep 5th 2022`), an ordinal day before `Sept` or an abbreviated month
with a dot (`5th Sept 2022`, `5th Dec. 2022`), and day, month and four-digit
year between dashes (`5-May-2022`, `05-Sep-2022`). `Sept` SHALL be read as
September. Forms that parsed before SHALL keep their pattern.

#### Scenario: AP-style abbreviation
- **WHEN** `parse("Sept. 5, 2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 9, 5)`

#### Scenario: Ordinal day after an abbreviation
- **WHEN** `parse("Sep 5th 2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 9, 5)`

#### Scenario: Dashes and a four-digit year
- **WHEN** `parse("5-May-2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5)`

---

### Requirement: Chinese, Japanese and Korean numeric dates

The parser SHALL read a year, month and day written as numbers followed by
their units: `年`, `月`, `日` or `号` (Chinese, Japanese) and `년`, `월`, `일`
(Korean), with ASCII or full-width digits. A weekday may follow the day, in
brackets or written out (`(木)`, `（木曜日）`, `星期四`, `(목)`, `목요일`), then
a time written with units (`14時30分`, `14时30分`, `14시 30분`) or after a
morning or afternoon marker (`午前`, `午後`, `上午`, `下午`, `오전`, `오후`); an
hour above 12 after a marker SHALL NOT be read as a time. A month and day
without a year (`5月5日`, `5월 5일`) SHALL be a `noyear` pattern. The patterns
SHALL belong to no language.

#### Scenario: Chinese or Japanese date
- **WHEN** `parse("2022年5月5日")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5)`

#### Scenario: Korean date
- **WHEN** `parse("2022년 5월 5일")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5)`

#### Scenario: Time after the date
- **WHEN** `parse("2022年5月5日 14:30")` or `parse("2022年5月5日午後2時30分")`
  is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 14, 30)`

---

### Requirement: Twelve-hour clock

The parser SHALL accept a 12-hour time after a date: an hour of one or two
digits, optional minutes and seconds, and a marker `AM`, `PM`, `am`, `pm`,
`a.m.`, `p.m.`, `A.M.` or `P.M.`, optionally preceded by the date language's
word before a time. `12 AM` SHALL be hour 0 and `12 PM` hour 12. An hour
above 12 SHALL NOT be read as a 12-hour time, and `AM`/`PM` followed by a
letter SHALL NOT be a marker. `match()` SHALL report the hour as a 24-hour
number and SHALL NOT add a marker value.

#### Scenario: Afternoon time with "at"
- **WHEN** `parse("May 5, 2022 at 3:45 PM")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 15, 45)`

#### Scenario: Midnight
- **WHEN** `parse("May 5, 2022 12:00 AM")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 0, 0)`

#### Scenario: Hour only
- **WHEN** `parse("May 5, 2022 at 3 p.m.")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 15, 0)`

#### Scenario: Values stay numeric
- **WHEN** `match("May 5, 2022 at 3:45 PM")` is called
- **THEN** its `values` SHALL contain `hour` `"15"` and no `ampm` key

---

### Requirement: Time before the date

The parser SHALL accept a time of day before a date, in any form of the
time-of-day and twelve-hour requirements and with an optional zone, followed
by `,`, `|`, `-` or a space.

#### Scenario: Russian date after the time
- **WHEN** `parse("12:30, 5 мая 2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 12, 30)`

#### Scenario: Numeric date after the time
- **WHEN** `parse("12:30 05.05.2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 12, 30)`

#### Scenario: Pipe separator
- **WHEN** `parse("14:30 | 5 May 2022")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 5, 14, 30)`

#### Scenario: A time alone is not a date
- **WHEN** `match("12:30 -15 комментариев")` is called
- **THEN** the result SHALL be `None`

---

### Requirement: Longest match wins

Patterns are not anchored at the end of the input, so several candidates can
match different lengths of it. `match()` SHALL return the candidate that
consumes the most input, not counting trailing whitespace; the internal
priority SHALL only break ties between candidates of equal length, and equal
priorities SHALL be broken by pattern generation order, so the result does not
depend on which filter produced the candidates. A trailing-text (`:t_right`)
variant SHALL NOT count the text after the date as consumed.

#### Scenario: Time is not dropped for a shorter date-only match
- **WHEN** `parse("14 Avril 1995 20:16:12")` is called
- **THEN** the result SHALL equal `datetime.datetime(1995, 4, 14, 20, 16, 12)`

#### Scenario: Seconds are not dropped for an HH:MM match
- **WHEN** `parse("22 August 2005 08:47:19")` is called
- **THEN** the result SHALL equal `datetime.datetime(2005, 8, 22, 8, 47, 19)`

#### Scenario: Clean date matches the plain variant
- **WHEN** `match("25 Jan 1936")` is called
- **THEN** the pattern key SHALL be `dt:date:date_eng1_short`, not its
  `:t_right` variant

---

### Requirement: Date component validation

The parser SHALL reject any match whose month is outside `1..12`, whose day is
outside `1..31`, whose hour is above `23`, or whose minute or second is above `59`
by treating it as no match (returning `None` for `parse`, skipping the pattern for
`match`).

#### Scenario: Invalid month rejected
- **GIVEN** a pattern that captures month `13`
- **WHEN** the candidate is evaluated
- **THEN** the candidate SHALL be skipped and the next pattern tried

#### Scenario: Invalid day rejected
- **GIVEN** a pattern that captures day `0` or `32`
- **WHEN** the candidate is evaluated
- **THEN** the candidate SHALL be skipped

#### Scenario: Invalid time of day rejected
- **WHEN** `parse("01.12.2009 25:00")` is called
- **THEN** the time-suffixed candidate SHALL be skipped
- **AND** the result SHALL equal `datetime.datetime(2009, 12, 1)` from the
  date-only pattern

---

### Requirement: Match returns structured result

The `match()` method SHALL return a dict with two keys — `"values"` (the parsed
components, convertible via `int()`) and `"pattern"` (the matched pattern's metadata
dict, which includes `"key"`) — when a pattern matches, and `None` otherwise.

#### Scenario: Match returns values and pattern
- **WHEN** `match("01.12.2009")` is called
- **THEN** the result SHALL contain key `"values"` whose items are `int()`-able
- **AND** the result SHALL contain key `"pattern"` with a `"key"` field

---

### Requirement: Graceful handling of invalid date construction

When the parsed components would form an invalid calendar date (e.g. day 0 or a
resulting `datetime` that raises `ValueError`), `parse()` SHALL return `None` rather
than raise.

#### Scenario: Components that do not form a valid date
- **GIVEN** parsed components that cause `datetime.datetime(**d)` to raise `ValueError`
- **WHEN** `parse()` builds the result
- **THEN** `parse()` SHALL return `None`

---

### Requirement: No-year pattern support

A pattern marked with the `noyear` flag SHALL substitute the current year for the
missing year component when `parse()` or `match()` is invoked with
`allow_no_year=True` (the default). `parse()` and `match_typed()` SHALL take
the year from `reference=` when given. With `prefer="past"` a date more than
`NOYEAR_ROLLOVER_GRACE` (two days) after the reference (default: now) SHALL
move to the previous year; with `prefer="future"` a date more than that
before it SHALL move to the next year; a day that does not exist in that year
SHALL give `None`. Other `prefer` values SHALL raise `ValueError`. With `allow_no_year=False`, `noyear` patterns
SHALL NOT match. Only a pattern marked `noyear` SHALL match a date without a year.

English dates without a year SHALL be read month first and day first, with a
full or abbreviated month name (`Sept` included, an optional dot after it)
and an optional ordinal suffix: `May 5`, `Sept. 5`, `Dec 25th`, `5 May`,
`25th December`. The month name SHALL be capitalised or in capitals, SHALL NOT
be followed by a letter, and the day SHALL NOT be followed by a digit or by a
two- or four-digit number that is not a time.
The keyword is specified in `packaging-and-api` ("Public parsing methods accept
`allow_no_year=`"), which also keeps `noyear=` as a deprecated alias.

#### Scenario: Day-month string with current year
- **GIVEN** the system clock is set to year `2026`
- **WHEN** `match("01.12", allow_no_year=True)` is called on a `noyear` pattern
- **THEN** the resulting year SHALL be `2026`

#### Scenario: Russian day and month with current year
- **GIVEN** the system clock is set to year `2026`
- **WHEN** `parse("4 Сентября в 04:06:33")` is called
- **THEN** the result SHALL equal `datetime.datetime(2026, 9, 4, 4, 6, 33)`

#### Scenario: Year from the reference
- **WHEN** `parse("05.12", reference=datetime.datetime(2020, 3, 1))` is called
- **THEN** the result SHALL equal `datetime.datetime(2020, 12, 5)`

#### Scenario: Last December read in January
- **WHEN** `parse("31.12", reference=datetime.datetime(2026, 1, 2), prefer="past")`
  is called
- **THEN** the result SHALL equal `datetime.datetime(2025, 12, 31)`

#### Scenario: English month and day
- **WHEN** `parse("May 5", reference=datetime.datetime(2026, 10, 22))` or
  `parse("5th May", reference=datetime.datetime(2026, 10, 22))` is called
- **THEN** the result SHALL equal `datetime.datetime(2026, 5, 5)`

#### Scenario: English words that are not dates
- **WHEN** `parse("may 5")`, `parse("5 Marketing tips")`, `parse("May 2022")`
  or `parse("May 5, 22")` is called
- **THEN** the result SHALL be `None`

#### Scenario: No-year patterns disabled
- **WHEN** `parse("4 Сентября в 04:06:33", allow_no_year=False)`,
  `parse("May 5", allow_no_year=False)` or
  `parse("05.12", allow_no_year=False)` is called
- **THEN** the result SHALL be `None`

---

### Requirement: Consistent repeated parsing

Calling `parse()` with the same input SHALL return equal results across repeated
invocations on the same parser instance.

#### Scenario: Repeated calls are consistent
- **WHEN** `parse("01.12.2009")` is called three times
- **THEN** all three results SHALL be equal

### Requirement: Relative date parsing for English and Russian

`DateParser` SHALL expose `parse_relative(text, reference=None)` that
resolves common English and Russian relative-date phrases ("today",
"yesterday", "tomorrow", "N days/weeks/months/years ago", "in N ...") against a
reference time (default: `datetime.now()`). The calendar date is shifted by the
phrase's offset; the time of day SHALL be the reference's time of day.

Relative parsing is a separate entry point: `parse()` and `match()` SHALL NOT
match relative phrases, and the constructor has no switch that adds them.

#### Scenario: parse_relative resolves "today"
- **GIVEN** `reference = datetime(2026, 6, 15, 12, 0)`
- **WHEN** `parser.parse_relative("today", reference)` is called
- **THEN** the result SHALL equal `datetime(2026, 6, 15, 12, 0)`

#### Scenario: parse_relative without a reference uses the current time
- **WHEN** `parser.parse_relative("today")` is called with no reference
- **THEN** the returned `datetime` SHALL have today's calendar date and the
  current time of day
- **AND** the call SHALL NOT raise

#### Scenario: parse_relative resolves "yesterday"
- **GIVEN** `reference = datetime(2026, 6, 15, 12, 0)`
- **WHEN** `parser.parse_relative("yesterday", reference)` is called
- **THEN** the result SHALL equal `datetime(2026, 6, 14, 12, 0)`

#### Scenario: parse_relative resolves N-days-ago
- **GIVEN** `reference = datetime(2026, 6, 15, 12, 0)`
- **WHEN** `parser.parse_relative("3 days ago", reference)` is called
- **THEN** the result SHALL equal `datetime(2026, 6, 12, 12, 0)`

#### Scenario: parse_relative resolves Russian phrases
- **GIVEN** `reference = datetime(2026, 6, 15, 12, 0)`
- **WHEN** `parser.parse_relative("сегодня", reference)` is called
- **THEN** the result SHALL equal `datetime(2026, 6, 15, 12, 0)`
- **WHEN** `parser.parse_relative("3 дня назад", reference)` is called
- **THEN** the result SHALL equal `datetime(2026, 6, 12, 12, 0)`

#### Scenario: Unsupported phrase
- **WHEN** `parser.parse_relative("not a date")` is called
- **THEN** the result SHALL be `None`

#### Scenario: parse() does not match relative phrases
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("today")` is called
- **THEN** the result SHALL be `None`

### Requirement: Filter pipeline is documented

The public documentation SHALL include a description of the six-level
filter pipeline used by `DateParser.match()` and friends, and SHALL link to
it from `match.md` and `parse.md`.

#### Scenario: docs/docs/api/filter-pipeline.md exists
- **WHEN** the docs site is built
- **THEN** the page `docs/docs/api/filter-pipeline.md` SHALL be present
- **AND** it SHALL be reachable from the API reference sidebar

#### Scenario: Page lists the six filter levels
- **WHEN** the page is rendered
- **THEN** it SHALL describe each of the six filters (length, separator,
  year format, language, character set, prefix bucket)
- **AND** it SHALL describe the keyword arguments (`noprefix`,
  `nocharsetfilter`, `noseparatorfilter`, `noyearformatfilter`,
  `nolanguagefilter`) that disable them
- **AND** it SHALL be honest about the cost (slower parses when filters
  are disabled)

### Requirement: Reachability oracle test

The test suite SHALL include a reachability oracle that asserts every base
pattern in `ALL_PATTERNS` is the *winning* match for at least one fixture
string, with one fixture dedicated to exercising each base pattern.

#### Scenario: Every base pattern wins a probe
- **GIVEN** the canonical pattern table `qddate.patterns.ALL_PATTERNS`
- **WHEN** the reachability oracle runs over a curated probe corpus
- **THEN** every basekey in `ALL_PATTERNS` SHALL appear as the winning match
  for at least one probe string
- **AND** every probe string SHALL produce a non-None parse result

#### Scenario: New pattern breaks the oracle loudly
- **GIVEN** a new pattern is added to `ALL_PATTERNS` without a matching probe
- **WHEN** the reachability oracle runs
- **THEN** the test SHALL fail with a message naming the new pattern key
- **AND** the fix SHALL be to add a probe, not to weaken the oracle

### Requirement: Pattern fingerprint index

Each pattern SHALL carry a precomputed fingerprint derived from
`len(qax)`, `separator`, `language`, `chars`, `year_format`, and length
range. The set of all fingerprints SHALL be exposed as
`qddate.patterns._PATTERN_FINGERPRINTS`, mapping each unique fingerprint
tuple to the frozenset of pattern keys that share it.

#### Scenario: Fingerprint is deterministic
- **WHEN** `compute_pattern_fingerprint(p)` is called twice on the same
  pattern dict
- **THEN** the result SHALL be `==` to itself (hashable, equality-stable)

#### Scenario: Every pattern is in the index
- **WHEN** the fingerprint index is built at import time
- **THEN** every key in `ALL_PATTERNS` SHALL appear in exactly one bucket
  of `_PATTERN_FINGERPRINTS`

### Requirement: Legacy buckets are projections of the index

The per-instance buckets `_patterns_by_length`, `_patterns_by_separator`,
`_patterns_by_language`, and `_patterns_by_year_format` SHALL be
derivable from `_PATTERN_FINGERPRINTS` by a single dimension-projection
loop. The index SHALL NOT carry any pattern that is missing from the
legacy buckets.

#### Scenario: Length bucket projection
- **GIVEN** the set of pattern keys whose pattern has
  `length_min ≤ len(text) ≤ length_max`
- **THEN** that set SHALL equal the union of `_PATTERN_FINGERPRINTS` entries
  whose `length_min ≤ len(text) ≤ length_max`

### Requirement: Intersection candidate set

`intersect_fingerprints(text_fingerprint, allowed_chars)` SHALL return the
union of `_PATTERN_FINGERPRINTS` entries whose key is satisfied by the
text's fingerprint (length match, chars match with `ACCENTED → LATIN`
substitution, separator subset, language subset, year-format subset).
The returned set SHALL be a superset-or-equal of the candidate set
returned by the existing 6-level filter pipeline for the same input.

#### Scenario: Accented-vs-Latin substitution preserved
- **GIVEN** a pattern whose required chars include `CHAR_SET_ACCENTED`
- **WHEN** the text contains only `CHAR_SET_LATIN`
- **THEN** `intersect_fingerprints` SHALL still include this pattern in
  the result

### Requirement: Fingerprint-based candidate selection is the default

`DateParser.__init__` SHALL accept a `use_fingerprint: bool = True`
parameter (default since ``1.0.14``). When the caller explicitly passes
``False``, the constructor SHALL emit a ``DeprecationWarning`` noting
that the legacy 6-level filter will be removed in ``v2.0.0``. Passing
``True`` (or omitting the argument) SHALL be silent.

#### Scenario: Default behaviour uses fingerprint
- **WHEN** ``DateParser()`` is constructed with no arguments
- **THEN** ``use_fingerprint`` SHALL be ``True``
- **AND** the fingerprint-based filter SHALL run
- **AND** no ``DeprecationWarning`` SHALL be emitted

#### Scenario: Feature flag explicitly disabled
- **GIVEN** a ``DateParser(use_fingerprint=False)``
- **WHEN** ``match()`` / ``match_all()`` / ``parse()`` is called
- **THEN** the legacy 6-level filter SHALL produce the candidate set

#### Scenario: Explicit opt-in emits a warning
- **GIVEN** ``warnings.simplefilter("always")`` is in effect
- **WHEN** ``DateParser(use_fingerprint=False)`` is constructed
- **THEN** a ``DeprecationWarning`` SHALL be emitted with a message that
  mentions ``v2.0.0`` as the removal milestone

### Requirement: Fingerprint filter keeps every legacy candidate

For every input string the fingerprint-based filter SHALL return a
candidate pattern set that is a superset-or-equal of the candidate set the
legacy 6-level filter returns for the same input, and `match()`,
`match_all()` and `parse()` SHALL return the same results on both paths.
Both properties MUST hold under any combination of filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``,
``noseparatorfilter``, ``noyearformatfilter``, ``nolanguagefilter``) and
during a session started with `start_session()`.

#### Scenario: Same results on the extended probe corpus
- **GIVEN** any string from the extended probe corpus (the union of the
  reachability probes and the regression corpus, covering every shipped
  language, every separator, every year-format bucket, weekday + short +
  compact + edge cases)
- **WHEN** the same string is fed to both paths
- **THEN** the fingerprint candidate set SHALL contain every legacy candidate
- **AND** `match_all()` SHALL return the same pattern keys on both paths

### Requirement: Toggles preservation across filter toggles

The fingerprint-based filter SHALL honour the existing filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``, ``noseparatorfilter``,
``noyearformatfilter``, ``nolanguagefilter``): disabling a filter SHALL skip
its dimension, so the candidate set can only widen, as on the legacy path.

#### Scenario: Disabling the character-set filter widens the candidate set
- **GIVEN** two parsers (``use_fingerprint=True`` and ``use_fingerprint=False``)
- **WHEN** `parse("01.12.2009", nocharsetfilter=True)` is called on both
- **THEN** both results SHALL equal `datetime.datetime(2009, 12, 1)`

#### Scenario: Disabling the separator filter widens the candidate set
- **WHEN** `DateParser().parse("01.12.2009", noseparatorfilter=True)` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 12, 1)`

### Requirement: Sessions restrict candidate patterns

`start_session(keys)` SHALL restrict matching to the given pattern keys until
`end_session()` is called, on both the fingerprint and the legacy path.
`start_session` / `end_session` are the canonical names; the camelCase
`startSession` / `endSession` SHALL keep working and emit
`DeprecationWarning` until `2.0`.

#### Scenario: Session excludes other patterns
- **GIVEN** `parser.start_session(["dt:date:date_eng1"])`
- **WHEN** `parser.parse("01.12.2009")` is called
- **THEN** the result SHALL be `None`
- **AND** `parser.parse("5 August 2001")` SHALL equal `datetime.datetime(2001, 8, 5)`

#### Scenario: Ending the session restores all patterns
- **WHEN** `parser.end_session()` is called after the session above
- **THEN** `parser.parse("01.12.2009")` SHALL equal `datetime.datetime(2009, 12, 1)`

#### Scenario: camelCase aliases still work
- **WHEN** `startSession(...)` / `endSession()` are called
- **THEN** they SHALL behave like `start_session` / `end_session`
- **AND** each call SHALL emit `DeprecationWarning`

### Requirement: Typed match result

`match_typed()` SHALL return a `DateMatch` exposing the constructed
`datetime`, the matched pattern's key (`pattern_key`), its language
(`language`, `None` for language-neutral patterns), its `format` string, the
raw input (`raw`), the `span` `(0, end)` of the date in `raw` (in characters of
the original text, without the `,`, `|`, `:` or `)` read after the date), its `precision` (`"day"` without a time, `"hour"` for a
12-hour time without minutes, `"minute"`, `"second"`), the written zone
(`tzinfo`, whether or not the parser is `tz_aware`, `None` without a zone) and
`has_year` (`False` for a `noyear` pattern), or `None` when nothing matches.
`DateMatch.to_dict()` SHALL return a plain dict of those fields. The new fields
SHALL have defaults, so `DateMatch` built with the first five fields keeps
working. The dict returned by `match()` SHALL remain unchanged.

#### Scenario: Typed result for a supported date
- **WHEN** `match_typed("01.12.2009")` is called
- **THEN** the result SHALL expose `.datetime == datetime.datetime(2009, 12, 1)`
- **AND** `.pattern_key == "dt:date:date_2"`, `.format == "%d.%m.%Y"`,
  `.raw == "01.12.2009"`

#### Scenario: Legacy dict shape preserved
- **WHEN** `match("01.12.2009")` is called
- **THEN** the result SHALL remain a dict with `"values"` and `"pattern"` keys

#### Scenario: Span, precision and zone
- **WHEN** `match_typed("5 мая 2022 в 12:30 МСК Новости")` is called on
  `DateParser()`
- **THEN** `.span` SHALL be `(0, 22)`, `.precision` SHALL be `"minute"`,
  `.tzinfo` SHALL have the offset `+03:00`, `.has_year` SHALL be `True`
- **AND** `.datetime` SHALL be naive

---

### Requirement: Search for dates inside text

`search(text)` SHALL return the `DateMatch` of the first date in `text`
wherever it starts, or `None`; `find_all(text)` SHALL return every date, left
to right, without overlaps. `span` SHALL give the date's start and end in
`text`. A date SHALL be tried at position 0 and at the start of every run of
one, two, four or eight digits that starts a word (not after a letter other
than a Chinese, Japanese or Korean one, not inside a number) and of every
month or weekday name; at each position the result SHALL be what
`match_typed()` finds there. With `max_offset=N` a date SHALL start at or
before index `N`. With `labels=True` a date that does not start the text (or
follow the previous date) SHALL follow a label of `DATE_LABELS` (compared
case-insensitively with the text after the last separator, punctuation after
it removed), a dateline (up to four words without digits and a comma or a
spaced dash) or punctuation alone; with a string or a list of strings, those
labels SHALL replace the built-in ones. `reference=`, `prefer=` and the keyword
arguments of `match()` SHALL apply.

#### Scenario: Date after a label
- **WHEN** `search("Posted on May 5, 2022")` is called
- **THEN** `.datetime` SHALL equal `datetime.datetime(2022, 5, 5)` and `.span`
  SHALL be `(10, 21)`

#### Scenario: Labels required
- **WHEN** `search("Some text 5 May 2022", labels=True)` is called
- **THEN** the result SHALL be `None`
- **AND** `search("Опубликовано: 5 мая 2022", labels=True)` and
  `search("GENEVA, 29 July 2022", labels=True)` SHALL find the date

#### Scenario: Every date
- **WHEN** `find_all("From 5 May 2022 to 7 May 2022")` is called
- **THEN** it SHALL return two matches with spans `(5, 15)` and `(19, 29)`

#### Scenario: Not a date start
- **WHEN** `search("Tel. +7 495 123-45-67", labels=True)` is called
- **THEN** the result SHALL be `None` without running a grammar

---

### Requirement: Ambiguous numeric date order

`DateParser(date_order=...)` and the `date_order=` keyword of `match()`,
`match_all()`, `parse()` and `match_typed()` SHALL accept `"DMY"`, `"MDY"`,
`"YMD"` (any case) or `None`, and SHALL raise `ValueError` otherwise. Among
candidates that consume the same text, the numeric patterns of that order
(day first: `date_1`, `date_2`, `date_4`, `date_4_point`, `date_5`, `date_8`,
`date_iso8601(_short)`, `weekday_(short_)eng_iso`; month first: `date_usa`,
`date_usa_1`; year first: `date_3`, `date_6`, `date_9`, `date_10`) SHALL win;
a longer match SHALL still win over a shorter one. `None` per call SHALL use
the constructor's value; `None` there SHALL keep the built-in preference.

#### Scenario: Month first
- **WHEN** `parse("05/06/2022", date_order="MDY")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 6)`

#### Scenario: Unambiguous date ignores the order
- **WHEN** `parse("13/05/2022", date_order="MDY")` is called
- **THEN** the result SHALL equal `datetime.datetime(2022, 5, 13)`

#### Scenario: Constructor default
- **GIVEN** `DateParser(date_order="MDY")`
- **WHEN** `match("05/06/2022")` is called
- **THEN** the pattern key SHALL be `dt:date:date_usa`

### Requirement: Ambiguity reporting

`match_all()` SHALL return every matching pattern for an input, one per base
pattern (its variant consuming the most input), ordered the way `match()`
picks: most input consumed first, then descending internal priority, so that
callers can detect dates that are valid under more than one interpretation.
The first entry SHALL be the pattern `match()` returns.

#### Scenario: Ambiguous numeric date
- **WHEN** `match_all("01/02/2020")` is called
- **THEN** the result SHALL include both a day-first and a month-first pattern

#### Scenario: Unambiguous date returns a single candidate
- **WHEN** `match_all("2026-08-04")` is called
- **THEN** the result SHALL contain exactly one candidate

### Requirement: Bulk parsing entry point

`parse_many(texts, **kwargs)` SHALL lazily yield one `parse()` result
(`datetime.datetime` or `None`) per input, in input order, passing keyword
arguments through to `parse()` and reusing the indexes built at construction.

#### Scenario: Batch of mixed inputs
- **WHEN** `list(parse_many(["01.12.2009", "invalid", "6 Jan 2009"]))` is called
- **THEN** the result SHALL equal
  `[datetime.datetime(2009, 12, 1), None, datetime.datetime(2009, 1, 6)]`

### Requirement: Timezone-aware parsing

The parser SHALL read a zone written after a time of day: a numeric offset
(`+HHMM`, `-HHMM`, `+HH:MM`, the legacy three digits `+HMM`), `Z`, `GMT` or
`UTC` alone or followed by an offset of one or two hour digits, `HH:MM` or
`HHMM` (`GMT+3`, `UTC-05:30`), or an abbreviation from
`qddate.patterns.TIMEZONE_ABBREVIATIONS` (`MSK`/`МСК`, `CET`/`CEST`,
`EET`/`EEST`, `BST`, `EST`/`EDT`, `PST`/`PDT`, …). Latin abbreviations SHALL
be matched in capitals only, and a zone SHALL NOT be followed by a letter. A
bare offset SHALL have at least three digits or the `HH:MM` form. `match()`
SHALL report the zone as written in its `timezone` value, and
`qddate.qdparser.parse_timezone()` SHALL convert such a value to a
fixed-offset `datetime.timezone` (named for an abbreviation), or `None` for an
offset of 24 hours or more.

`DateParser(tz_aware=True)` SHALL attach the zone to the returned datetime.
Without `tz_aware=True`, or when the input carries no zone, the result SHALL
be a naive datetime.

#### Scenario: Offset present, tz handling enabled
- **GIVEN** `DateParser(tz_aware=True)`
- **WHEN** `parse("01.12.2009 14:53:12 +0000")` is called
- **THEN** the result SHALL be timezone-aware with a UTC offset of `0`

#### Scenario: No offset, tz handling enabled
- **GIVEN** `DateParser(tz_aware=True)`
- **WHEN** `parse("01.12.2009 14:53")` is called
- **THEN** the result SHALL be naive

#### Scenario: tz handling disabled (default)
- **WHEN** `DateParser().parse("01.12.2009 14:53:12 +0000")` is called
- **THEN** the result SHALL be naive

#### Scenario: ISO offset with a colon
- **GIVEN** `DateParser(tz_aware=True)`
- **WHEN** `parse("2022-05-05T10:00:00+03:00")` is called
- **THEN** the result SHALL equal 10:00 at UTC offset `+03:00`

#### Scenario: Abbreviation after HH:MM
- **GIVEN** `DateParser(tz_aware=True)`
- **WHEN** `parse("5 мая 2022 г., 12:30 МСК")` is called
- **THEN** the result SHALL equal 12:30 at UTC offset `+03:00`

#### Scenario: Word that is not a zone
- **GIVEN** `DateParser(tz_aware=True)`
- **WHEN** `parse("5 May 2022 10:00 est la date")` is called
- **THEN** the result SHALL be naive

### Requirement: Two-digit year pivot

`DateParser(pivot_year=Y)` SHALL map a two-digit year `yy` from a `yearshort`
pattern to `20yy` when `yy < Y % 100` and to `19yy` otherwise. Without
`pivot_year` (the default `None`), two-digit years SHALL pass through
unchanged. `pivot_year` SHALL be an integer (a 4-digit year such as `1968`) or
`None`; the constructor SHALL raise `TypeError` for a bool or any other value,
because `True` would act as pivot year 1.

#### Scenario: Pivot enabled, high two-digit year
- **GIVEN** `DateParser(pivot_year=1968)`
- **WHEN** `parse("16.05.99")` is called
- **THEN** the result year SHALL be `1999`

#### Scenario: Pivot enabled, low two-digit year
- **GIVEN** `DateParser(pivot_year=1968)`
- **WHEN** `parse("16.05.20")` is called
- **THEN** the result year SHALL be `2020`

#### Scenario: Pivot disabled (default)
- **WHEN** `DateParser().parse("16.05.99")` is called
- **THEN** the result year SHALL be `99`

#### Scenario: Boolean pivot rejected
- **WHEN** `DateParser(pivot_year=True)` is constructed
- **THEN** it SHALL raise `TypeError` whose message names the expected 4-digit year
