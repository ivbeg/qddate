---
title: "Best practices"
description: "Practical defaults for constructing parsers and handling misses"
---
# Best practices

## Construct once, parse many

Build a single `DateParser` per process or worker. Pattern generation and
indexing happen in `__init__`; `parse()` is the cheap path.

```python
parser = qddate.DateParser(languages=["en", "de"])
dates = [parser.parse(row) for row in rows]
```

## Restrict languages when you know them

Pass `languages=` for crawls that stay in one locale or a small set. This is
faster and avoids month-name collisions across languages.

## Treat `None` as "no date"

Do not wrap `parse()` in try/except for normal misses. Invalid input and
unsupported formats return `None`. Catch `ValueError` only around constructor
calls with untrusted `languages=` values.

## Keep dates left-aligned

Strip leading labels in the scraper, not in qddate:

```python
text = raw.lstrip()
# or cut a known prefix such as "Published: "
```

qddate ignores **trailing** noise; it does not search the middle of a sentence.

## Prefer explicit formats upstream

When you control the producer, emit ISO-8601 (`YYYY-MM-DD`). qddate still helps
for third-party HTML; it is not a substitute for a stable date field in your own
APIs.

## Do not use qddate for relative dates

"yesterday", "2 days ago", and timezone-aware scheduling belong in dateparser or
dateutil. Mixing libraries by concern is expected: qddate for bylines, another
parser for user-typed relative phrases. See [when to use](/getting-started/when-to-use).

## Add patterns with tests, not one-off regexes

New formats should land as named entries in `qddate/patterns/` plus fixtures in
`tests/`. After adding them, regenerate the language catalog:

```bash
python scripts/generate_pattern_docs.py
```

See [adding languages](/development/adding-languages).
