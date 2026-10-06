# Changelog

All notable changes to this project are tracked here.

## 1.0.15 (2026-10-06)

**Deprecations**
- `DateParser(use_fingerprint=False)` is **deprecated**. The legacy
  6-level filter (`_filter_patterns_hierarchical`) is superseded by
  the fingerprint-based path that became the default in `1.0.14`.
  Constructing a parser with `use_fingerprint=False` emits a
  `DeprecationWarning`; the legacy path will be **removed in v2.0.0**.
  Omit the parameter (or pass `True`) to silence the warning.

**No user-visible API changes.**

## 1.0.14 (2026-10-06)

**Performance — single-walk fingerprint filter is now the default**
- `DateParser.__init__` accepts `use_fingerprint: bool = True` (default
  flipped from `False` in this release). When `True` (the default),
  `match()` / `match_all()` / `parse()` route through the new
  `_filter_patterns_fingerprint` — a single-walk intersection over the
  precomputed `qddate.patterns.fingerprint._PATTERN_FINGERPRINTS` index
  — instead of the 6-level `_filter_patterns_hierarchical` filter.
- The fingerprint path is **exactly equivalent** to the legacy path on
  the extended probe corpus (165 strings covering every shipped
  language, every separator, every year-format bucket, weekday + short +
  compact + edge cases). The equivalence is locked by
  `tests/test_fingerprint_parity.py`.
- Three pipeline simplifications fall out of the new path:
  1. Length filter is implicit (the index doesn't contain patterns
     with a mismatched length range at all).
  2. Charset filter is a single index walk over `<= text_char_sets`
     buckets (vs. a per-pattern loop).
  3. Separator, language, and year-format filters collapse into one
     per-dimension intersection.
- Set `DateParser(use_fingerprint=False)` to opt back into the legacy
  6-level filter; useful when debugging the matcher itself.

**No user-visible API changes.**

## 1.0.13 (2026-10-05)

**Internal — single source of truth for month names**
- New `qddate.patterns.months.MONTHS_BY_LANGUAGE` table is the canonical
  source for every supported language's month-name variants (full, lowercase,
  abbreviated, genitive where the language distinguishes case, plus a
  `detect_excludes` allow-list for cross-language collisions like Romanian
  *mai* / *august*).
- `qddate.qdparser._detect_language` now derives its per-language detection
  sets from the same table (intentionally skipping abbreviations to avoid
  false-positive language detection on shared 3-letter forms like *Jan*).
- All 14 per-language pattern modules (`base`, `bg`, `cz`, `de`, `es`, `fr`,
  `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`, `uk`) now source their `*_MONTHS`
  lists and `*_mname2mon` dicts from the table. The legacy constants are
  preserved as re-exports so existing tests and downstream consumers keep
  working unchanged.
- 72 parity tests in `tests/test_months_table.py` lock equivalence: every
  legacy `*_mname2mon` pair (across all variants) is either present in
  `MONTHS_BY_LANGUAGE` or, for the Bulgarian mixed-script legacy forms,
  maps cleanly to a canonical Cyrillic entry.

No user-visible API changes.

## 1.0.11 (2026-10-05)

**API additions**
- Added `qddate.format_date(dt, pattern_key)` and `DateMatch.format_date()` for
  locale-aware round-trip of a parsed `datetime` back to a string the parser
  accepts again. `DateParser.format_date(dt, pattern_key)` is exposed as an
  instance method.
- Added type hints on the public surface (`DateParser.__init__`, `parse`,
  `match`, `match_all`, `match_typed`, `parse_many`, `start_session`,
  `end_session`, `format_date`; `DateMatch.format_date`, `to_dict`). `mypy
  qddate/__init__.py qddate/qdparser.py` is now clean.

**Internal hardening**
- `qddate.dirty.matchPrefix` prefix-bucket lists are now derived from
  `_PATTERN_METADATA` at import time. Adding a pattern no longer requires
  editing `dirty.py` (closes bug class 4.4 from `IMPROVEMENT_PLAN.md`).
