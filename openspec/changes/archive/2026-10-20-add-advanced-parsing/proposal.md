# OpenSpec Change: Add advanced parsing (relative dates, ambiguity, docs)

The largest, most forward-looking change set. Closes the biggest feature gaps vs.
`dateparser` and improves the filtering-pipeline story. From `IMPROVEMENT_PLAN.md`
§7.3, §7.6, §7.7, §8, §6.3. Each sub-item is independently archivable and should
likely be split into its own change folder at implementation time; they are grouped
here as a thematic roadmap.

## Why

- **Relative dates** ("yesterday", "2 days ago", "today") are extremely common in
  scraped HTML and are explicitly listed as a *limitation* in the README — the very
  library qddate is positioned against (`dateparser`) handles them. This is the
  single biggest feature gap.
- **Ambiguity is silently resolved.** Today the first matching pattern wins, so
  `01/02/2020` parses as D/M/Y or M/D/Y depending on pattern priority order, with no
  signal to the caller. For scraping, surfacing ambiguity is valuable.
- **The filtering pipeline is undocumented** and the docs lag the code (README stats,
  divergent signatures). There is no CONTRIBUTING guide for adding languages.

## What changes

**Relative date parsing (opt-in, locale-aware)**
- From: Relative expressions are unsupported (README lists this as a limitation).
- To: A relative-date module, gated behind `DateParser(relative=True)` or a separate
  `parse_relative()` function, resolves expressions like "yesterday", "today",
  "N days/hours ago" against a reference time (default: now). Locale-aware via the
  existing language tables.
- Reason: Closes the headline feature gap; common in scraped timestamps.
- Impact: Non-breaking (opt-in). Adds a new capability.

**Ambiguity / multi-match reporting**
- From: `match()` returns the first matching pattern; alternates are invisible.
- To: A `match_all()` (or `match(ambiguous=True)`) returns *all* matching patterns
  ranked by `_calculate_pattern_priority`, letting the caller see that a date is
  ambiguous and decide.
- Reason: Scraping consumers often need to know when a date is ambiguous (e.g. D/M vs
  M/D) rather than silently getting one interpretation.
- Impact: Non-breaking (additive new method/flag).

**Formatting / round-trip helper**
- From: Every pattern carries a `format` string but it is not exposed to callers.
- To: A `format_date(date, pattern_key=...)` helper (or a method on `DateMatch`)
  normalizes a `datetime` to a canonical representation using a pattern's format.
- Reason: Useful for normalizing scraped dates to one canonical form.
- Impact: Non-breaking (additive).

**Documentation & DX pass**
- From: README stats are stale; filtering pipeline undocumented; no "add a language"
  guide; many public methods lack accurate docstrings; no type hints on the public API.
- To: Fix stats, document the 6-level filtering pipeline, add a CONTRIBUTING section
  on adding languages (trivial after Change 3), add type hints, generate API docs.
- Reason: Contributor onboarding and user trust.
- Impact: Non-breaking. Docs/tooling only.

**Single compiled matcher (optional, long-term)**
- From: Six filter levels stitched with temporary list comprehensions and set
  round-trips.
- To: Each pattern carries a cheap `fingerprint`; candidate selection becomes a set
  intersection over precomputed frozensets.
- Reason: Less code, fewer allocations, easier to reason about.
- Impact: Non-breaking (internal). May be its own change; listed here as the
  long-term architectural target.

## Impact

- **Breaking?** No. All feature additions are opt-in/additive.
- **Affected:** Users wanting relative dates or ambiguity signals; contributors
  (docs/type hints).
- **Rollback:** Each sub-feature is independently removable.

## Open questions

- **Relative-date scope.** Full natural-language ("last Tuesday") vs. the common
  subset ("today/yesterday/N days ago")? Recommend shipping the subset first.
- **`match_all` shape.** Return a list of `DateMatch`, or a single `DateMatch` plus
  an `alternatives` field? Recommend list-of-`DateMatch` for simplicity.
- **Splitting.** Should this folder become 4–5 separate change folders at
  implementation? Recommend yes (relative, ambiguity, format helper, docs, matcher).

> **Note:** This change is intentionally a thematic roadmap rather than a single
> implementation unit. At implementation time it should be split into one change
> folder per bullet so each can be proposed, reviewed, and archived independently,
> per OpenSpec conventions.
