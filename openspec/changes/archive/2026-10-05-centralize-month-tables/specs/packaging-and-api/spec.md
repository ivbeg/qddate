## ADDED Requirements

### Requirement: Single source of truth for month names

Month-name lists and `month_to_int` mappings SHALL be defined once in
`qddate/patterns/months.py` and consumed by the per-language pattern
modules and the language-detection logic in `qddate/qdparser.py`.

#### Scenario: Adding a new language touches one file
- **WHEN** a new language is added to `qddate`
- **THEN** the contributor SHALL add a single entry to `MONTHS_BY_LANGUAGE`
  in `qddate/patterns/months.py` and (optionally) a small pattern module
- **AND** language detection SHALL pick it up automatically

#### Scenario: Per-language names are unchanged externally
- **WHEN** tests import `EN_MONTHS`, `de_mname2mon`, etc.
- **THEN** the names SHALL be present and equal to the canonical table
  values (verified by `test_each_language_month_to_int_matches_legacy`)
- **AND** no test code SHALL need to change

### Requirement: Detection logic uses the same table

The language-detection logic in `qddate/qdparser.py` SHALL resolve month
names from `MONTHS_BY_LANGUAGE` rather than from a hand-maintained
duplicate list.

#### Scenario: Detection table is data-only
- **WHEN** the detection logic searches the input for a known language
- **THEN** the lookup SHALL go through `MONTHS_BY_LANGUAGE[code]`
- **AND** no per-language `_MONTH_LANGUAGES` constant SHALL exist outside
  `qddate/patterns/months.py`