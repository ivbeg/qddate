## ADDED Requirements

### Requirement: Pattern tables use pyparsing 3 snake_case API

All pattern definitions SHALL use the pyparsing 3 snake_case API
(`set_results_name`, `one_of`, `set_parse_action`) rather than the deprecated
camelCase aliases.

#### Scenario: Library emits no pyparsing DeprecationWarnings at import
- **WHEN** `import qddate` is run with `-W error::DeprecationWarning`
- **THEN** no pyparsing deprecation warning SHALL be raised
- **AND** the module SHALL still expose the same `ALL_PATTERNS` table

#### Scenario: Pattern tables parse identically after migration
- **GIVEN** any historical parse probe from the regression test suite
- **WHEN** the probe is parsed by `qddate.DateParser()`
- **THEN** the result SHALL match the historical golden value