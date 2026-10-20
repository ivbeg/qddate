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

The parser SHALL accept an optional time-of-day suffix in `HH:MM` or `HH:MM:SS` form
after a date and SHALL populate the hour, minute, and (when present) second fields of
the returned `datetime`. After a Russian date the suffix MAY be preceded by the
word `в` ("at"); the word SHALL NOT be accepted after a date in another language.

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
`allow_no_year=True` (the default). With `allow_no_year=False`, `noyear` patterns
SHALL NOT match. Only a pattern marked `noyear` SHALL match a date without a year.
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

#### Scenario: No-year patterns disabled
- **WHEN** `parse("4 Сентября в 04:06:33", allow_no_year=False)` or
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
(`language`, `None` for language-neutral patterns), its `format` string and the
raw input (`raw`), or `None` when nothing matches. `DateMatch.to_dict()` SHALL
return a plain dict of those fields. The dict returned by `match()` SHALL
remain unchanged.

#### Scenario: Typed result for a supported date
- **WHEN** `match_typed("01.12.2009")` is called
- **THEN** the result SHALL expose `.datetime == datetime.datetime(2009, 12, 1)`
- **AND** `.pattern_key == "dt:date:date_2"`, `.format == "%d.%m.%Y"`,
  `.raw == "01.12.2009"`

#### Scenario: Legacy dict shape preserved
- **WHEN** `match("01.12.2009")` is called
- **THEN** the result SHALL remain a dict with `"values"` and `"pattern"` keys

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

`DateParser(tz_aware=True)` SHALL attach a numeric UTC offset captured from the
input (`+HHMM` / `-HHMM`) to the returned datetime as a fixed-offset `tzinfo`.
Without `tz_aware=True`, or when the input carries no numeric offset, the
result SHALL be a naive datetime. Timezone abbreviations (`UTC`, `GMT`, `MSK`)
SHALL NOT be applied.

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
