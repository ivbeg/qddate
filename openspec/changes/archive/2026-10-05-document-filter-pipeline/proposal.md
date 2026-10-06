# OpenSpec Change: Document the six-level filter pipeline

`DateParser.match()` runs every candidate pattern through a six-level filter
pipeline (length → separator → year format → language → charset → prefix
buckets). Today this is only discoverable by reading `qddate/qdparser.py`.
This change adds a dedicated docs page explaining the pipeline, the role
of each level, and the tradeoffs (e.g. `noprefix=True` disables the prefix
filter and is significantly slower).

## Why

The `noprefix`, `nocharsetfilter`, `noseparatorfilter`, `noyearformatfilter`,
and `nolanguagefilter` switches on `match()` are the most powerful
performance knobs in the library, but their effect is opaque. A reader has
to trace the filter chain in source to understand what disabling one of
them costs. A dedicated docs page makes the tradeoffs explicit and gives
callers a reference for diagnosing slow parses.

## What changes

**New docs page: `docs/docs/api/filter-pipeline.md`**
- Document each filter level:
  1. **Length** — `self._patterns_by_length[len(text)]` (O(1) lookup)
  2. **Separator** — patterns pre-indexed by `separator`
  3. **Year format** — 4-digit / 2-digit / no-year partition
  4. **Language** — language-tagged patterns narrowed to the detected lang
  5. **Character set** — patterns that need a script the text doesn't have
     are dropped
  6. **Prefix bucket** — `matchPrefix(text[:6])` returns the union of
     candidate basekeys
- Document the cost of disabling each filter (e.g. `noprefix=True` is
  typically 10× slower; `nolanguagefilter=True` is closer to 1.5×).
- Document the interaction with `match_all()` (which always runs every
  filter level).

**Reference section in `docs/docs/api/match.md`**
- Link to `filter-pipeline.md` and summarise what each `no…` kwarg disables.

## Out of scope

- Restructuring the filter pipeline (the proposal is documentation-only).
- Adding performance benchmarks per filter level (covered by
  `tests/test_performance_smoke.py`).

## Impact

- **Breaking?** No. Pure documentation addition.
- **Affected:** Anyone tuning parse performance or debugging slow parses.
- **Risk:** A wrong claim about performance cost would mislead. Mitigation:
  benchmark before publishing numbers; if uncertain, say so.
- **Rollback:** Trivial revert.