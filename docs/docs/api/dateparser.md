---
title: "DateParser"
description: "Constructor options and the methods of DateParser"
---
# DateParser

`qddate.DateParser` holds the compiled pattern catalog and the indexes used to
narrow candidates before pyparsing runs.

```python
from qddate import DateParser

parser = DateParser()
parser = DateParser(languages=["en", "de"])
parser = DateParser(generate=True, base_only=False)
```

## Constructor

```python
DateParser(generate=True, patterns=ALL_PATTERNS, base_only=False, languages=None,
           pivot_year=None, tz_aware=False, use_fingerprint=True, date_order=None)
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `generate` | `True` | Expand each base date pattern with time-of-day and trailing-text variants |
| `patterns` | `qddate.patterns.ALL_PATTERNS` | Pattern dicts to load |
| `base_only` | `False` | Keep only base patterns; skip generated "date plus extra text" variants |
| `languages` | `None` | Language code, list of codes, or `None` for all languages |
| `pivot_year` | `None` | 4-digit pivot for two-digit years: with `1968`, `99` → 1999 and `20` → 2020. `None` keeps the raw two-digit year. A bool or other non-integer raises `TypeError`: `pivot_year=True` would mean pivot year 1 |
| `tz_aware` | `False` | Attach the zone written after the time to the result: `+0300`, `+03:00`, `Z`, `GMT+3`, `UTC-05:30` or an abbreviation (`MSK`/`МСК`, `CET`/`CEST`, `EET`/`EEST`, `BST`, `EST`/`EDT`, `PST`/`PDT`, …; see `qddate.patterns.TIMEZONE_ABBREVIATIONS`) |
| `use_fingerprint` | `True` | Use the fingerprint candidate filter. `False` selects the legacy 6-level filter and emits `DeprecationWarning`; it will be removed in 2.0 |
| `date_order` | `None` | `"DMY"`, `"MDY"` or `"YMD"`: how to read a numeric date several patterns read differently (`05/06/2022`). `None` keeps day first. Overridable per call |

If `languages` is a non-empty string or list, the catalog is filtered with
`qddate.patterns.get_patterns_for_languages` **before** generation. Empty list
and `None` both mean "all languages". Invalid codes raise `ValueError`.

See [languages=](/api/languages) for allow-list behavior.

## Custom pattern lists

Advanced callers can pass a subset or a locally defined list:

```python
from qddate.patterns import PATTERNS_EN, INTEGER_LIKE_PATTERNS

parser = DateParser(patterns=PATTERNS_EN + INTEGER_LIKE_PATTERNS)
```

The parser uses exactly those patterns. Each item is a dict with at least
`key`, `pattern` (pyparsing grammar), `length`, and usually `format`.

## Methods

| Method | Returns | Notes |
|--------|---------|-------|
| [`parse(text, ...)`](/api/parse) | `datetime` or `None` | Best match as a datetime |
| [`match(text, ...)`](/api/match) | `dict` or `None` | Best match as `{"values", "pattern"}` |
| `match_all(text, ...)` | `list[dict]` | Every matching pattern, longest match first, then priority; the first item is what `match()` returns |
| `match_typed(text, **kwargs)` | `DateMatch` or `None` | Best match as a typed object (below) |
| `parse_many(texts, **kwargs)` | iterator of `datetime` or `None` | One `parse()` result per input, in order |
| `parse_relative(text, reference=None)` | `datetime` or `None` | Relative phrases (below) |
| `format_date(dt, pattern_key)` | `str` | Formats `dt` with the pattern's `format` string |
| `start_session(keys)` / `end_session()` | `None` | Restrict matching to the given pattern keys until the session ends |

The keyword filters of `parse()` and `match()` (`allow_no_year`, `noprefix`,
`nocharsetfilter`, ...) pass through `match_typed()` and `parse_many()`.

## Per-call options

`match()`, `match_all()`, `parse()`, `match_typed()` and `parse_many()` also
take these keyword-only options, so one parser can serve pages in different
languages and locales:

| Option | Methods | Meaning |
|--------|---------|---------|
| `languages=` | all | Language code or list to try first: their patterns and the language-neutral numeric ones run first, the others only when none of them matches. Never excludes a pattern (unlike the constructor's `languages=`). The candidate index for each set of languages is built once and kept |
| `date_order=` | all | `"DMY"`, `"MDY"` or `"YMD"` for this call; `None` uses the constructor's value |
| `reference=` | `parse`, `match_typed` | The moment that counts as "now" for a date without a year (`05.12`, `4 Сентября`): its year is used. Default: the current time |
| `prefer=` | `parse`, `match_typed` | For a date without a year: `"past"` moves it to the previous year when it would lie more than `qddate.qdparser.NOYEAR_ROLLOVER_GRACE` (2 days) after `reference`; `"future"` to the next year when it would lie more than that before it. `None` keeps the reference year |

```python
parser.match("18 Juni 1953", languages="de")["pattern"]["key"]  # 'dt:date:de_base' (nl_base without the hint)
parser.parse("05/13/2022", languages="ru")    # datetime(2022, 5, 13): no Russian pattern reads it, English does
parser.parse("05/06/2022", date_order="MDY")  # datetime(2022, 5, 6)
parser.parse("13/05/2022", date_order="MDY")  # datetime(2022, 5, 13): not ambiguous
parser.parse("31.12", reference=datetime(2026, 1, 2), prefer="past")  # datetime(2025, 12, 31)
```

`date_order` decides only between patterns that consume the same text; a
longer match still wins. The month-first patterns are `date_usa` and
`date_usa_1` (slashes): dotted and dashed dates stay day first under `"MDY"`.
`"YMD"` prefers the year-first patterns (`date_3`, `date_6`, `date_9`,
`date_10`), which matters for eight-digit dates such as `12101112`.

```python
parser.match_all("01/02/2020")       # date_1 (day first) and date_usa (month first)
list(parser.parse_many(["01.12.2009", "junk"]))   # [datetime(2009, 12, 1), None]

