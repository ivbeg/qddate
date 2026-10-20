# Specification: Language Support

qddate supports a fixed set of languages and allows callers to restrict the active
pattern set to one or more languages via the `languages=` constructor parameter.

## Purpose

Define the supported language set, the behavior of the `languages=` parameter, and the
contract of automatic language detection used internally for pattern filtering.

---

## Requirements

### Requirement: Supported languages

The library SHALL support exactly the following language codes: `bg`, `cz`, `de`,
`en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`, `uk`.

#### Scenario: Querying supported languages
- **WHEN** the list of supported languages is read
- **THEN** it SHALL contain all fourteen codes listed above

---

### Requirement: Filter patterns by language

The `DateParser` constructor SHALL accept a `languages` parameter (a single code, a
list/tuple of codes, or `None`) and SHALL restrict the active pattern set to only
those languages when it is non-empty, while still including language-neutral numeric
patterns for the applicable languages.

#### Scenario: Single-language string code
- **GIVEN** `DateParser(languages="ru")`
- **WHEN** `parse("3 Января 2003 года")` is called
- **THEN** the result SHALL equal `datetime.datetime(2003, 1, 3)`

#### Scenario: Multiple-language list
- **GIVEN** `DateParser(languages=["en", "de"])`
- **WHEN** `parse("6 Jan 2009")` is called
- **THEN** the result SHALL equal `datetime.datetime(2009, 1, 6)`

#### Scenario: Default uses all languages
- **GIVEN** `DateParser()` (no `languages` argument)
- **WHEN** dates from several languages are parsed
- **THEN** all supported languages SHALL be parseable

#### Scenario: Empty list is backward compatible
- **GIVEN** `DateParser(languages=[])`
- **WHEN** any supported date is parsed
- **THEN** it SHALL behave identically to the default (all languages)

---

### Requirement: Reject unsupported language codes

The constructor SHALL raise `ValueError` when `languages` contains any code that is
not in the supported set, listing the offending code(s).

#### Scenario: Single invalid code
- **WHEN** `DateParser(languages="invalid")` is constructed
- **THEN** a `ValueError` SHALL be raised whose message contains "Unsupported language"

#### Scenario: One invalid code among valid ones
- **WHEN** `DateParser(languages=["en", "invalid"])` is constructed
- **THEN** a `ValueError` SHALL be raised

---

### Requirement: Language-exclusive parsing

When `languages=` restricts the active set, the parser SHALL NOT successfully parse a
date that is exclusive to a non-selected language's month-name patterns.

#### Scenario: Russian excluded by English-only parser
- **GIVEN** `DateParser(languages="en")`
- **WHEN** `parse("3 Января 2003 года")` is called
- **THEN** the result SHALL be `None`

#### Scenario: Ukrainian excluded by Russian-only parser
- **GIVEN** `DateParser(languages="ru")`
- **WHEN** `parse("21 травня 2026")` is called
- **THEN** the result SHALL be `None`

---

### Requirement: Automatic language detection for filtering

The parser MAY use automatic language detection (based on character sets,
month names and weekday names) purely as an internal candidate-narrowing
optimization. Detection SHALL NOT change the result of a parse:

- when the caller supplied a `languages=` allow-list, detected languages SHALL
  be intersected with it and SHALL NOT remove patterns of a requested language;
- when a month name is shared by several languages, a weekday name in the input
  SHALL pick the language;
- when the patterns of the detected language find no match, the parser SHALL
  try the patterns of every active language.

#### Scenario: Shared month name does not drop a requested language
- **GIVEN** `DateParser(languages=["en", "de"])`
- **WHEN** `parse("28. Juli 2015")` is called ("Juli" is shared by German and Dutch)
- **THEN** the result SHALL equal `datetime.datetime(2015, 7, 28)`

#### Scenario: Weekday picks the language of a shared month
- **GIVEN** `DateParser()`
- **WHEN** `parse("Montag, 18 Juni 1953")` is called
- **THEN** the result SHALL equal `datetime.datetime(1953, 6, 18)`

#### Scenario: Wrongly detected language falls back to all languages
- **GIVEN** `DateParser()`
- **WHEN** `parse("11 Август 2009")` is called (Bulgarian; "Август" is also Russian)
- **THEN** the result SHALL equal `datetime.datetime(2009, 8, 11)`

---

### Requirement: Romanian month-name dates

The library SHALL parse Romanian day-month-year dates using all twelve full month
names and standard abbreviated month forms in lowercase or title case, and SHALL
make those patterns available through the `ro` language filter with Romanian
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
