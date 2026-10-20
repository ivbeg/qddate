# Tasks: Modernize API surface

> Archived 2026-10-20 after verification against the code. Shipped in 1.0.11. Items shipped differently or not at all are left unchecked below.


## DateMatch result object

- [x] Define `DateMatch` dataclass: `datetime`, `pattern_key`, `language`, `format`,
      `raw`, plus `to_dict()` returning the legacy shape.
- [x] Add `match_typed()` method (recommended rollout) returning `DateMatch` or `None`.
- [x] Populate `language` from the pattern metadata added in Change 3.
- [x] Tests: `match_typed()` returns a `DateMatch` with correct fields for EN/RU/DE
      cases; `to_dict()` round-trips to the legacy shape.

## Bulk parsing

- [ ] Add `parse_many(iterable)` generator yielding `(input, datetime|None)` (or
      `DateMatch|None`).
  - Shipped differently: `parse_many()` yields `datetime | None` per input (no `(input, result)` tuples); the canonical spec records this contract.
- [ ] Reuse the length/charset indexes across the batch; avoid re-running per-string
      detection where the charset is shared.
  - Partly: indexes are built once at construction; per-string detection is not shared across the batch.
- [ ] Tests: batch of mixed-language inputs returns correct results; throughput is
      >= single-call path on the benchmark corpus.
  - Partly: the batch test exists; no throughput comparison.

## snake_case aliases

- [x] Add `start_session()` / `end_session()` delegating to the existing methods.
- [x] Mark `startSession` / `endSession` as deprecated (DeprecationWarning) in
      docstrings; keep them functional.
- [x] Test: both names work and are equivalent.

## Docs

- [ ] Update README usage section with `DateMatch`, `parse_many`, and snake_case names.
  - Not done in README; documented in `docs/docs/api/dateparser.md` instead.
- [x] Add type hints to the new public methods (`target-version = "py38"`).

## Verification

- [x] `pytest -q` green; existing dict-returning `match()` unchanged.
- [ ] Benchmark: `parse_many` >= single-call throughput on the corpus.
  - Not done: no benchmark; `parse_many()` calls `parse()` per item.
