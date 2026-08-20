---
title: "News aggregation"
description: "Rebuild publication timestamps for sites that never offered RSS"
---
# News aggregation

qddate ships as part of a "news reconstruction" toolchain: sites without RSS
still have human-readable dates in HTML. Parsing those strings quickly is what
lets a crawler attach a timestamp to each reconstructed item.

## What the parser assumes

- The candidate is a **publication date**, not a relative phrase.
- It appears at the **start** of the extracted string.
- Language coverage is the 14 supported codes, not every locale on earth.

Relative labels ("2 hours ago") need a different tool. See
[when to use](/getting-started/when-to-use).

## Mixed-language feeds

A feed that mixes English, Spanish, and Romanian should list those codes:

```python
parser = qddate.DateParser(languages=["en", "es", "ro"])
```

Shared month tokens (`May` / `Mai` / `August`) can be ambiguous when every
language is loaded. An explicit allow-list makes the intended catalog
deterministic.

## Time of day is optional

Many bylines are date-only. When a time is present (`HH:MM` or `HH:MM:SS`,
optionally in brackets), it is parsed into the `datetime`. Timezone
abbreviations are trailing text and are not converted.

## Related

- [Web scraping](/use-cases/web-scraping)
- [Cookbook](/getting-started/cookbook)
- [Languages](/languages/)
