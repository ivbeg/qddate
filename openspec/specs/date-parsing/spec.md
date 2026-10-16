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
the returned `datetime`.

#### Scenario: Date with minutes
- **WHEN** `parse("16 May 2009 14:10")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 5, 16, 14, 10)`

#### Scenario: Date with full time
- **WHEN** `parse("01.03.2009 14:53:12")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 3, 1, 14, 53, 12)`

#### Scenario: Bracketed time
- **WHEN** `parse("9 Июля 2015 [11:23]")` is called
- **THEN** the result SHALL equal `datetime.datetime(2015, 7, 9, 11, 23)`

---

### Requirement: Date component validation

The parser SHALL reject any match whose month is outside `1..12` or whose day is
outside `1..31` by treating it as no match (returning `None` for `parse`, skipping
the pattern for `match`).

#### Scenario: Invalid month rejected
- **GIVEN** a pattern that captures month `13`
- **WHEN** the candidate is evaluated
- **THEN** the candidate SHALL be skipped and the next pattern tried

#### Scenario: Invalid day rejected
- **GIVEN** a pattern that captures day `0` or `32`
- **WHEN** the candidate is evaluated
- **THEN** the candidate SHALL be skipped

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
missing year component when `parse()` or `match()` is invoked with `noyear=True`.

#### Scenario: Day-month string with current year
- **GIVEN** the system clock is set to year `2026`
- **WHEN** `match("01.12", noyear=True)` is called on a `noyear` pattern
- **THEN** the resulting year SHALL be `2026`

---

### Requirement: Consistent repeated parsing

Calling `parse()` with the same input SHALL return equal results across repeated
invocations on the same parser instance.

#### Scenario: Repeated calls are consistent
- **WHEN** `parse("01.12.2009")` is called three times
- **THEN** all three results SHALL be equal

### Requirement: Relative date parsing for English and Russian

`DateParser` SHALL expose `parse_relative(text, *, reference=None)` that
resolves common English and Russian relative-date phrases against a
reference time (default: `datetime.now()`).

`DateParser(relative=True)` SHALL make `parse()` also try the relative grammar
when the absolute grammar returns `None`. The default behaviour (without
`relative=True`) is unchanged.

#### Scenario: parse_relative resolves "today"
- **WHEN** `parser.parse_relative("today")` is called with no reference
- **THEN** the returned `datetime` SHALL have today's calendar date and
  midnight hour
- **AND** the call SHALL NOT raise

#### Scenario: parse_relative resolves "yesterday"
- **WHEN** `parser.parse_relative("yesterday")` is called
- **THEN** the returned `datetime` SHALL be `reference.date - 1 day` with
  midnight hour

#### Scenario: parse_relative resolves N-days-ago
- **WHEN** `parser.parse_relative("3 days ago")` is called
- **THEN** the returned `datetime` SHALL be `reference.date - 3 days`

#### Scenario: parse_relative with pinned reference is deterministic
- **GIVEN** `reference = datetime(2020, 6, 15, 0, 0)`
- **WHEN** `parser.parse_relative("yesterday", reference=reference)` is called
- **THEN** the result SHALL equal `datetime(2020, 6, 14, 0, 0)`

#### Scenario: parse_relative resolves Russian phrases
- **WHEN** `parser.parse_relative("сегодня")` is called
- **THEN** the result SHALL be today at midnight
- **WHEN** `parser.parse_relative("3 дня назад")` is called
- **THEN** the result SHALL be `reference.date - 3 days`

#### Scenario: parse() does not match relative phrases by default
- **GIVEN** `parser = DateParser()` (no `relative=True`)
- **WHEN** `parser.parse("today")` is called
- **THEN** the result SHALL be `None` (back-compat preserved)

#### Scenario: parse() matches relative phrases when relative=True
- **GIVEN** `parser = DateParser(relative=True)`
- **WHEN** `parser.parse("yesterday")` is called
- **THEN** the result SHALL be `datetime.now().date() - 1 day`

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

### Requirement: Fingerprint-based filter is exactly equivalent to the legacy filter

For every input string the fingerprint-based filter SHALL return a
candidate pattern set that is **equal** to the candidate set the
existing 6-level filter would have returned for the same input. The
equality MUST hold under any combination of filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``,
``noseparatorfilter``, ``noyearformatfilter``, ``nolanguagefilter``).

#### Scenario: Equality on the extended probe corpus
- **GIVEN** any string from the extended probe corpus (the union of the
  reachability probes and the regression corpus — 165 strings covering
  every shipped language, every separator, every year-format bucket,
  weekday + short + compact + edge cases)
- **WHEN** the same string is fed to both filters
- **THEN** the two candidate sets SHALL be equal (no additions, no removals)

### Requirement: Toggles preservation across filter toggles

The fingerprint-based filter SHALL honour the existing filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``, ``noseparatorfilter``,
``noyearformatfilter``, ``nolanguagefilter``) and SHALL produce the same
candidate set as the legacy filter under the same toggles.

#### Scenario: Disabling nocharsetfilter widens the candidate set symmetrically
- **GIVEN** two parsers (``use_fingerprint=True`` and ``use_fingerprint=False``)
  both with ``nocharsetfilter=True``
- **WHEN** the same text is fed to both
- **THEN** both candidate sets SHALL be equal