parser.start_session(["dt:date:date_eng1"])
parser.parse("01.12.2009")           # None: outside the session
parser.parse("5 August 2001")        # datetime(2001, 8, 5)
parser.end_session()
```

The camelCase `startSession()` / `endSession()` still work and emit
`DeprecationWarning`.

## DateMatch

`match_typed()` returns a `qddate.DateMatch` dataclass:

```python
m = parser.match_typed("6 Jan 2009")
m.datetime      # datetime(2009, 1, 6, 0, 0); pivot_year / tz_aware already applied
m.pattern_key   # "dt:date:date_eng1_short"
m.language      # "en" (None for language-neutral numeric patterns)
m.format        # "%d.%b.%Y"
m.raw           # "6 Jan 2009"
m.span          # (0, 10): where the date is in raw; raw[m.span[1]:] is the rest
m.precision     # "day", "hour" ("3 PM"), "minute" or "second"
m.tzinfo        # zone written after the time ("+03:00", "МСК") or None
m.has_year      # False for "05.12": the year came from reference=
m.to_dict()     # the same fields as a plain dict
m.format_date() # formats m.datetime with m.format
```

`tzinfo` is set whether or not the parser has `tz_aware=True`; only with it is
`m.datetime` aware. An abbreviation's timezone carries its name
(`m.tzinfo.tzname(None) == "МСК"`). `qddate.qdparser.parse_timezone(text)`
converts a `timezone` value of `match()` the same way.

`qddate.format_date(dt, pattern_key)` is the module-level form of
`DateParser.format_date()`.

## Instance reuse

Keep one instance for the lifetime of the worker. Construction compiles
grammars, builds length indexes, and stamps language/separator metadata onto
generated variants.

## Relative date parsing

`DateParser.parse_relative(text, reference=None)` resolves common English
and Russian relative-date phrases against a reference time. Default
`reference` is `datetime.now()`. The result keeps the reference's time of day;
only the calendar date moves.

```python
from datetime import datetime
from qddate import DateParser

parser = DateParser()

# Reference is pinned for deterministic tests / scraping historic content.
ref = datetime(2026, 6, 15, 12, 0, 0)

parser.parse_relative("today", ref)            # 2026-06-15 12:00:00
parser.parse_relative("yesterday", ref)        # 2026-06-14 12:00:00
parser.parse_relative("3 days ago", ref)       # 2026-06-12 12:00:00
parser.parse_relative("in 5 days", ref)        # 2026-06-20 12:00:00
parser.parse_relative("two weeks ago", ref)    # word-form numbers
parser.parse_relative("сегодня", ref)            # Russian today
parser.parse_relative("3 дня назад", ref)       # Russian 3 days ago
parser.parse_relative("через 5 дней", ref)     # Russian in 5 days
parser.parse_relative("not a date", ref)       # None
```

Supported phrases:

| Direction | English | Russian |
|---|---|---|
| Anchors | `today`, `yesterday`, `tomorrow` | `сегодня`, `вчера`, `завтра` |
| Past | `N unit(s) ago` | `N <unit> назад` |
| Future | `(in) N unit(s)` | `через N <unit>` |

Units: `day(s)` / `days`; `week(s)`; `month(s)`; `year(s)`; and Russian
`день`/`дня`/`дней`, `неделю`/`недели`/`недель`, `месяц`/`месяца`/`месяцев`,
`год`/`года`/`лет`. Both digit-form (`3`) and word-form (`three`) numbers are
accepted for English.

**`parse()` does not match relative phrases.** Call `parse_relative()`
explicitly; there is no constructor switch that adds them to `parse()`.

## Related

- [parse()](/api/parse)
- [match()](/api/match)
- [Filter pipeline](/api/filter-pipeline)
- [Adding languages](/development/adding-languages)
