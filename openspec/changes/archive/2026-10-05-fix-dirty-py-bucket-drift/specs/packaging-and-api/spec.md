## ADDED Requirements

### Requirement: Pattern metadata drives prefix buckets

The `matchPrefix()` function SHALL derive its prefix-bucket groupings from the
single-source-of-truth `_PATTERN_METADATA` table, not from hand-synced lists.

#### Scenario: Adding a new pattern updates the buckets automatically
- **GIVEN** a new pattern dict is appended to `qddate.patterns.ALL_PATTERNS`
  with a registered `_PATTERN_METADATA` entry
- **WHEN** `matchPrefix(text[:6])` is called for any input
- **THEN** the new pattern SHALL be eligible for inputs whose prefix matches
  its `(language, separator)` grouping
- **AND** the contributor SHALL NOT need to edit `qddate/dirty.py` to enable
  this

#### Scenario: Removing a pattern clears the buckets automatically
- **GIVEN** a pattern is removed from `qddate.patterns.ALL_PATTERNS`
- **WHEN** `matchPrefix(text[:6])` is called
- **THEN** the removed pattern SHALL NOT appear in any bucket

### Requirement: Prefix bucket parity is regression-tested

The test suite SHALL include a parity test that asserts the derived buckets
produce the same candidate set as the legacy hand-synced lists (during the
migration window) and that any subsequent regression in the derivation logic
is caught at CI time.

#### Scenario: Parity test exists
- **WHEN** `pytest tests/test_regressions_2026_09.py` runs
- **THEN** the parity test SHALL execute against the full probe corpus
- **AND** any disagreement SHALL fail the suite with a clear diff