# History

## 1.0.5 (2025-11-25)

- Updated README and benchmark documentation with current performance guidance and references to `benchmarks/bench.py` and `PERFORMANCE_ANALYSIS.md`.
- Added explicit instructions for running the benchmark and inviting community-reported numbers.

## 1.0.2 (2022-01-27)

- Added pattern `dt:date:date_eng4_short`. It covers dates like `17-Oct-21`, commonly used in UK open data.

## 1.0.1 (2022-01-15)

- Added the `noyear` flag to the match function. When enabled, all `noyear` patterns are ignored to avoid false positives.
- Added `patterns` and `base_only` parameters for the `DateParser` `__init__` method. `patterns` accepts the list of date patterns listed in `qddate.patterns`, and `base_only` prevents generation of derived patterns from the provided base set.
- Disabled pattern `dt:date:date_7` (dates like `09.2019` without a day) because it caused too many false positives and is rare in real data.

## 0.1.1 (2018-07-20)

- Code cleanup; date patterns moved to `qddate.patterns`.

## 0.1.0 (2018-01-14)

- First public release on PyPI and GitHub.

