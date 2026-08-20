---
title: "Web scraping"
description: "Extract publication dates from messy HTML bylines"
---
# Web scraping

qddate exists because news and government HTML rarely stores dates in a single
clean field. Bylines look like `12.03.1999 some text here` or
`Thursday, Jun 25, 2026 - 13:46`.

## Typical pipeline

1. Extract a candidate string from the DOM (time element, byline, meta tag, or first line of the article chrome).
2. Strip leading labels (`Published:`, `Date:`).
3. Call `parse()` on a reused `DateParser`.
4. Treat `None` as "no structured date" and fall back to HTTP headers or skip.

```python
import qddate

parser = qddate.DateParser(languages=["en", "es"])

def published_at(byline: str):
    text = byline.strip()
    for prefix in ("Published:", "Date:", "Posted:"):
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
            break
    return parser.parse(text)
```

## Why left-aligned matching matters

Scrapers often capture the date plus the rest of the byline in one text node.
qddate is designed for that: the date must start the string, and everything after
it is ignored. Searching for a date in the middle of a paragraph is out of scope.

## Language subsets

If a crawl is locale-specific, pass that code. A German government crawl does
not need Russian month names:

```python
parser = qddate.DateParser(languages="de")
```

For mixed international feeds, omit `languages=` or pass the union you actually
see.

## Related

- [News aggregation](/use-cases/news-aggregation)
- [languages=](/api/languages)
- [Troubleshooting](/getting-started/troubleshooting)
