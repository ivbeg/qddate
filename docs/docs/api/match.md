---
title: "match()"
description: "Return parsed components and the pattern that matched"
---
# match()

`DateParser.match()` is the lower-level API. It returns the pyparsing result
and the pattern metadata instead of building a `datetime`.

```python
parser.match(text) -> dict | None
```

## Signature

```python
match(
    text,
    noprefix=False,
    noyear=True,
    nocharsetfilter=False,
    noseparatorfilter=False,
    noyearformatfilter=False,
    nolanguagefilter=False,
)
```

Arguments match [`parse()`](/api/parse), plus:

| Argument | Default | Meaning |
|----------|---------|---------|
| `noyear` | `True` | Include patterns that omit the year (current year is filled later by `parse()`) |

Set `noyear=False` to skip day-month-only patterns and reduce false positives on
short numeric fragments.

## Return value

On success, a dict with two keys:

- `values` — pyparsing `ParseResults`; items are `int()`-able (`day`, `month`, `year`, and optionally time fields)
- `pattern` — the matched pattern metadata dict, including `key`, `name`, `format`, `length`, and related flags

On failure, `None`.

```python
result = parser.match("01.12.2009")
result["pattern"]["key"]   # e.g. 'dt:date:date_2'
dict(result["values"])     # {'day': '01', 'month': '12', 'year': '2009'}
```

Month values outside 1–12 and day values outside 1–31 are skipped; the next
candidate pattern is tried.

## When to use it

- Logging which pattern fired in a crawl
- Building analytics over `pattern["key"]`
- Diagnosing unexpected parses

Application code that only needs a timestamp should call [`parse()`](/api/parse).
