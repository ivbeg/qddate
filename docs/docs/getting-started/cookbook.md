---
title: "Cookbook"
description: "Pick a role and goal, then follow verified qddate examples"
---
# Cookbook

qddate covers a small, focused surface. This page is a task-oriented index: find
the row that sounds like you, then follow the linked sections. If you are
completely new, do the [one-minute quickstart](/getting-started/quick-start) first.

| You are a… | You want to… | Start with |
|------------|--------------|------------|
| [Web scraper](/use-cases/web-scraping) | Pull publication dates out of HTML bylines with trailing noise | `DateParser().parse(text)` |
| [Data engineer](/use-cases/bulk-processing) | Parse millions of strings from a crawl with a language subset | `DateParser(languages=[...])` |
| [News aggregator](/use-cases/news-aggregation) | Reconstruct RSS-like feeds from sites that never offered one | parse + left-aligned matching |
| Application developer | Normalize mixed numeric and month-name dates in Python | [Basic usage](/getting-started/basic-usage) |
| [Contributor](/development/adding-languages) | Add a language or a rare format | pattern tables + tests |

## Common recipes

### Date plus trailing HTML text

```python
parser.parse("12.03.1999 Hello people")
# datetime.datetime(1999, 3, 12, 0, 0)
```

### Date with time of day

```python
parser.parse("16 May 2009 14:10")
parser.parse("01.03.2009 14:53:12")
parser.parse("9 Июля 2015 [11:23]")
```

### English weekday + abbreviated month

```python
parser.parse("Thursday, Jun 25, 2026")
parser.parse("Monday, Jun 22, 2026 - 13:46")
```

### Spanish article dates

```python
parser.parse("03 de Julio, 2026")
parser.parse("30 de junio, 2026")
```

### Dates without a year

```python
parser.match("01.12", noyear=True)
# year is substituted from the current clock
```

Pass `noyear=True` only when you intentionally want day-month strings. It can
increase false positives on short numeric fragments.

## Detailed walkthroughs

- [Web scraping](/use-cases/web-scraping)
- [Bulk processing](/use-cases/bulk-processing)
- [News aggregation](/use-cases/news-aggregation)
- [API reference](/api/)
