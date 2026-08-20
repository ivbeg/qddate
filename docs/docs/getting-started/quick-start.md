---
title: "Quick Start"
description: "Parse a first dirty date string with qddate in under a minute"
---
# Quick Start

Short task-oriented paths to first success. Installation details:
[Installation](/getting-started/installation). Method list:
[API reference](/api/).

## Parse one string

```python
import qddate

parser = qddate.DateParser()
print(parser.parse("2012-12-15"))
print(parser.parse("Fri, 12 Dec 2014 10:55:50"))
print(parser.parse("12.03.1999 some text here"))
```

`parse()` returns a `datetime.datetime` when the string starts with a supported
date, otherwise `None`. Trailing prose after the date is ignored.

## Restrict languages

```python
import qddate

parser = qddate.DateParser(languages=["en", "de"])
print(parser.parse("28. Juli 2015"))   # 2015-07-28 00:00:00
print(parser.parse("6 Jan 2009"))       # 2009-01-06 00:00:00
print(parser.parse("3 Января 2003 года"))  # None
```

Passing `languages=` loads fewer patterns and avoids cross-language month-name
ambiguity. See [languages=](/api/languages).

## Inspect which pattern matched

```python
result = parser.match("01.12.2009")
if result:
    print(result["pattern"]["key"])
    print(dict(result["values"]))
```

`match()` is the lower-level API: it returns parsed components and pattern
metadata instead of a `datetime`. See [match()](/api/match).

## Next steps

- [Cookbook](/getting-started/cookbook) — pick a role and a goal
- [When to use qddate](/getting-started/when-to-use)
- [Languages and patterns](/languages/)
- [Web scraping](/use-cases/web-scraping)
