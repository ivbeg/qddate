## MODIFIED Requirements

### Requirement: Minimal runtime dependencies

The runtime dependency set SHALL be limited to `pyparsing`. Heavy general-purpose
date libraries (e.g. `dateparser`, `python-dateutil`, `arrow`, `pendulum`) SHALL be
optional, available only through extras, and SHALL NOT be imported by the library at
runtime.

#### Scenario: Import without optional deps installed
- **GIVEN** an environment with only `pyparsing` installed
- **WHEN** `import qddate` and `qddate.DateParser()` are executed
- **THEN** no `ImportError` or `ModuleNotFoundError` SHALL be raised

#### Scenario: Benchmark extras are opt-in
- **WHEN** the package is installed without extras
- **THEN** `dateparser`, `python-dateutil`, `arrow`, and `pendulum` SHALL NOT be
  installed as transitive dependencies
- **AND** installing the `bench` extra SHALL make them available
