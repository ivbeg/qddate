## MODIFIED Requirements

### Requirement: Fingerprint-based candidate selection is the default

`DateParser.__init__` SHALL accept a `use_fingerprint: bool = True`
parameter (default since ``1.0.14``). When the caller explicitly passes
``False``, the constructor SHALL emit a ``DeprecationWarning`` noting
that the legacy 6-level filter will be removed in ``v2.0.0``. Passing
``True`` (or omitting the argument) SHALL be silent.

#### Scenario: Default behaviour uses fingerprint
- **WHEN** ``DateParser()`` is constructed with no arguments
- **THEN** ``use_fingerprint`` SHALL be ``True``
- **AND** the fingerprint-based filter SHALL run
- **AND** no ``DeprecationWarning`` SHALL be emitted

#### Scenario: Feature flag explicitly disabled
- **GIVEN** a ``DateParser(use_fingerprint=False)``
- **WHEN** ``match()`` / ``match_all()`` / ``parse()`` is called
- **THEN** the legacy 6-level filter SHALL produce the candidate set

#### Scenario: Explicit opt-in emits a warning
- **GIVEN** ``warnings.simplefilter("always")`` is in effect
- **WHEN** ``DateParser(use_fingerprint=False)`` is constructed
- **THEN** a ``DeprecationWarning`` SHALL be emitted with a message that
  mentions ``v2.0.0`` as the removal milestone