# Tasks: Add Romanian date patterns

## Pattern definitions

- [x] Add a Romanian pattern module containing all twelve full month names and CLDR
  abbreviated forms, with lowercase and title-case day-month-year patterns.
- [x] Ensure abbreviated forms accept their standard trailing period without making
  punctuation optional for unrelated full month names.
- [x] Verify generated time suffixes and trailing-text variants inherit Romanian
  pattern metadata.

## Parser integration

- [x] Register `PATTERNS_RO` in the canonical all-pattern list and language map.
- [x] Add `ro` to the supported-language set and assign explicit language/separator
  metadata to every Romanian base pattern.
- [x] Add Romanian month names to automatic language detection and classify Romanian
  month patterns for character-set filtering.
- [x] Update generated documentation and supported-language counts where applicable.

## Tests

- [x] Add positive tests for every full Romanian month name in lowercase and title
  case using representative day/year values from the data.gov.ro listing.
- [x] Add positive tests for every CLDR abbreviated Romanian month form.
- [x] Add tests for `DateParser(languages="ro")`, default parsing, time suffixes,
  trailing text, and Romanian pattern metadata.
- [x] Add negative tests proving a Romanian-only parser rejects language-exclusive
  French and German month names.
- [x] Add a regression fixture covering `19 Februarie 2026`, `4 Decembrie 2025`, and
  ambiguous `21 Mai 2026`.

## Verification

- [x] Run the focused Romanian, language-filter, and pattern-metadata tests.
- [x] Run the complete qddate test suite.
- [x] Install the local qddate checkout into an isolated environment and verify that
  newsworker analysis of the saved data.gov.ro fixture discovers Romanian patterns
  and extracts non-May entries.
