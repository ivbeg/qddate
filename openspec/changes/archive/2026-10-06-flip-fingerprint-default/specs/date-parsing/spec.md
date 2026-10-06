## MODIFIED Requirements

### Requirement: Fingerprint-based candidate selection is opt-in

The constructor parameter ``use_fingerprint`` SHALL default to
``True`` (flipped from ``False`` in release ``1.0.14``). When ``True``
(the default), the matcher routes through the fingerprint-based
filter (``_filter_patterns_fingerprint``); when ``False``, the existing
6-level filter (``_filter_patterns_hierarchical``) runs.

#### Scenario: Default behaviour uses fingerprint
- **WHEN** ``DateParser()`` is constructed with no arguments
- **THEN** ``use_fingerprint`` SHALL be ``True``
- **AND** the fingerprint-based filter SHALL run

#### Scenario: Feature flag explicitly disabled
- **GIVEN** a ``DateParser(use_fingerprint=False)``
- **WHEN** ``match()`` / ``match_all()`` / ``parse()`` is called
- **THEN** the legacy 6-level filter SHALL produce the candidate set

## MODIFIED Requirements

### Requirement: Fingerprint-based filter is exactly equivalent to the legacy filter

For every input string the fingerprint-based filter SHALL return a
candidate pattern set that is **equal** to the candidate set the
existing 6-level filter would have returned for the same input. The
equality MUST hold under any combination of filter toggles
(``noprefix``, ``allow_no_year``, ``nocharsetfilter``,
``noseparatorfilter``, ``noyearformatfilter``, ``nolanguagefilter``).

#### Scenario: Equality on the extended probe corpus
- **GIVEN** any string from the extended probe corpus (the union of the
  reachability probes and the regression corpus — 165 strings covering
  every shipped language, every separator, every year-format bucket,
  weekday + short + compact + edge cases)
- **WHEN** the same string is fed to both filters
- **THEN** the two candidate sets SHALL be equal (no additions, no removals)