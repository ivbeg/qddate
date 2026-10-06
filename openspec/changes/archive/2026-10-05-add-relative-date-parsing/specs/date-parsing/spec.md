## ADDED Requirements

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