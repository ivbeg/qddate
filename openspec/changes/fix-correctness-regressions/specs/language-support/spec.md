## MODIFIED Requirements

### Requirement: Automatic language detection for filtering

The parser MAY use automatic language detection (based on character sets and month
names) purely as an internal candidate-narrowing optimization. When the caller has
supplied a `languages=` allow-list, any detected-language narrowing SHALL be
intersected with that allow-list and SHALL NOT remove patterns belonging to a
language the caller explicitly requested.

#### Scenario: Shared month name does not drop a requested language
- **GIVEN** `DateParser(languages=["en", "de"])`
- **WHEN** `parse("28. Juli 2015")` is called (where "Juli" is shared by German/Dutch)
- **THEN** the result SHALL equal `datetime.datetime(2015, 7, 28)`

#### Scenario: Detection still narrows within the allow-list
- **GIVEN** `DateParser(languages=["en", "de", "ru"])`
- **WHEN** a Cyrillic Russian date is parsed
- **THEN** the parser MAY narrow candidates to the Russian subset of the allow-list
