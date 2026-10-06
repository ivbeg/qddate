# Tasks

## 1. Design

- [x] Read IMPROVEMENT_PLAN.md §6.3 and current `_filter_patterns_hierarchical`
- [x] Audit all six current filter buckets (`_patterns_by_length`,
      `_patterns_by_separator`, `_patterns_by_language`,
      `_patterns_by_year_format`, `_patterns_by_charset` (currently inline),
      `_matchPrefix`)
- [x] Decide fingerprint tuple shape: `(length_min, length_max, required_chars, separator, language, year_format)`
- [x] Decide which dimensions get their own bucket vs union inside the projection
- [x] Decide boundary for "language=any" (multi-language month-name patterns)

## 2. Implementation: `qddate/patterns/fingerprint.py`

- [ ] Define `FingerprintKey` namedtuple
- [ ] Define `compute_pattern_fingerprint(pattern)` — pure function over a
      pattern dict, returns the tuple
- [ ] Define `_PATTERN_FINGERPRINTS: dict[FingerprintKey, frozenset[str]]`
      built once at import time from `ALL_PATTERNS`
- [ ] Define `intersect_fingerprints(text_fingerprint, allowed_chars) -> set[str]`
      helper that yields the candidate pattern keys
- [ ] Re-export `FingerprintKey`, `compute_pattern_fingerprint`,
      `_PATTERN_FINGERPRINTS`, `intersect_fingerprints` from
      `qddate.patterns` (top-level convenience)

## 3. Wire into `qdparser`

- [ ] Add `fingerprint` field to each pattern dict in `annotate_patterns()`
      (read-only; same discipline as `required_chars`)
- [ ] No change to `_filter_patterns_hierarchical` in this round

## 4. Tests

- [ ] `tests/test_fingerprint_index.py` — parity with `ALL_PATTERNS`
- [ ] `tests/test_fingerprint_index.py` — projection: every legacy bucket
      (`_patterns_by_length`, `_patterns_by_separator`, etc.) is reconstructible
      from the fingerprint index
- [ ] `tests/test_fingerprint_index.py` — `compute_pattern_fingerprint` is
      deterministic (calling twice yields equal tuples)
- [ ] `tests/test_fingerprint_index.py` — `intersect_fingerprints` returns a
      superset-or-equal of the current pipeline's candidate set for a handful
      of canonical inputs

## 5. Documentation

- [ ] Module-level docstring on `qddate/patterns/fingerprint.py` explaining
      the index layout and the relationship to the legacy buckets
- [ ] Short note in `IMPROVEMENT_PLAN.md` §6.3 marking the data layer as
      shipped, the consumer wiring as "future round"

## 6. Verification

- [ ] `pytest tests/ --cov=qddate --cov-fail-under=85 -q` — 345 existing
      tests pass + new tests pass; coverage ≥ 85%
- [ ] `ruff check qddate tests scripts openspec` — clean
- [ ] `mypy qddate/__init__.py qddate/qdparser.py` — clean
- [ ] `qddate.__version__` unchanged (this round is data-layer-only)

## 7. Archive

- [ ] `openspec validate fingerprint-based-matcher`
- [ ] `openspec archive fingerprint-based-matcher -y`