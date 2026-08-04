## ADDED Requirements

### Requirement: Timezone-aware parsing

`parse()` SHALL accept an optional timezone-handling parameter that, when enabled,
returns a timezone-aware `datetime.datetime` carrying any numeric UTC offset parsed
from the input string. When the parameter is omitted or no offset is present in the
input, `parse()` SHALL return a naive datetime, preserving current behavior.

#### Scenario: Offset present, tz handling enabled
- **GIVEN** `DateParser()` with tz handling enabled
- **WHEN** `parse("... +0530")` is called on a string whose time pattern captures an offset
- **THEN** the returned datetime SHALL be timezone-aware with an offset of `+05:30`

#### Scenario: No offset, tz handling enabled, no default tz
- **GIVEN** `DateParser()` with tz handling enabled
- **WHEN** `parse("01.12.2009 14:53")` is called (no offset in input)
- **THEN** the returned datetime SHALL be naive (status quo)

#### Scenario: tz handling disabled (default)
- **WHEN** `parse("01.12.2009 14:53:12 +0000")` is called without enabling tz handling
- **THEN** the returned datetime SHALL be naive, matching current behavior

### Requirement: Two-digit year pivot

`DateParser` SHALL accept an optional `pivot_year` parameter that, when enabled,
interprets two-digit years from `yearshort` patterns by mapping values below the
pivot break to the 2000s and values at or above the break to the 1900s. When the
parameter is omitted, two-digit years SHALL pass through unchanged (legacy behavior).

#### Scenario: Pivot enabled, high two-digit year
- **GIVEN** `DateParser(pivot_year=True)` (break at 68 by default)
- **WHEN** `parse("05/16/99")` is called
- **THEN** the result year SHALL be `1999`

#### Scenario: Pivot enabled, low two-digit year
- **GIVEN** `DateParser(pivot_year=True)`
- **WHEN** `parse("05/16/20")` is called
- **THEN** the result year SHALL be `2020`

#### Scenario: Pivot disabled (default)
- **WHEN** `parse("05/16/99")` is called without `pivot_year`
- **THEN** the result year SHALL be `99` (legacy passthrough)
