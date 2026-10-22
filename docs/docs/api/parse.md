---
title: "parse()"
description: "Turn a left-aligned date string into datetime.datetime or None"
---
# parse()

`DateParser.parse()` is the method most applications should call.

```python
parser.parse(text) -> datetime.datetime | None
```

## Signature

```python
parse(
    text,
    noprefix=False,
    nocharsetfilter=False,
    noseparatorfilter=False,
    noyearformatfilter=False,
    nolanguagefilter=False,
    allow_no_year=True,
    *,
    languages=None,
    date_order=None,
    reference=None,
    prefer=None,
)
```

Pass the options by keyword: `parse()` and `match()` order their positional
parameters differently.

| Argument | Default | Meaning |
|----------|---------|---------|
| `text` | required | Input string |
| `allow_no_year` | `True` | Include day-month patterns without a year; the current year is filled in. `noyear=` is a deprecated alias |
| `noprefix` | `False` | Skip prefix-based candidate filtering |
| `nocharsetfilter` | `False` | Skip character-set filtering |
| `noseparatorfilter` | `False` | Skip separator filtering |
| `noyearformatfilter` | `False` | Skip 2-digit vs 4-digit year filtering |
| `nolanguagefilter` | `False` | Skip automatic language narrowing |
| `languages` | `None` | Languages to try first; see [per-call options](/api/dateparser#per-call-options) |
| `date_order` | `None` | `"DMY"`, `"MDY"` or `"YMD"` for an ambiguous numeric date; `None` uses the parser's |
| `reference` | `None` | "Now" for a date without a year: its year is used. Default: the current time |
| `prefer` | `None` | `"past"` or `"future"`: move a date without a year across the year boundary relative to `reference` |

Leave the `no*` flags at `False` unless you are debugging a miss. Each flag
skips one level of the [filter pipeline](/api/filter-pipeline). See also
[troubleshooting](/getting-started/troubleshooting).

## Return value

- A `datetime.datetime` when a supported pattern matches at index 0 and the components form a valid calendar date. It is naive unless the parser was built with `tz_aware=True` and the input carries a zone after the time (`+0300`, `+03:00`, `Z`, `GMT+3`, `MSK`).
- `None` when nothing matches, the string is empty/whitespace, or `datetime.datetime(**components)` would raise `ValueError`.

`parse()` never raises for ordinary bad input.

## Behavior notes

- Matching is **left-aligned**. Trailing text after the date is ignored.
- A time of day populates hour, minute, and second: `HH:MM`, `HH:MM:SS`, `14h30` / `14 h 30`, or the 12-hour clock (`3:45 PM`, `11:05:09 a.m.`, `3 p.m.`; `12:00 AM` is midnight). It can follow the date (after `,`, `|` or the ISO `T`) or come first (`12:30, 5 мая 2022`, `14:30 | 5 May 2022`, `12:30 05.05.2022`).
- A word the date's language writes before the time is accepted: `at` (en), `à` (fr), `um` (de), `a las` (es), `alle` (it), `om` (nl), `às` (pt), `в` (ru): `4 Сентября 2020 в 04:06` → `datetime(2020, 9, 4, 4, 6)`. Numeric dates accept any of them (`05.05.2022 в 12:30`).
- Patterns flagged `noyear` (`05.12`, `4 Сентября`, `May 5`, `5th May`, `Sept. 5`) substitute the year of `reference` (the current year by default) when `allow_no_year=True` (the default); `prefer="past"` / `"future"` moves them across the year boundary. With `allow_no_year=False` they do not match.
- Two-digit years pass through as-is (`99` → year 99) unless the parser was built with `pivot_year=` (for example `DateParser(pivot_year=1968)` maps `99` → 1999, `20` → 2020). `pivot_year` must be an integer; `pivot_year=True` raises `TypeError`.
- A zone after the time (`+0300`, `+03:00`, `Z`, `GMT+3`, `UTC-05:30`, `MSK`/`МСК`, `CEST`, `BST`, `PDT`, …) is attached only with `DateParser(tz_aware=True)`. Latin abbreviations are matched in capitals only, so the French `est` after a time is not US Eastern time.
- Relative phrases (`today`, `3 days ago`) return `None`; use [`parse_relative()`](/api/dateparser#relative-date-parsing).

## Examples

```python
import datetime
import qddate

parser = qddate.DateParser()
assert parser.parse("01.12.2009") == datetime.datetime(2009, 12, 1)
assert parser.parse("12.03.1999 Hello people") == datetime.datetime(1999, 3, 12)
assert parser.parse("16 May 2009 14:10") == datetime.datetime(2009, 5, 16, 14, 10)
assert parser.parse("totally invalid date") is None
```

## Related

- [match()](/api/match)
- [DateParser methods](/api/dateparser#methods)
- [Filter pipeline](/api/filter-pipeline)
- [Basic usage](/getting-started/basic-usage)
