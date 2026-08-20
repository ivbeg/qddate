---
title: "Languages and patterns"
description: "Fourteen languages, base patterns, and generated time variants"
---
# Languages and patterns

qddate ships a fixed set of languages. Coverage grows when someone adds a
pattern table and tests — not by loading CLDR at runtime.

## Supported languages

| Code | Language | Notes |
|------|----------|-------|
| `en` | English | Numeric cores, US `mm/dd`, weekdays, abbreviated months |
| `de` | German | Full, short, weekday, month-first |
| `ru` | Russian | Nominative/genitive months, optional `г.` / `года` |
| `es` | Spanish | Articles (`de`), comma-year (`03 de Julio, 2026`) |
| `fr` | French | Month names with accents |
| `it` | Italian | Month names, weekdays |
| `nl` | Dutch | Full and short months, weekdays |
| `pt` | Portuguese | Articles |
| `pl` | Polish | Nominative and genitive |
| `cz` | Czech | Nominative and genitive |
| `bg` | Bulgarian | Cyrillic month names |
| `tr` | Turkish | Month names, optional suffixes |
| `ro` | Romanian | Full and CLDR-abbreviated months |
| `uk` | Ukrainian | Nominative, genitive, abbreviated |

Language-neutral numeric patterns (ISO-like `YYYY-MM-DD`, `dd.mm.yyyy`, compact
digits) live with the English table but are available regardless of month-name
language.

## How many patterns?

The catalog is **base patterns × generated variants** (134 base patterns in the current tree). Each base date pattern can expand with `HH:MM`, `HH:MM:SS`, and trailing-text forms. Counts on each language page are **base** patterns from `qddate/patterns/*.py`. Generated variants are produced at `DateParser` construction when `generate=True`.

Regenerate the per-language tables after pattern changes:

```bash
python scripts/generate_pattern_docs.py
```

## Pattern flags

- **Year Short**: 2-digit years (`24` → 2024-style handling in that pattern)
- **No Year**: day-month only; `parse()` fills the current year
- **Filter**: stricter prefix/length filtering (higher means more aggressive)

Format strings use `strftime`-style tokens (`%d`, `%m`, `%Y`, `%y`, `%b`). Length
min/max bound which strings a pattern is even tried against.

## Pages

Pick a language in the sidebar, or start with [English](/languages/en) (numeric
cores) and [Russian](/languages/ru) / [German](/languages/de) for month-name
examples.
