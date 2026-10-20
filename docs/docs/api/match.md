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
    allow_no_year=True,
    nocharsetfilter=False,
    noseparatorfilter=False,
    noyearformatfilter=False,
    nolanguagefilter=False,
)
```

Arguments match [`parse()`](/api/parse):

| Argument | Default | Meaning |
|----------|---------|---------|
| `allow_no_year` | `True` | Include patterns that omit the year (current year is filled later by `parse()`) |

Set `allow_no_year=False` to skip day-month-only patterns (`05.12`,
`4 Сентября`) and reduce false positives on short numeric fragments. The old name `noyear=` still works as a
keyword and emits `DeprecationWarning`. Pass the options by keyword: the
positional order differs from `parse()`. Each `no*` flag skips one level of the
[filter pipeline](/api/filter-pipeline).

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

Candidates with a month outside 1–12, a day outside 1–31, an hour above 23, or a
minute or second above 59 are skipped; the next candidate pattern is tried.

Among the remaining candidates, the one that consumes the most input wins, so
`14 Avril 1995 20:16:12` keeps its time; the internal priority only breaks ties
between matches of the same length.

## Related methods

- `match_all(text, ...)` returns every matching pattern, ranked the way
  `match()` picks (longest match first, then priority), so you can spot ambiguous dates such as `01/02/2020` (day-first and
  month-first).
- `match_typed(text, ...)` returns the best match as a `DateMatch` with the
  datetime already built. See [DateParser](/api/dateparser#datematch).

## When to use it

- Logging which pattern fired in a crawl
- Building analytics over `pattern["key"]`
- Diagnosing unexpected parses

Application code that only needs a timestamp should call [`parse()`](/api/parse).
