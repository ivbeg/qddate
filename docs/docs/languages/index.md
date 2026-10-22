---
title: "Languages and patterns"
description: "Fifteen languages, base patterns, and generated time variants"
---
# Languages and patterns

qddate ships a fixed set of languages. Coverage grows when someone adds a
pattern table and tests — not by loading CLDR at runtime.

## Supported languages

| Code | Language | Notes |
|------|----------|-------|
| `en` | English | Numeric cores, US `mm/dd`, weekdays, abbreviated months, dates without a year (`May 5`, `5 May`), `Sept. 5, 2022`, `Sep 5th 2022`, `5-May-2022` |
| `de` | German | Full, short, weekday, month-first |
| `ru` | Russian | Nominative/genitive months, optional `г.` / `года` |
| `es` | Spanish | Articles (`de`), comma-year (`03 de Julio, 2026`) |
| `fr` | French | Month names with accents |
| `it` | Italian | Month names, weekdays |
| `nl` | Dutch | Full and short months, weekdays |
| `pt` | Portuguese | Articles |
| `pl` | Polish | Nominative and genitive, optional dot after the day |
| `cz` | Czech | Nominative and genitive, day with a dot (`5. května 2022`) |
| `bg` | Bulgarian | Cyrillic month names |
| `tr` | Turkish | Month names, optional suffixes |
| `ro` | Romanian | Full and CLDR-abbreviated months |
| `uk` | Ukrainian | Nominative, genitive, abbreviated |
| `sk` | Slovak | Nominative and genitive, day with a dot (`5. mája 2022`) |

Language-neutral numeric patterns (ISO-like `YYYY-MM-DD`, `dd.mm.yyyy`, compact
digits, and the Chinese, Japanese and Korean `2022年5月5日` / `2022년 5월 5일`)
live with the English table but are available regardless of month-name
language. Their `DateMatch.language` is `None`.

## How many patterns?

The catalog is **base patterns × generated variants** (151 base patterns in the current tree). Each base date pattern can expand with a time after it (`HH:MM` or `14h30`, `HH:MM:SS`, `[HH:MM]`, the 12-hour clock), a time before it, and trailing-text forms. Counts on each language page are **base** patterns from `qddate/patterns/*.py`. Generated variants are produced at `DateParser` construction when `generate=True`.

Regenerate the per-language tables after pattern changes:

```bash
python scripts/generate_pattern_docs.py
```

## Pattern flags

- **Year Short**: 2-digit years (`24` → 2024-style handling in that pattern)
- **No Year**: day-month only; `parse()` fills the year of `reference=` (the current year by default)
- **Filter**: stricter prefix/length filtering (higher means more aggressive)

Format strings use `strftime`-style tokens (`%d`, `%m`, `%Y`, `%y`, `%b`). Length
min/max bound which strings a pattern is even tried against.

## Pages

Pick a language in the sidebar, or start with [English](/languages/en) (numeric
cores) and [Russian](/languages/ru) / [German](/languages/de) for month-name
examples.
