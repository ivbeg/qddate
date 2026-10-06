## ADDED Requirements

### Requirement: README pattern counts are auto-generated

The pattern counts in `README.md` SHALL be a function of
`qddate.patterns.ALL_PATTERNS` (and the package's supported-language list),
not a hand-written string. A delimited markdown fragment SHALL be inserted
into the README so the script can replace it idempotently.

#### Scenario: Generated counts match the canonical table
- **WHEN** `python scripts/generate_readme_stats.py` is run against the
  current codebase
- **THEN** the emitted fragment SHALL report the same count as
  `len(qddate.patterns.ALL_PATTERNS)` (or the equivalent generated-pattern
  count from a fresh `DateParser().patterns`)
- **AND** the language count SHALL equal `len(qddate.patterns.SUPPORTED_LANGUAGES)`

#### Scenario: Script is idempotent
- **WHEN** the script runs twice on the same `README.md`
- **THEN** the second run SHALL NOT produce a diff (or only a no-op diff
  where the script replaces the block with itself)

#### Scenario: Adding a new pattern updates the README
- **GIVEN** a new base pattern is added to `qddate.patterns`
- **WHEN** `python scripts/generate_readme_stats.py` is run
- **THEN** the emitted count SHALL increase by 1
- **AND** the README SHALL be updated to reflect the new count