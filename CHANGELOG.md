# Changelog

All notable changes to this project are tracked here.

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
