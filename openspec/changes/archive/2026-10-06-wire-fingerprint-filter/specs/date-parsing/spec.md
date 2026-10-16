## ADDED Requirements

### Requirement: Fingerprint-based candidate selection is opt-in

`DateParser.__init__` SHALL accept a `use_fingerprint: bool = False`
parameter. When `True`, the matcher routes through the fingerprint-based
filter (``_filter_patterns_fingerprint``); when ``False`` (the default),
the existing 6-level filter (``_filter_patterns_hierarchical``) runs
unchanged.

#### Scenario: Default behaviour unchanged
- **WHEN** ``DateParser()`` is constructed with no arguments
- **THEN** ``use_fingerprint`` SHALL be ``False``
- **AND** the existing 6-level filter SHALL run unchanged

#### Scenario: Feature flag is honoured by every public method
- **GIVEN** a ``DateParser(use_fingerprint=True)``
- **WHEN** ``match()``, ``match_all()``, or ``parse()`` is called
- **THEN** the fingerprint-based filter SHALL produce the candidate set
- **AND** the existing 6-level filter SHALL NOT be invoked

### Requirement: Fingerprint-based filter is a superset of the legacy filter

For every input string the fingerprint-based filter SHALL return a
candidate pattern set that is a superset-or-equal of the candidate set
the existing 6-level filter would have returned for the same input.

#### Scenario: Superset on the probe corpus
- **GIVEN** any string from the existing reachability probe corpus
- **WHEN** the same string is fed to both filters
- **THEN** the fingerprint-based filter's set SHALL contain every pattern
  the legacy filter's set contains

### Requirement: Superset preservation across filter toggles

The fingerprint-based filter SHALL honour the existing filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``, ``noseparatorfilter``,
``noyearformatfilter``, ``nolanguagefilter``) and SHALL NOT silently drop
a pattern that the legacy filter would have kept under the same toggles.

#### Scenario: Disabling nocharsetfilter widens the candidate set
- **GIVEN** a ``DateParser(use_fingerprint=True, nocharsetfilter=True)``
- **WHEN** ``match(text)`` runs
- **THEN** the candidate set SHALL include patterns the charset filter
  would have dropped (mirroring the legacy filter's behaviour)