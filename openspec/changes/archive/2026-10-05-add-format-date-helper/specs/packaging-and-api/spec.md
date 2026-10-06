## ADDED Requirements

### Requirement: Round-trip format helper

The library SHALL expose a `format_date()` function and equivalent instance
methods that round-trip a parsed `datetime` back into a string the parser
will accept again, using the format string attached to the matched pattern.

#### Scenario: Round-trip a parsed English date
- **GIVEN** `parser.parse("6 Jan 2009")` returns a `DateMatch` for
  `pattern_key="dt:date:date_eng1_short"` with `datetime(2009, 1, 6)`
- **WHEN** `match.format_date()` is called
- **THEN** the returned string SHALL be `"6 Jan 2009"`
- **AND** the returned string SHALL be parseable back to the same datetime

#### Scenario: Locale round-trip via Russian pattern
- **GIVEN** `parser.parse("05 Января 2003")` returns a `DateMatch`
- **WHEN** `format_date(match.datetime, pattern_key="dt:date:date_rus1_short")` is called
- **THEN** the returned string SHALL contain the Russian month word
- **AND** the returned string SHALL be parseable back to the same datetime

#### Scenario: Unknown pattern key raises
- **WHEN** `format_date(dt, pattern_key="not:a:real:key")` is called
- **THEN** `ValueError` SHALL be raised with a message naming the unknown key

#### Scenario: format_date exposed on DateParser
- **GIVEN** a `DateParser` instance `parser` and a `datetime` `dt`
- **WHEN** `parser.format_date(dt, pattern_key=...)` is called
- **THEN** the result SHALL match the standalone `format_date(dt, pattern_key=...)`

### Requirement: DateMatch exposes format_date

`DateMatch` SHALL expose `format_date()` as an instance method that uses the
match's own `format` string and `datetime` to produce the round-trip output.

#### Scenario: DateMatch.format_date() works without explicit pattern key
- **GIVEN** a `DateMatch` produced by any `DateParser.match()` or
  `DateParser.parse()` call
- **WHEN** `match.format_date()` is called
- **THEN** the returned string SHALL be the result of
  `match.datetime.strftime(match.format)`
- **AND** no `ValueError` SHALL be raised for any successful match