- `qddate.qdparser._DateParser__generate` is now strictly read-only against
  `ALL_PATTERNS`. The `required_chars` stamping was moved into
  `annotate_patterns()` so constructing any number of `DateParser()` instances
  leaves `ALL_PATTERNS` byte-identical (new `tests/test_pattern_immutability.py`
  regression net).
- Reachability oracle `test_every_pattern_matches_some_probe` now uses
  `match_all()` (set membership) instead of `match()` (winner only). The
  probe corpus was extended from 70 to ~150 strings, each carrying an inline
  `# basekey=…` comment. Patterns that are intentionally shadowed (rare-X
  variants that always lose to a higher-priority equivalent) live in
  `_KNOWN_SHADOWED` with one-line reasons.

**Repository hygiene**
- `benchmarks/results/` and `benchmarks/baseline_test.json` are git-ignored
  (105 regenerable benchmark outputs removed from the index).
- `requirements.txt` reduced to `-e .[dev,test,bench]` plus a header pointing
  to `pyproject.toml` as the canonical dependency declaration.
- `README.md` pattern counts updated to `1,072 generated date patterns (from
  134 base patterns)` (matching current `ALL_PATTERNS`).
- Root-level scratch files (`tests.py`, `dateparser.code-workspace`,
  `reproduce_issues.py`) removed or moved to `scripts/repro_2026_09_weekday_bug.py`.

**CI / lint**
- GitHub Actions CI: Ruff is now a gate (`ruff check qddate tests scripts`),
  refresh Python matrix `[3.10, 3.11, 3.12, 3.13, 3.14]`, coverage gate at
  `--cov-fail-under=85`, `QDDATE_PERF=1` so the new
  `tests/test_performance_smoke.py` runs on every CI invocation.
- `pyproject.toml`: `requires-python = ">=3.10"`; classifiers refreshed;
  Ruff `line-length = 120` with per-file ignores for pattern-table scripts.
- `tox.ini` envlist updated to `py310,py311,py312,py313,py314`.
- Lint baseline: 0 ruff errors (down from 355).

## 1.0.12 (2026-10-05)

**New features**
- Added `DateParser.parse_relative(text, reference=None)` that resolves
  common English and Russian relative-date phrases:
  - English: `today`, `yesterday`, `tomorrow`, `N day(s) ago`, `(in) N day(s)`
    (and the same for weeks/months/years); both digit-form and word-form
    numbers (`three days ago`).
  - Russian: `сегодня`, `вчера`, `завтра`, `N <unit> назад`, `через N <unit>`.
  - `reference` defaults to `datetime.now()`; pass an explicit value for
    deterministic tests.
- README pattern counts are now generated by
  `scripts/generate_readme_stats.py` from the canonical pattern table —
  they cannot drift again.

**Quality**
- Migrated pattern files off pyparsing 3 camelCase aliases (`oneOf`) onto
  `one_of`. `python -W error::DeprecationWarning -c "import qddate"` is
  now silent.
- Renamed `noyear=` keyword argument on `parse`/`match`/`match_all` to
  `allow_no_year=` (the old name was the opposite of the semantic
  intent). `noyear=` continues to work as a deprecated alias emitting
  `DeprecationWarning`.

## Unreleased

- Replaced the Sphinx/Read the Docs pages with a Docusaurus site in `docs/`, organized like undatum (getting started, use cases, API, languages, development) and ready for GitHub Pages.

- Added Ukrainian (`uk`) month-name and abbreviated date patterns, including genitive forms.

**Romanian language support**
- Added full and CLDR-abbreviated Romanian month-name patterns in lowercase and
  title case, including generated time and trailing-text variants.
- Added `ro` to `SUPPORTED_LANGUAGES` and the `languages=` filter, with explicit
  metadata, prefix, character-set, and automatic-detection integration.
