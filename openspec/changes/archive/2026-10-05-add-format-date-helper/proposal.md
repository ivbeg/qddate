# OpenSpec Change: Add format_date helper for round-trip normalization

`DateParser` already knows the `format` string every matched pattern carries
(strftime/strptime codes). Today callers who want to convert a parsed
`datetime` back into a normalized string have to inspect `DateMatch.format` by
hand and call `datetime.strftime(format)`. This change exposes a single helper
that does the round-trip, both as a standalone function and as a method on
`DateMatch` for symmetry.

## Why

`DateParser` is the only fast, multi-lingual HTML date parser in the Python
ecosystem. Once a value is parsed, the natural next step for many callers is
to **normalize** the result back into a canonical ISO string for downstream
storage — `parsed.dt.isoformat()` works for date-only inputs but throws away
the locale information, while calling `datetime.strftime(match.format)` by hand
requires every caller to know about the `format` attribute and to handle the
"long tail" formats (weekday prefixes, comma spacers, year-short tokens, etc.).

Exposing `format_date()` on both `DateParser` and `DateMatch` keeps the
locale knowledge inside `qddate` and gives callers a one-line round-trip.

## What changes

**Standalone `format_date(dt, pattern_key=…)`**
- New: `qddate.qdparser.format_date(dt, pattern_key)` returns a string built
  from `dt` using the format attached to `pattern_key` in `ALL_PATTERNS`.
- Reason: Single source of truth for "given this datetime and pattern key,
  what string would the parser have recognised?"
- Impact: Non-breaking, additive.

**`DateParser.format_date(dt, pattern_key=…)`**
- New: instance method that calls the standalone function.
- Reason: Most callers already hold a parser instance.
- Impact: Non-breaking, additive.

**`DateMatch.format_date()`**
- New: instance method using `self.format` and `self.datetime`.
- Reason: Symmetric with `match.datetime`, `match.language`, `match.pattern_key`.
- Impact: Non-breaking, additive.

**`pattern_key` validation**
- The helper raises `ValueError` for an unknown `pattern_key`, with a helpful
  message naming the candidate.
- Reason: Prevents silent fallbacks to ISO format.
- Impact: Non-breaking.

**Round-trip semantics**
- `format_date(parse(text).datetime, pattern_key=parse(text).pattern.match_key)`
  must return a string that `parse()` will accept again and resolve to the same
  pattern (and the same datetime within the same calendar year).
- Reason: The whole point of the helper.
- Impact: Test-only requirement.

## Out of scope

- Locale-aware month-name output (already covered by `format` codes; the
  helper is just a `strftime` wrapper).
- Custom format strings — only `ALL_PATTERNS`-registered pattern keys.
- Side-effects on the original `datetime` (the helper returns a new string).

## Impact

- **Breaking?** No. Pure additive change; no existing method signatures move.
- **Affected:** Callers who want locale-aware round-trip; the docs (a new
  `docs/docs/api/format-date.md` page or section).
- **Risk:** The `format` strings in `ALL_PATTERNS` are tuned for parsing, not
  emitting (e.g. `date_rus3` uses `%d.%m.%Y` which round-trips fine). If a
  pattern's `format` includes literal text (e.g. commas or weekday names) the
  helper will reproduce it; this is desired.
- **Rollback:** Drop the new methods; nothing else depends on them.