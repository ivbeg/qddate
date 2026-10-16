# OpenSpec Change: Modernize API surface

Ergonomic improvements to the public API without removing existing methods: a typed
result object, a bulk parsing entry point, and snake_case aliases for the two
camelCase session methods. From `IMPROVEMENT_PLAN.md` §4.8, §7.4, §7.5.

## Why

- `match()` returns `{"values": ParseResults, "pattern": dict}`, forcing the caller
  to iterate `values` and `int()` each component by hand. This is awkward and
  error-prone, and blocks adding future result fields (timezone, confidence) cleanly.
- The library is positioned for "millions of strings at scale" but offers only a
  single-string `parse()`, re-running the full filter pipeline per call.
- `startSession()` / `endSession()` are the only camelCase names in the API,
  violating PEP 8 and the rest of the surface.

## What changes

**Typed `DateMatch` result object**
- From: `match()` returns a bare dict `{"values": ..., "pattern": ...}`; callers must
  hand-convert components.
- To: `match()` returns a `DateMatch` dataclass exposing `.datetime` (already
  constructed), `.pattern_key`, `.language`, `.format`, and `.raw`. A `.to_dict()`
  method preserves the old shape for backward compatibility.
- Reason: Ergonomics; future-proofing for tz/confidence fields.
- Impact: **Breaking if switched naively.** Therefore: `match()` keeps returning the
  dict shape by default; a new `match_typed()` (or a `typed=True` flag) returns
  `DateMatch`. The dict shape is deprecated but not removed in 1.x. See Open question.

**Bulk `parse_many` API**
- From: Only single-string `parse()` exists; per-call filter setup is repeated.
- To: A generator/method `parse_many(iterable)` that reuses the length/charset
  indexes and amortizes filter overhead across many inputs.
- Reason: The library's stated use case is high-throughput scraping.
- Impact: Non-breaking (additive).

**snake_case session aliases**
- From: `startSession()` / `endSession()` (camelCase).
- To: `start_session()` / `end_session()` aliases; the camelCase names remain as
  deprecated aliases.
- Reason: PEP 8 consistency.
- Impact: Non-breaking (aliases only).

## Impact

- **Breaking?** No, if `DateMatch` is gated behind a flag/new method (recommended).
  The snake_case aliases and `parse_many` are purely additive.
- **Affected:** All callers gain ergonomics; no existing call site breaks.
- **Rollback:** Additive features removed; aliases removed.

## Open questions

- **`DateMatch` rollout.** Options: (a) new `match_typed()` method, (b) `typed=True`
  flag on `match()`, (c) flip `match()` and provide legacy dict via a compatibility
  shim. Recommend (a) for 1.x — zero breakage — and (c) for 2.0. To be confirmed with
  the maintainer before implementation.
