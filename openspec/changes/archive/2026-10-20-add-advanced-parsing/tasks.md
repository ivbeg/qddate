# Tasks: Add advanced parsing

> Archived 2026-10-20 after verification against the code. Shipped in 1.0.11–1.0.14 as separate changes (relative dates, `match_all`, `format_date`, filter-pipeline docs, fingerprint matcher). Relative parsing is the standalone `parse_relative(text, reference=None)`; `parse()` does not match relative phrases and there is no `relative=True` switch.


> These tasks are grouped thematically. At implementation time, split into separate
> change folders (relative-dates, ambiguity-reporting, format-helper, docs-dx,
> compiled-matcher) and archive each independently.

## Relative dates (new capability)

- [x] Decide scope: ship "today / yesterday / tomorrow / N days ago / N hours ago"
      first; defer "last Tuesday"-style until later.
- [x] Add a relative module gated behind `DateParser(relative=True)` or a standalone
      `parse_relative(text, now=None)`.
- [ ] Locale tables: reuse existing language tables for "today/yesterday" words.
  - Not done: `qddate/relative.py` keeps its own English/Russian word tables.
- [x] Tests: each supported expression resolves correctly against a fixed `now`;
      unsupported expressions return `None` without falling through to date parsing.

## Ambiguity / multi-match

- [x] Add `match_all(text, ...)` returning a list of all matching patterns ranked by
      `_calculate_pattern_priority`.
- [x] Tests: `01/02/2020` returns both D/M/Y and M/D/Y candidates; ranking is stable;
      unambiguous dates return a single-element list.

## Format helper

- [x] Expose `format_date(date, pattern_key=...)` and/or a `DateMatch.format()`.
- [x] Tests: round-trip `parse` → `format_date` reproduces the canonical string for a
      representative set of patterns.

## Docs & DX

- [x] Fix README stats (coordinate with Change 2).
- [x] Document the 6-level filtering pipeline (length → charset → separator →
      language → year-format → prefix).
- [x] Add CONTRIBUTING section "How to add a new language" (trivial after Change 3).
- [x] Add type hints to the public API (`parse`, `match`, `__init__`).
- [x] Audit docstrings for signature drift; ensure Read the Docs builds.

## Compiled matcher (long-term)

- [x] Prototype a `fingerprint`-based candidate selection (length-range, charset,
      separator, language, year-format).
- [x] Differential test: candidate sets identical to current pipeline.
- [x] Benchmark: no regression vs. current pipeline; ideally faster.

## Verification

- [x] `pytest -q` green; new feature tests pass.
- [x] No existing call site breaks (all additions opt-in/additive).
