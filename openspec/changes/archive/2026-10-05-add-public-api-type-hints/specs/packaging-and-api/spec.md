## ADDED Requirements

### Requirement: Public API is type-hinted

The public methods of `DateParser` and `DateMatch` SHALL carry parameter and
return type hints. Internal helpers MAY be untyped.

#### Scenario: Static type-checking finds the public surface
- **WHEN** a downstream consumer runs `mypy` (or equivalent) against code
  that imports `qddate`
- **THEN** calls to `DateParser.parse()`, `.match()`, `.match_all()`,
  `.match_typed()`, `.parse_many()`, `.format_date()`, and attribute access
  on the returned `DateMatch` SHALL be type-checked without `# type: ignore`

#### Scenario: DateMatch fields carry hints
- **WHEN** `DateMatch` is introspected (e.g. by `dataclasses.fields()` or an
  IDE)
- **THEN** every declared field SHALL declare a type
- **AND** the hints SHALL be consistent with the runtime types documented in
  the `DateMatch` docstring