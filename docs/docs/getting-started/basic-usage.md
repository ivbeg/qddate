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

## Time suffixes

Optional `HH:MM` or `HH:MM:SS` after the date populates hour, minute, and second:

```python
parser.parse("23 Jul 2015, 09:00 BST")
# datetime.datetime(2015, 7, 23, 9, 0)
```

Timezone labels such as `BST` are not interpreted; they are trailing text.

## Filter debug flags

`parse()` and `match()` accept flags that turn off individual candidate filters.
Leave them at the defaults unless you are diagnosing a miss:

- `noprefix`
- `nocharsetfilter`
- `noseparatorfilter`
- `noyearformatfilter`
- `nolanguagefilter`

`match()` also accepts `noyear` (default `True`) to include day-month patterns
without a year.

## Next steps

- [DateParser](/api/dateparser)
- [Performance](/getting-started/performance)
- [Troubleshooting](/getting-started/troubleshooting)
