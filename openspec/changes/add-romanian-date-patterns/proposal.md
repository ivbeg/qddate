# OpenSpec Change: Add Romanian date patterns

Add Romanian (`ro`) month-name parsing so qddate can parse Romanian news listings
without relying on coincidental French or German matches for the shared month name
`Mai`.

## Why

Romanian is not in the supported-language set and qddate has no Romanian month-name
patterns. On pages such as `https://data.gov.ro/ro/blog`, unrestricted parsing matches
only dates containing `Mai` through French or German patterns and rejects dates such as
`19 Februarie 2026` and `4 Decembrie 2025`. Downstream listing analyzers can therefore
build an incomplete cached pattern set and silently omit most entries.

## What changes

**Romanian month-name parsing**
- From: Romanian full and abbreviated month names are unsupported, except where a name
  happens to overlap another language.
- To: qddate supports day-month-year dates using all twelve Romanian full month names
  and the standard abbreviated forms published by Unicode CLDR, in lowercase and
  title case, including generated time and trailing-text variants.
- Reason: Romanian news listings commonly publish localized textual dates.
- Impact: Non-breaking. Inputs that previously returned `None` gain a parsed result.

**Romanian language registration and filtering**
- From: `DateParser(languages="ro")` raises `ValueError`, Romanian patterns have no
  metadata/index entry, and automatic filtering cannot recognize Romanian month names.
- To: `ro` is a supported language code with registered patterns, metadata, character
  classification, and month-name detection; `languages="ro"` selects Romanian and
  language-neutral patterns while excluding other languages.
- Reason: New patterns must remain reachable through every parser filter and public
  language-selection path.
- Impact: Non-breaking. The supported-language set grows from twelve to thirteen.

**Shared month-name behavior**
- From: `Mai` may be labeled French or German by unrestricted parsing because Romanian
  has no candidate patterns.
- To: A Romanian-only parser matches `Mai` with Romanian pattern metadata. An
  unrestricted parser guarantees the correct calendar result but may retain an
  equivalent French or German pattern key because the token alone is linguistically
  ambiguous.
- Reason: A single shared month name does not provide enough evidence to infer language;
  explicit filtering must be deterministic without inventing certainty for unrestricted
  parsing.
- Impact: Non-breaking. Parsed date values remain unchanged for ambiguous inputs.

## Impact

- **Breaking?** No. This adds accepted inputs and one supported language code.
- **Affected:** Romanian-language consumers, language-filter users, pattern-metadata
  consumers, and downstream analyzers such as newsworker.
- **Data source:** Unicode CLDR Romanian Gregorian month names and abbreviations.
- **Rollback:** Remove the Romanian pattern module and its registry, metadata,
  detection, documentation, and test entries.

## Open questions

None. Weekday-prefixed Romanian dates and relative-date phrases are outside this
change; they can be proposed separately if real fixtures require them.
