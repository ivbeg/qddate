---
title: "API overview"
description: "Public Python surface: DateParser, parse, match, and languages"
---
# API overview

qddate exposes a small public surface. Import `DateParser` from the top-level
package; pattern tables live in `qddate.patterns`.

```python
from qddate import DateParser
import qddate

qddate.__version__
```

## Classes and methods

| Symbol | Role |
|--------|------|
| [`DateParser`](/api/dateparser) | Constructs and indexes the pattern catalog |
| [`DateParser.parse`](/api/parse) | String → `datetime.datetime` or `None` |
| [`DateParser.match`](/api/match) | String → `{values, pattern}` or `None` |
| [`languages=`](/api/languages) | Restrict the catalog at construction |

## Package layout

- `qddate.DateParser` — supported public class
- `qddate.__version__` — package version string
- `qddate.patterns` — pattern tables, `ALL_PATTERNS`, `SUPPORTED_LANGUAGES`, `get_patterns_for_languages`

Internal helpers (`qddate.dirty`, filter indexes, generated variant keys) may
change without a major version bump.

## Runtime contract

- Python 3.8–3.12, CPython and PyPy
- Runtime dependency: `pyparsing` only
- Import does not read extra files or call the network
- Import enables pyparsing packrat caching as a process-level optimization

Authoritative behavioral specs live in `openspec/specs/` in the repository.
This site describes the same contract for humans.
