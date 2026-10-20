## MODIFIED Requirements

### Requirement: Supported languages

The library SHALL support exactly the following language codes: `bg`, `cz`, `de`,
`en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`, `uk`.

#### Scenario: Querying supported languages
- **WHEN** the list of supported languages is read
- **THEN** it SHALL contain all fourteen codes listed above

### Requirement: Language-exclusive parsing

When `languages=` restricts the active set, the parser SHALL NOT successfully parse a
date that is exclusive to a non-selected language's month-name patterns.

#### Scenario: Ukrainian excluded by Russian-only parser
- **GIVEN** `DateParser(languages="ru")`
- **WHEN** `parse("21 травня 2026")` is called
- **THEN** the result SHALL be `None`
