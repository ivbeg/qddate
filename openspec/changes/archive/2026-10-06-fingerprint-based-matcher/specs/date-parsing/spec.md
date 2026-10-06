## ADDED Requirements

### Requirement: Pattern fingerprint index

Each pattern SHALL carry a precomputed fingerprint derived from
`len(qax)`, `separator`, `language`, `chars`, `year_format`, and length
range. The set of all fingerprints SHALL be exposed as
`qddate.patterns._PATTERN_FINGERPRINTS`, mapping each unique fingerprint
tuple to the frozenset of pattern keys that share it.

#### Scenario: Fingerprint is deterministic
- **WHEN** `compute_pattern_fingerprint(p)` is called twice on the same
  pattern dict
- **THEN** the result SHALL be `==` to itself (hashable, equality-stable)

#### Scenario: Every pattern is in the index
- **WHEN** the fingerprint index is built at import time
- **THEN** every key in `ALL_PATTERNS` SHALL appear in exactly one bucket
  of `_PATTERN_FINGERPRINTS`

### Requirement: Legacy buckets are projections of the index

The per-instance buckets `_patterns_by_length`, `_patterns_by_separator`,
`_patterns_by_language`, and `_patterns_by_year_format` SHALL be
derivable from `_PATTERN_FINGERPRINTS` by a single dimension-projection
loop. The index SHALL NOT carry any pattern that is missing from the
legacy buckets.

#### Scenario: Length bucket projection
- **GIVEN** the set of pattern keys whose pattern has
  `length_min ≤ len(text) ≤ length_max`
- **THEN** that set SHALL equal the union of `_PATTERN_FINGERPRINTS` entries
  whose `length_min ≤ len(text) ≤ length_max`

### Requirement: Intersection candidate set

`intersect_fingerprints(text_fingerprint, allowed_chars)` SHALL return the
union of `_PATTERN_FINGERPRINTS` entries whose key is satisfied by the
text's fingerprint (length match, chars match with `ACCENTED → LATIN`
substitution, separator subset, language subset, year-format subset).
The returned set SHALL be a superset-or-equal of the candidate set
returned by the existing 6-level filter pipeline for the same input.

#### Scenario: Accented-vs-Latin substitution preserved
- **GIVEN** a pattern whose required chars include `CHAR_SET_ACCENTED`
- **WHEN** the text contains only `CHAR_SET_LATIN`
- **THEN** `intersect_fingerprints` SHALL still include this pattern in
  the result