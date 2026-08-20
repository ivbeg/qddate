---
title: "When to use qddate"
description: "qddate vs dateparser vs dateutil"
---
# When to use qddate vs dateparser vs dateutil

Evaluators often ask which Python date parser to reach for. Short answer:
**qddate is a speed-first pattern matcher for scraped HTML bylines**. Use the
others when you want broader natural-language coverage or calendar math.

| Need | Prefer |
|------|--------|
| Extract dates from messy HTML at scale (`12.03.1999 some text here`) | **qddate** |
| Parse almost any human-readable date in any language, including relative phrases | **dateparser** |
| Standard English / ISO / RFC strings, plus `rrule` and `relativedelta` | **dateutil** |
| Chatbots, search bars, unconstrained user input | **dateparser** |
| Recurrence rules and date arithmetic | **dateutil** |
| Minimal runtime dependencies (`pyparsing` only) | **qddate** |

## qddate strengths

- Speed: pre-generated pyparsing grammars, length/prefix/charset filters, no disk I/O at runtime
- Dirty matching: left-aligned dates with trailing text are first-class
- Determinism: if a pattern is in the catalog, it matches; if it is not, it fails
- Light footprint: runtime depends on `pyparsing` only

## When another library wins

- **dateparser**: relative dates ("yesterday", "in 2 weeks"), ~200 locales, "it just works" user input
- **dateutil**: battle-tested tokenizer for standard formats, `rrule`, `relativedelta`, calendar apps

## Architectural snapshot

| Feature | `dateutil` | `dateparser` | `qddate` |
|---------|------------|--------------|----------|
| Primary goal | Robust extensions to `datetime` | Universal coverage | High-throughput HTML dates |
| Approach | Lexer + heuristics | Locale translation + heuristics | Pattern matching + pre-filtering |
| Language support | English + custom `parserinfo` | ~200 locales | 14 languages, manual patterns |
| Relative dates | No (math via `relativedelta`) | Yes | No |
| Dependencies | Light | Heavy | Light (`pyparsing`) |
| Best for | Standard apps, calendars | User input, chatbots | Web scraping, bulk corpora |

## Related docs

- [Quick start](/getting-started/quick-start)
- [Performance](/getting-started/performance)
- [Languages](/languages/)
- [Best practices](/getting-started/best-practices)
