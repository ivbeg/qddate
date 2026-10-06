## ADDED Requirements

### Requirement: ALL_PATTERNS is not mutated after import

The module-level `qddate.patterns.ALL_PATTERNS` list SHALL be a stable,
read-only structure after import. Constructing any number of `DateParser`
instances SHALL NOT modify it.

#### Scenario: Repeated DateParser construction is idempotent
- **GIVEN** a snapshot of `qddate.patterns.ALL_PATTERNS` taken right after
  import
- **WHEN** five `DateParser()` instances are constructed sequentially
- **THEN** the snapshot SHALL match `ALL_PATTERNS` byte-for-byte afterward

#### Scenario: __generate is read-only against ALL_PATTERNS
- **GIVEN** `qddate.patterns.ALL_PATTERNS` before any `DateParser` is created
- **WHEN** `DateParser._DateParser__generate(ALL_PATTERNS)` is called twice
- **THEN** the second call SHALL produce the same list of generated patterns
  as the first
- **AND** `ALL_PATTERNS[i]` SHALL be byte-identical after each call