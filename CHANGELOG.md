# Changelog

All notable changes to this project are tracked here. Older entries are adapted from `HISTORY.rst`.

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
