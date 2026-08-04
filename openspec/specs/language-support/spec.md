# Specification: Language Support

qddate supports a fixed set of languages and allows callers to restrict the active
pattern set to one or more languages via the `languages=` constructor parameter.

## Purpose

Define the supported language set, the behavior of the `languages=` parameter, and the
contract of automatic language detection used internally for pattern filtering.

---

### Requirement: Supported languages

The library SHALL support exactly the following language codes: `bg`, `cz`, `de`,
`en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ru`, `tr`.

#### Scenario: Querying supported languages
- **WHEN** the list of supported languages is read
- **THEN** it SHALL contain all twelve codes listed above

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

---

### Requirement: Automatic language detection for filtering

The parser MAY use automatic language detection (based on character sets and month
names) purely as an internal candidate-narrowing optimization. It SHALL NOT cause a
user-requested language (via `languages=`) to be dropped from consideration.

> Note: the current shipped behavior violates this requirement for shared month names
> (e.g. German "Juli" detected as Dutch). That violation is tracked as a proposed
> change in `changes/fix-correctness-regressions/`, not as accepted behavior.
