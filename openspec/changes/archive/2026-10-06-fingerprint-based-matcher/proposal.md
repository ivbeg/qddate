# Fingerprint-based matcher (single intersection)

## Why

`_filter_patterns_hierarchical()` in `qddate/qdparser.py` runs **six independent
filter passes** in sequence (length → charset → separator → language → year
format → prefix). Each pass builds its own per-instance index (`_patterns_by_length`,
`_patterns_by_separator`, …) and iterates the candidate list with its own
custom merge rules. The behaviour is correct but the implementation is
spread across ~200 lines of branching, the per-index dicts are constructed
twice (once per `DateParser` instance), and one-off "space-compat" /
"year-bucket merge" exceptions live inside the hot path.

A **fingerprint** is the natural unification: for every pattern, precompute
the tuple `(length_range, required_chars, separator, language, year_format)`
once at import time and look up patterns by intersecting precomputed
frozensets at call time. Result: one obvious place to audit filtering
behaviour, ~200 fewer lines, and the same test corpus (345 today) can lock
equivalence.

This change ships the **infrastructure** for round 6.3:

1. A new module `qddate/patterns/fingerprint.py` exposing the
   `PatternFingerprint` dataclass and the canonical
   `_PATTERN_FINGERPRINTS: dict[str, frozenset[str]]` indexed by fingerprint
   tuple.
2. Test coverage asserting the new module exposes the same data as the
   existing per-instance buckets.
3. **No behaviour change** to `match()` / `match_all()` / `parse()` in this
   round. The existing 6-level pipeline keeps running unchanged. A future
   round wires the intersection into the hot path with the existing pipeline
   as the parity fallback.

## Scope

**In scope (this change):**
- New `qddate/patterns/fingerprint.py` with:
  - `FingerprintKey` namedtuple `(length_min, length_max, chars, separator, language, year_format)`.
  - `_PATTERN_FINGERPRINTS: dict[FingerprintKey, frozenset[str]]` mapping
    fingerprint tuples to the set of pattern keys that carry them.
  - `compute_pattern_fingerprint(pattern: dict) -> FingerprintKey` returning
    the deterministic tuple for one pattern.
  - `intersect_fingerprints(text_fingerprint, allowed_chars) -> set[str]`
    helper that intersects the relevant buckets.
- `tests/test_fingerprint_index.py` with parity tests asserting that
  `_PATTERN_FINGERPRINTS` carries every pattern from `ALL_PATTERNS` and that
  every legacy per-instance bucket (`_patterns_by_length`, etc.) is
  reachable as a projection over the fingerprint index.
- Optional: `annotate_patterns()` adds a `fingerprint` field to each pattern
  dict (read-only at runtime — same defensive-copy discipline as
  `required_chars`).

**Out of scope (future round):**
- Replacing `_filter_patterns_hierarchical` with an intersection-based
  implementation. The behaviour-equivalence risk is too high to take in one
  step; this round locks the data, the next round ships the consumer.
- Changes to `DateParser.__init__` constructor parameters.
- Performance optimization beyond what the data layout naturally enables.

## Acceptance criteria

- `pytest tests/test_fingerprint_index.py -v`: all new tests pass.
- `pytest tests/`: existing 345 tests still pass (no regression).
- `ruff check qddate tests scripts openspec`: clean.
- `mypy qddate/__init__.py qddate/qdparser.py`: clean.
- Coverage of the new module ≥ 90%.
- No change to `qddate.__version__` (this is a data-layer-only round).

## Rollback plan

The change adds a new module and a new test file; nothing existing is
modified at the importing level. Rollback is `git revert`.