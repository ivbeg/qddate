# qddate

> Quick and dirty date parsing for scraped HTML.

A Python 3 library focused on parsing date strings extracted from messy HTML pages
as fast as possible. Born out of long-term news aggregation work: fewer abstractions,
lots of hard-coded optimizations, and enough language coverage to process millions of
strings at scale. It is intentionally pragmatic and prioritizes speed over breadth.

## Scope

**In scope**

- Parsing left-aligned dates with optional trailing text from scraped HTML.
- Numeric and month-name date formats across a fixed set of languages.
- Optional time-of-day suffixes (`HH:MM`, `HH:MM:SS`).
- Multi-stage candidate filtering for high throughput on large corpora.
- Configurable language subsets via the `languages=` parameter.

**Out of scope (today)**

- Relative date parsing ("yesterday", "2 days ago").
- Calendar / timezone-aware scheduling semantics.
- General natural-language date extraction from arbitrary prose.

These out-of-scope items are revisited as proposed changes under `openspec/changes/`.

## Guiding principles

1. **Speed first.** Patterns are pre-generated pyparsing grammars; runtime does no
   disk I/O and avoids regular expressions in the hot path.
2. **Minimal dependencies.** The runtime depends on `pyparsing` only. Other date
   libraries are benchmark-only.
3. **Left-aligned, dirty matching.** Strings like `12.03.1999 some text here` must
   parse; trailing noise is suppressed.
4. **Stable public API.** `qddate.DateParser` and its `parse`/`match` methods are
   the supported surface. Internal helpers may change.

## Current capabilities (at a glance)

- 124 base patterns → 992 generated patterns (numeric + time variants).
- 12 languages: bg, cz, de, en, es, fr, it, nl, pl, pt, ru, tr.
- See `openspec/specs/` for the authoritative behavioral specification.

## Specification pointers

- **Current behavior:** `openspec/specs/`
- **Proposed changes:** `openspec/changes/`
- **Source review & rationale:** `IMPROVEMENT_PLAN.md` (root of repo)
