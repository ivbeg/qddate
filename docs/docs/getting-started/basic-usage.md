---
title: "Basic usage"
description: "How parse, match, and DateParser options behave"
---
# Basic usage

The public surface is small: construct a `DateParser`, then call `parse` or
`match`. Everything else is either constructor configuration or an internal
filter you can disable for debugging.

## Construct a parser once

`DateParser()` compiles and indexes patterns at construction time. Reuse the
instance across calls:

```python
import qddate

parser = qddate.DateParser()
for raw in rows:
    dt = parser.parse(raw)
```

Rebuilding a parser on every row pays the generation cost repeatedly.

## `parse` vs `match`

| Method | Returns | Typical use |
|--------|---------|-------------|
| [`parse()`](/api/parse) | `datetime.datetime` or `None` | Application code |
| [`match()`](/api/match) | `{"values", "pattern"}` or `None` | Debugging, pattern stats |

`parse()` is implemented on top of `match()`. Invalid calendar dates (month 13,
day 0, year 0) become `None` rather than raising.

## Constructor parameters

```python
DateParser(
    generate=True,
    patterns=None,      # defaults to qddate.patterns.ALL_PATTERNS
    base_only=False,
    languages=None,
)
```

- `generate=True` expands each base date pattern with time-of-day and trailing-text variants.
- `base_only=True` keeps only the base patterns (no generated "date plus extra text" variants).
- `languages=` restricts the loaded set. See [languages=](/api/languages).
- `patterns=` replaces the catalog with a caller-supplied list of pattern dicts.

## What matches

qddate matches a date **at the start of the string**. Trailing text is ignored.
Strings that are not left-aligned dates return `None`.

```python
parser.parse("2013-01-12")                 # ok
parser.parse("published 2013-01-12")       # None — date is not left-aligned
parser.parse("totally invalid date")       # None
parser.parse("")                           # None
parser.parse("1")                          # None
```

## Time of day

A time after the date populates hour, minute, and second: `HH:MM`,
`HH:MM:SS`, `14h30`, or the 12-hour clock (`3:45 PM`, `3 p.m.`). A time can
also come first (`12:30, 5 мая 2022`). A word between the date and the time is
accepted in the date's language (`at`, `à`, `um`, `a las`, `alle`, `om`, `às`,
`в`):

```python
parser.parse("May 5, 2022 at 3:45 PM")    # datetime(2022, 5, 5, 15, 45)
parser.parse("le 5 mai 2022 à 14h30")     # datetime(2022, 5, 5, 14, 30)
parser.parse("12:30 05.05.2022")          # datetime(2022, 5, 5, 12, 30)
parser.parse("23 Jul 2015, 09:00 BST")    # datetime(2015, 7, 23, 9, 0)
```

A zone after the time (`+03:00`, `Z`, `GMT+3`, `BST`, `МСК`) is read but only
attached with `DateParser(tz_aware=True)`; `match_typed()` reports it as
`tzinfo` either way.

## Filter debug flags

`parse()` and `match()` accept flags that turn off individual candidate filters.
Leave them at the defaults unless you are diagnosing a miss:

- `noprefix`
- `nocharsetfilter`
- `noseparatorfilter`
- `noyearformatfilter`
- `nolanguagefilter`

`parse()` and `match()` also accept `allow_no_year` (default `True`) to include
day-month patterns without a year. The old name `noyear` is deprecated.

## Next steps

- [DateParser](/api/dateparser)
- [Performance](/getting-started/performance)
- [Troubleshooting](/getting-started/troubleshooting)