- Kept shared `Mai` and `August` tokens ambiguous for unrestricted parsing while
  making their Romanian pattern identity deterministic under `languages="ro"`.
- Added fixture-backed regression coverage for the data.gov.ro date corpus.

**Refactor (behavior-preserving)**
- Replaced the three duplicated copies of substring-based language/separator
  inference in `qdparser.py` (`_infer_char_sets`, `_build_language_index`,
  `_build_separator_index`) with reads from a single authoritative
  `_PATTERN_METADATA` table in `qddate.patterns`. Net ~120 lines removed from
  `qdparser.py`. Adding or renaming a pattern no longer requires editing multiple
  inference sites.
- Simplified `_calculate_pattern_priority` to use the stamped `language` field
  instead of substring matching.
- `_infer_char_sets` now distinguishes numeric-only patterns (including the
  language-tagged but numerically-formatted `date_usa`/`date_usa_1`) via an
  explicit `_NUMERIC_PATTERN_KEYS` set, eliminating the old `has_month_names`
  heuristic.
- Added `tests/test_pattern_metadata.py`: safety-net tests proving the stamped
  fields reproduce the pre-refactor inference bit-for-bit (language, separator,
  and charset oracles), plus reachability tests ensuring every generated pattern
  is findable through each filter index.

**Correctness**
- Fixed `languages=` regression: automatic language detection no longer drops a
  language the caller explicitly requested. Previously, a shared month name (e.g.
  German/Dutch "Juli") could cause `DateParser(languages=["en","de"]).parse("28. Juli 2015")`
  to return `None`; it now correctly returns `2015-07-28`.
- Fixed `ENG_WEEKDAYS` typo: `"Satuday"` → `"Saturday"`, so full-weekday strings
  like `Saturday 6 May 2023` now match.
- Fixed `ENG_MONTHS_LC` typo: `"jule"` → `"july"`.
- Replaced the broken `__main__` block in `qdparser.py` (it referenced an undefined
  `r` and imported an optional dependency unguarded) with a working smoke demo.

**Testing**
- Reconciled three "should return None" tests that drifted after 1.0.7 added German
  short-month and English ordinal patterns (`14th April 2015:`, `15. Jul 2023`,
  `5. jan 2020` now asserted as valid).
- Added regression test for the `languages=` allow-list vs. auto-detection.
- Added `Saturday` full-weekday test.

**Packaging & hygiene**
- Moved `dateparser` from a hard runtime dependency to an optional `bench` extra
  (`pip install -e ".[bench]"`). The library never imported it at runtime; it is only
  used by `benchmarks/`. Runtime deps are now `pyparsing` only.
- Guarded the unguarded `import dateparser` in `benchmarks/bench.py`.
- Removed unused `dill` import and `DILL_ENABLED` flag from `qdparser.py`.
- Narrowed bare `except:` clauses to `except Exception:`.
- Removed unused `os` import from `qdparser.py`.
- Deduplicated `BASE_DATE_PATTERNS` entries (`pat:date:ddmmyyyy`, `pat:date:mmyyyy`
  were each defined twice).
- Stopped tracking build artifacts in git (`profile_results/`, root `tests.py`,
  `reproduce_issues.py`); extended `.gitignore` (`.venv-*/`, `profile_results/`).

**Documentation**
- README: corrected pattern counts (124 base → 992 generated, previously "712+ / 89"),
  added the missing Dutch language to the supported-languages list, and documented
  the `languages=` parameter with a usage example.

## 1.0.10 (2026-07-05)

**English date patterns**
- Added `dt:date:weekday_eng_abbrev3` for full weekday with abbreviated month-first dates, e.g. `Thursday, Jun 25, 2026 - 09:08`
- Registered the new pattern in prefix matching for faster candidate filtering

**Testing**
- Added test cases for weekday + abbreviated month formats with optional trailing time

## 1.0.9 (2026-07-05)

