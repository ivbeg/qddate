# Tasks: Refactor pattern metadata

> Status: **IMPLEMENTED** on branch `openspec/stabilize-and-cleanup`.
> Behavior-preserving (no delta spec). Verified by a differential/oracle test suite.

## Add metadata fields

- [x] Add `language` field to every pattern (use `None` for language-neutral numeric
      patterns like `date_1`, `date_iso8601`).
- [x] Add `separator` field (`slash`/`dot`/`dash`/`space`/`none`/`mixed`) to every
      pattern.
- [x] Implementation note: fields live in a single authoritative
      `_PATTERN_METADATA` table in `patterns/__init__.py` (one source of truth),
      stamped onto each pattern at import via `annotate_patterns()`, rather than
      scattered across 13 pattern files. Every pattern has both fields (verified).

## Replace inference

- [x] Rewrite `_infer_char_sets` to read language via `_pattern_language()`; numeric
      patterns resolved via `_NUMERIC_PATTERN_KEYS` (covers the `date_usa` special
      case where language=en but format is numeric).
- [x] Rewrite `_build_language_index` to group by `_pattern_language(p)`.
- [x] Rewrite `_build_separator_index` to group by `_pattern_separator(p)`.
- [x] Simplify `_calculate_pattern_priority` to use `_pattern_language()` for the
      language boosts (identity-based `date_N` checks left intact — not inference).
- [x] Deleted all three dead substring-inference ladders (~120 lines removed).

## Centralize month/weekday tables

- [ ] **Deferred.** The `month_table()` helper is independent of this refactor and
      can ship separately. The `Satuday`/`jule` typo fixes (Change 1) already
      address the immediate bugs; this task makes the *class* of typo impossible
      but is not required for the metadata refactor to land.

## Differential & coverage tests (`tests/test_pattern_metadata.py`)

- [x] `test_every_pattern_has_metadata_fields` — every pattern carries both fields.
- [x] `test_metadata_table_covers_every_pattern` — table has exactly the right keys.
- [x] `test_stamped_language_matches_legacy_inference` — language oracle.
- [x] `test_stamped_separator_matches_legacy_inference` — separator oracle.
- [x] `test_infer_char_sets_matches_legacy_output` — charset oracle (incl. date_usa).
- [x] Reachability tests: every pattern findable through length / language / separator
      indices.

## Verification

- [x] `pytest tests/test_dateparser.py tests/test_pattern_metadata.py` → 132 passed.
- [x] Multi-language parity sweep: identical parse results vs. pristine master on a
      37-case cross-language corpus.
- [x] Perf parity: 7512 µs/parse (branch) vs. 7235 µs/parse (master) — within noise;
      no measurable regression from the field reads.
