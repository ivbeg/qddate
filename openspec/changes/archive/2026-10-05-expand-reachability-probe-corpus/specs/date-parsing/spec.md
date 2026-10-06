## ADDED Requirements

### Requirement: Reachability oracle test

The test suite SHALL include a reachability oracle that asserts every base
pattern in `ALL_PATTERNS` is the *winning* match for at least one fixture
string, with one fixture dedicated to exercising each base pattern.

#### Scenario: Every base pattern wins a probe
- **GIVEN** the canonical pattern table `qddate.patterns.ALL_PATTERNS`
- **WHEN** the reachability oracle runs over a curated probe corpus
- **THEN** every basekey in `ALL_PATTERNS` SHALL appear as the winning match
  for at least one probe string
- **AND** every probe string SHALL produce a non-None parse result

#### Scenario: New pattern breaks the oracle loudly
- **GIVEN** a new pattern is added to `ALL_PATTERNS` without a matching probe
- **WHEN** the reachability oracle runs
- **THEN** the test SHALL fail with a message naming the new pattern key
- **AND** the fix SHALL be to add a probe, not to weaken the oracle