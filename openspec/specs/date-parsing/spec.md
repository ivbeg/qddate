# Specification: Date Parsing

The core date-parsing capability of qddate: turning a string extracted from scraped
HTML into a `datetime.datetime`, including left-aligned matching with trailing text
and date-component validation.

## Purpose

Define the externally observable behavior of `qddate.DateParser.parse()` and
`.match()` so that refactors and new features preserve (or intentionally change) the
contract.

---

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
