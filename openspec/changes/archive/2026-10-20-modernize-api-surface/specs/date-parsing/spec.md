## ADDED Requirements

### Requirement: Typed match result

The parser SHALL provide a typed result object (`DateMatch`) exposing the constructed
`datetime`, the matched pattern's key, the detected language, the format string, and
the raw input string, as an alternative to the legacy dict return shape. The legacy
dict shape returned by `match()` SHALL remain available and unchanged.

#### Scenario: Typed result for a supported date
- **WHEN** the typed match method is called on `"01.12.2009"`
- **THEN** the result SHALL expose `.datetime == datetime.datetime(2009, 12, 1)`
- **AND** SHALL expose `.pattern_key`, `.language`, `.format`, and `.raw`

#### Scenario: Legacy dict shape preserved
- **WHEN** `match("01.12.2009")` is called
- **THEN** the result SHALL remain a dict with `"values"` and `"pattern"` keys

### Requirement: Bulk parsing entry point

The parser SHALL provide a bulk parsing entry point that accepts an iterable of input
strings and yields a result for each, reusing internal filter indexes across the batch
rather than re-initializing them per string.

#### Scenario: Batch of mixed inputs
- **WHEN** the bulk method is called with `["01.12.2009", "invalid", "6 Jan 2009"]`
- **THEN** it SHALL yield a datetime for the first and third inputs and `None` for the
  second

#### Scenario: Throughput at least matches single-call path
- **WHEN** the bulk method is run over the benchmark corpus
- **THEN** its throughput SHALL not be lower than calling `parse()` per string

### Requirement: Snake_case session aliases

The parser SHALL provide `start_session` and `end_session` methods as PEP 8-compliant
aliases for the existing `startSession` and `endSession` methods. Both naming forms
SHALL remain functional and equivalent.

#### Scenario: Alias equivalence
- **WHEN** `start_session(...)` is called instead of `startSession(...)`
- **THEN** the behavior SHALL be identical
