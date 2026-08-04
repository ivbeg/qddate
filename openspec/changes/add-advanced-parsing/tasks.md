# Tasks: Add advanced parsing

> These tasks are grouped thematically. At implementation time, split into separate
> change folders (relative-dates, ambiguity-reporting, format-helper, docs-dx,
> compiled-matcher) and archive each independently.

## Relative dates (new capability)

- [ ] Decide scope: ship "today / yesterday / tomorrow / N days ago / N hours ago"
      first; defer "last Tuesday"-style until later.
- [ ] Add a relative module gated behind `DateParser(relative=True)` or a standalone
      `parse_relative(text, now=None)`.
- [ ] Locale tables: reuse existing language tables for "today/yesterday" words.
- [ ] Tests: each supported expression resolves correctly against a fixed `now`;
      unsupported expressions return `None` without falling through to date parsing.

## Ambiguity / multi-match

- [ ] Add `match_all(text, ...)` returning a list of all matching patterns ranked by
      `_calculate_pattern_priority`.
- [ ] Tests: `01/02/2020` returns both D/M/Y and M/D/Y candidates; ranking is stable;
      unambiguous dates return a single-element list.

## Format helper

- [ ] Expose `format_date(date, pattern_key=...)` and/or a `DateMatch.format()`.
- [ ] Tests: round-trip `parse` → `format_date` reproduces the canonical string for a
      representative set of patterns.

## Docs & DX

- [ ] Fix README stats (coordinate with Change 2).
- [ ] Document the 6-level filtering pipeline (length → charset → separator →
      language → year-format → prefix).
- [ ] Add CONTRIBUTING section "How to add a new language" (trivial after Change 3).
- [ ] Add type hints to the public API (`parse`, `match`, `__init__`).
- [ ] Audit docstrings for signature drift; ensure Read the Docs builds.

## Compiled matcher (long-term)

- [ ] Prototype a `fingerprint`-based candidate selection (length-range, charset,
      separator, language, year-format).
- [ ] Differential test: candidate sets identical to current pipeline.
- [ ] Benchmark: no regression vs. current pipeline; ideally faster.

## Verification

- [ ] `pytest -q` green; new feature tests pass.
- [ ] No existing call site breaks (all additions opt-in/additive).
