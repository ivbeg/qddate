## MODIFIED Requirements

### Requirement: Supported languages

The library SHALL support exactly the following language codes: `bg`, `cz`, `de`,
`en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`.

#### Scenario: Querying supported languages
- **WHEN** the list of supported languages is read
- **THEN** it SHALL contain all thirteen codes listed above

## ADDED Requirements

### Requirement: Romanian month-name dates

The library SHALL parse Romanian day-month-year dates using all twelve full month
names and standard abbreviated month forms in lowercase or title case, and SHALL make
those patterns available through the `ro` language filter with correct Romanian
pattern metadata.

#### Scenario: Full Romanian month name
- **GIVEN** `DateParser(languages="ro")`
- **WHEN** `parse("19 Februarie 2026")` is called
- **THEN** the result SHALL equal `datetime.datetime(2026, 2, 19)`

#### Scenario: Lowercase Romanian month name
- **WHEN** `DateParser().parse("4 decembrie 2025")` is called
- **THEN** the result SHALL equal `datetime.datetime(2025, 12, 4)`

#### Scenario: Abbreviated Romanian month name
- **GIVEN** `DateParser(languages="ro")`
- **WHEN** `parse("23 apr. 2025")` is called
- **THEN** the result SHALL equal `datetime.datetime(2025, 4, 23)`

#### Scenario: Shared month under Romanian filter
- **GIVEN** `DateParser(languages="ro")`
- **WHEN** `match("21 Mai 2026")` is called
- **THEN** the result SHALL represent `2026-05-21` and its pattern metadata SHALL identify `ro`

#### Scenario: Generated time and trailing text variant
- **GIVEN** `DateParser(languages="ro")`
- **WHEN** `parse("31 Martie 2025, 14:30 actualizare")` is called
- **THEN** the result SHALL equal `datetime.datetime(2025, 3, 31, 14, 30)`

#### Scenario: Romanian filter excludes French
- **GIVEN** `DateParser(languages="ro")`
- **WHEN** `parse("21 janvier 2026")` is called
- **THEN** the result SHALL be `None`
