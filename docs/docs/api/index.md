---
title: "API overview"
description: "Public Python surface: DateParser and its methods, DateMatch, format_date, and languages"
---
# API overview

qddate exposes a small public surface. Import `DateParser`, `DateMatch` and
`format_date` from the top-level package; pattern tables live in
`qddate.patterns`.

```python
from qddate import DateMatch, DateParser, format_date
import qddate

qddate.__version__
```

## Classes and methods

| Symbol | Role |
|--------|------|
| [`DateParser`](/api/dateparser) | Constructs and indexes the pattern catalog |
| [`DateParser.parse`](/api/parse) | String → `datetime.datetime` or `None` |
| [`DateParser.match`](/api/match) | String → `{values, pattern}` or `None` |
| [`DateParser.match_all`](/api/dateparser#methods) | String → every matching `{values, pattern}`, highest priority first |
| [`DateParser.match_typed`](/api/dateparser#datematch) | String → `DateMatch` or `None` |
| [`DateParser.parse_many`](/api/dateparser#methods) | Iterable of strings → iterator of `datetime.datetime` or `None` |
| [`DateParser.parse_relative`](/api/dateparser#relative-date-parsing) | `today`, `3 days ago`, `через 5 дней` → `datetime.datetime` or `None` |
| [`DateParser.format_date`](/api/dateparser#datematch) / `qddate.format_date` | `datetime` + pattern key → string |
| [`DateParser.start_session` / `end_session`](/api/dateparser#methods) | Restrict matching to chosen pattern keys |
| [`DateMatch`](/api/dateparser#datematch) | Typed match result: `datetime`, `pattern_key`, `language`, `format`, `raw` |
| [`languages=`](/api/languages) | Restrict the catalog at construction |

## Package layout

- `qddate.DateParser`: the parser class
- `qddate.DateMatch`: typed result of `match_typed()`
- `qddate.format_date`: module-level form of `DateParser.format_date()`
- `qddate.__version__`: package version string
- `qddate.patterns`: pattern tables, `ALL_PATTERNS`, `SUPPORTED_LANGUAGES`, `get_patterns_for_languages`

Internal helpers (`qddate.dirty`, filter indexes, generated variant keys) may
change without a major version bump.

## Runtime contract

- Python 3.10–3.14, CPython and PyPy (CI tests CPython)
- Runtime dependency: `pyparsing` only
- Import does not read extra files or call the network
- Import enables pyparsing packrat caching as a process-level optimization

Authoritative behavioral specs live in `openspec/specs/` in the repository.
This site describes the same contract for humans.
