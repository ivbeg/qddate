## ADDED Requirements

### Requirement: Relative date parsing

The parser SHALL provide an opt-in capability to resolve relative date expressions
("today", "yesterday", "tomorrow", "N days/hours ago") against a reference time
(defaulting to the current time), returning a `datetime.datetime`. When relative
parsing is not enabled, such expressions SHALL return `None` as they do today.

#### Scenario: Relative parsing enabled, "yesterday"
- **GIVEN** relative parsing enabled and a fixed reference time of `2026-08-04`
- **WHEN** `parse("yesterday")` is called
- **THEN** the result SHALL equal `datetime.datetime(2026, 8, 3)`

#### Scenario: Relative parsing disabled (default)
- **WHEN** `parse("yesterday")` is called without enabling relative parsing
- **THEN** the result SHALL be `None`

#### Scenario: Unsupported relative expression
- **GIVEN** relative parsing enabled
- **WHEN** `parse("sometime next week maybe")` is called
- **THEN** the result SHALL be `None`

### Requirement: Ambiguity reporting

The parser SHALL provide a method to return all matching patterns for an input,
ranked by internal priority, so that callers can detect ambiguous dates (e.g. a date
valid as both day/month/year and month/day/year). The existing single-result `match()`
SHALL remain unchanged.

#### Scenario: Ambiguous numeric date
- **WHEN** the multi-match method is called on `"01/02/2020"`
- **THEN** the result SHALL include at least two candidates interpreting the date as
  both day-first and month-first
- **AND** the candidates SHALL be ordered by descending priority

#### Scenario: Unambiguous date returns single candidate
- **WHEN** the multi-match method is called on `"2026-08-04"`
- **THEN** the result SHALL contain exactly one candidate

### Requirement: Date formatting helper

The parser SHALL expose a formatting helper that renders a `datetime.datetime` to a
canonical string using a pattern's `format` string, enabling normalization of scraped
dates to a single representation.

#### Scenario: Round-trip parse then format
- **WHEN** a datetime parsed from `"01.12.2009"` is formatted with the matching
  pattern's format
- **THEN** the output SHALL reproduce the canonical form of that pattern
