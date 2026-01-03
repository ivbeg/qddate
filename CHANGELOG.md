# Changelog

All notable changes to this project are tracked here.

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
