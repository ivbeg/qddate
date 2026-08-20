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

## Related

- [parse()](/api/parse)
- [match()](/api/match)
- [Adding languages](/development/adding-languages)
