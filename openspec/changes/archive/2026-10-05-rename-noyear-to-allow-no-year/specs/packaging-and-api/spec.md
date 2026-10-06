## ADDED Requirements

### Requirement: Public parsing methods accept `allow_no_year=`

`DateParser.parse`, `DateParser.match`, and `DateParser.match_all` SHALL
accept an `allow_no_year: bool = True` keyword parameter that controls whether
patterns carrying the ``noyear`` flag are eligible to match.

The legacy keyword ``noyear=`` SHALL continue to work as a deprecated alias
that emits `DeprecationWarning` recommending `allow_no_year=`.

#### Scenario: Default behaviour unchanged
- **WHEN** a caller invokes `parser.parse(text)` without any keyword
- **THEN** no-year patterns SHALL be eligible (the historical default)
- **AND** the caller SHALL NOT see a `DeprecationWarning`

#### Scenario: Explicit allow_no_year=False disables no-year patterns
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", allow_no_year=False)` is called
- **THEN** the result SHALL be `None` (no-year patterns are excluded)
- **AND** the caller SHALL NOT see a `DeprecationWarning`

#### Scenario: Legacy noyear= alias still works
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", noyear=True)` is called
- **THEN** the result SHALL equal the `allow_no_year=True` result
- **AND** a `DeprecationWarning` SHALL be emitted

#### Scenario: Legacy noyear=False still works
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", noyear=False)` is called
- **THEN** the result SHALL be `None`
- **AND** a `DeprecationWarning` SHALL be emitted