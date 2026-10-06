## ADDED Requirements

### Requirement: Filter pipeline is documented

The public documentation SHALL include a description of the six-level
filter pipeline used by `DateParser.match()` and friends, and SHALL link to
it from `match.md` and `parse.md`.

#### Scenario: docs/docs/api/filter-pipeline.md exists
- **WHEN** the docs site is built
- **THEN** the page `docs/docs/api/filter-pipeline.md` SHALL be present
- **AND** it SHALL be reachable from the API reference sidebar

#### Scenario: Page lists the six filter levels
- **WHEN** the page is rendered
- **THEN** it SHALL describe each of the six filters (length, separator,
  year format, language, character set, prefix bucket)
- **AND** it SHALL describe the keyword arguments (`noprefix`,
  `nocharsetfilter`, `noseparatorfilter`, `noyearformatfilter`,
  `nolanguagefilter`) that disable them
- **AND** it SHALL be honest about the cost (slower parses when filters
  are disabled)