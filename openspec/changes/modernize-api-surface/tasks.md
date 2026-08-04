# Tasks: Modernize API surface

## DateMatch result object

- [ ] Define `DateMatch` dataclass: `datetime`, `pattern_key`, `language`, `format`,
      `raw`, plus `to_dict()` returning the legacy shape.
- [ ] Add `match_typed()` method (recommended rollout) returning `DateMatch` or `None`.
- [ ] Populate `language` from the pattern metadata added in Change 3.
- [ ] Tests: `match_typed()` returns a `DateMatch` with correct fields for EN/RU/DE
      cases; `to_dict()` round-trips to the legacy shape.

## Bulk parsing

- [ ] Add `parse_many(iterable)` generator yielding `(input, datetime|None)` (or
      `DateMatch|None`).
- [ ] Reuse the length/charset indexes across the batch; avoid re-running per-string
      detection where the charset is shared.
- [ ] Tests: batch of mixed-language inputs returns correct results; throughput is
      >= single-call path on the benchmark corpus.

## snake_case aliases

- [ ] Add `start_session()` / `end_session()` delegating to the existing methods.
- [ ] Mark `startSession` / `endSession` as deprecated (DeprecationWarning) in
      docstrings; keep them functional.
- [ ] Test: both names work and are equivalent.

## Docs

- [ ] Update README usage section with `DateMatch`, `parse_many`, and snake_case names.
- [ ] Add type hints to the new public methods (`target-version = "py38"`).

## Verification

- [ ] `pytest -q` green; existing dict-returning `match()` unchanged.
- [ ] Benchmark: `parse_many` >= single-call throughput on the corpus.
