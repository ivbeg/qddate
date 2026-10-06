---
title: "DateParser"
description: "Constructor options for generating and filtering the pattern catalog"
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
DateParser(generate=True, patterns=ALL_PATTERNS, base_only=False, languages=None)
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `generate` | `True` | Expand each base date pattern with time-of-day and trailing-text variants |
| `patterns` | `qddate.patterns.ALL_PATTERNS` | Pattern dicts to load |
| `base_only` | `False` | Keep only base patterns; skip generated "date plus extra text" variants |
| `languages` | `None` | Language code, list of codes, or `None` for all languages |

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

## Instance reuse

Keep one instance for the lifetime of the worker. Construction compiles
grammars, builds length indexes, and stamps language/separator metadata onto
generated variants.

## Relative date parsing

`DateParser.parse_relative(text, reference=None)` resolves common English
and Russian relative-date phrases against a reference time. Default
`reference` is `datetime.now()`.

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

**The default `parse()` does NOT match relative phrases.** Opt in via
`DateParser(relative=True)` or call `parse_relative()` explicitly.

## Related

- [parse()](/api/parse)
- [match()](/api/match)
- [Filter pipeline](/api/filter-pipeline)
- [Adding languages](/development/adding-languages)
