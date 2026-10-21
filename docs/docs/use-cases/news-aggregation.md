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

Many bylines are date-only. When a time is present (`HH:MM`, `HH:MM:SS`,
`14h30`, `3:45 PM`, before or after the date), it is parsed into the
`datetime`. `match_typed()` tells the two apart: `precision` is `"day"` for a
date-only byline, and `tzinfo` carries a zone written after the time
(`12:30 МСК`, `10:00 BST`, `+03:00`).

One parser can serve every site: pass the page language as a hint and the
site's day/month order per call.

```python
parser = qddate.DateParser()
m = parser.match_typed(text, languages=page_lang, date_order="MDY",
                       reference=fetched_at, prefer="past")
```

## Related

- [Web scraping](/use-cases/web-scraping)
- [Cookbook](/getting-started/cookbook)
- [Languages](/languages/)