**Spanish date patterns**
- Extended `dt:date:es_base_article` and `dt:date:es_base_lc_article` to accept a comma before the year, e.g. `03 de Julio, 2026` (common on Latin American government sites)
- Updated Spanish benchmark data generator to cover comma-before-year variants

**Testing**
- Added test cases for Spanish article dates with comma before the year

## 1.0.8 (2026-01-03)

**Benchmarking Tools**
- Added `scripts/generate_webpage_test_data.py` for generating test data from real-world webpages
  - Fetches HTML content from government and international organization websites
  - Extracts text snippets and tests them with qddate's match() method
  - Generates CSV files with text snippets and pattern matches for benchmarking
- Added `benchmarks/benchmark_webpage_data.py` for comparing qddate with other libraries using webpage data
  - Benchmarks qddate against dateparser and dateutil using real-world text snippets
  - Measures success rates and performance metrics
  - Outputs results in JSON and text formats
- Updated README with documentation for new benchmark tools

## 1.0.7 (2026-01-01)

**Language Coverage - Phase 1 Enhancements**
- **CRITICAL**: Completed Czech language patterns (was broken with 0 patterns)
  - Added 4 patterns with genitive month support similar to Polish
  - Czech dates like "15 Leden 2015", "5 ledna 2020" now supported
  - Fixed "Incomplete" status - Czech is now fully functional
- **Enhanced German** patterns from 2 to 8 (+6 patterns)
  - Added weekday patterns: "Montag, 28. Juli 2015"
  - Added abbreviated months: "15. Jul 2023", "5. jan 2020"
  - Added rare month-first formats
- **Enhanced English** patterns (+6 patterns)
  - Added abbreviated month support: "24 Jul 2015", "Jan 15, 2020"
  - Added weekday with abbreviations: "Fri, 24 Jul 2015"
  - Added ordinal suffix patterns: "8th Jul 2015"

**Testing**
- Added 16 new test cases covering all new patterns
- 4 Czech tests, 6 German tests, 6 English abbreviation tests
- All tests passing

**Pattern Count**: 16 new patterns added (Czech: 4, German: 6, English: 6)

## 1.0.6 (2026-01-01)

**Infrastructure**
- Migrated CI/CD from Travis CI to GitHub Actions with Python 3.8-3.12 matrix testing
- Modernized `pyproject.toml` to PEP 621 standard with optional dependencies
- Added Ruff linter configuration for code quality

**Performance**
- **Critical**: Eliminated expensive list copying in `matchPrefix()` hot path (~15-25% faster)
- Pre-computed combined basekey lists to avoid runtime allocations
- All Phase 1 optimizations from `PERFORMANCE_ANALYSIS.md` now implemented

**Robustness**
- Fixed missing Turkish and Polish pattern keys in prefix matching
- Added support for comma-separated dates: `7 August, 2015`
- Added `dt:date:weekday_eng_mixed` pattern for `Wednesday 22 Apr 2015` format
- Updated `dt:date:date_eng1` to allow optional comma after month

**Testing**
- Added 3 new test cases for previously unsupported date formats
- All 69 tests passing

## 1.0.5 (2025-11-25)
- Updated README and benchmark documentation with current performance guidance and references to `benchmarks/bench.py` and `PERFORMANCE_ANALYSIS.md`.
- Added explicit instructions for running the benchmark and inviting community-reported numbers.

## 1.0.2 (2022-01-27)
- Added pattern `dt:date:date_eng4_short` to cover `17-Oct-21` style dates common in UK open data.

## 1.0.1 (2022-01-15)
- Added the `noyear` flag to the `match` function to disable patterns without year data.
- Added `patterns` and `base_only` parameters to `DateParser.__init__` to make pattern selection configurable.
- Disabled pattern `dt:date:date_7` (dates like `09.2019`) due to excessive false positives.

## 0.1.1 (2018-07-20)
- Code cleanup and moved date patterns into `qddate.patterns`.

## 0.1.0 (2018-01-14)
- First public release on PyPI and GitHub.
