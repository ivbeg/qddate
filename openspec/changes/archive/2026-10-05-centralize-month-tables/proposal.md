# OpenSpec Change: Centralize month tables across languages

Today every language module (`qddate/patterns/<lang>.py`) ships 3-5 month-name
lists (`EN_MONTHS`, `EN_MONTHS_LC`, `EN_MONTHS_ABBREV`, ...) and one or more
`*_mname2mon` dicts that map each form to an integer. The detection logic in
`qddate/qdparser.py` keeps yet another set of month-name lists
(`_RUSSIAN_MONTHS`, `_FRENCH_MONTHS`, `_GERMAN_MONTHS`, ...) that are
near-duplicates of the per-language ones, hand-maintained and drifted.

This change consolidates everything into a single `MONTHS_BY_LANGUAGE` table
in `qddate/patterns/months.py`. The per-language modules and the detection
logic both consume from this table.

## Why

`qddate.patterns.en` carries `ENG_MONTHS` (12 names), `ENG_MONTHS_LC` (12),
`ENG_MONTHS_ABBREV` (12), `ENG_MONTHS_ABBREV_LC` (12), plus `en_mname2mon`
(36 entries) and `enabbrev_mname2mon` (12). The same shape is repeated in
`de.py`, `fr.py`, `es.py`, `it.py`, `nl.py`, `pt.py`, `pl.py`, `cz.py`, `ro.py`,
`uk.py`, `tr.py`, `bg.py`, `ru.py`. Across the 14 languages that's ~600 LOC
of duplicated month-name data.

`qddate/qdparser.py` keeps a separate `_LANGUAGE_MONTHS` constant for
language detection. Adding a new language today means editing three files
(pattern module, detection language list, language code list), with no compile-
time or test-time guard ensuring all three stay in sync.

The fix is structural: a single table is the source of truth, and every
consumer reads from it.

## What changes

**`qddate/patterns/months.py` — new module**
- New module exposing:
  - `MONTHS_BY_LANGUAGE: dict[str, LanguageMonths]` — keyed by language
    code (`"en"`, `"de"`, ..., `"uk"`).
  - `LanguageMonths` dataclass with fields:
    - `code: str` — ISO 639-1 code
    - `full: tuple[str, ...]` — title-case full month names (12)
    - `full_lc: tuple[str, ...]` — lowercase full month names (12)
    - `abbrev: tuple[str, ...]` — title-case abbreviated names (12)
    - `abbrev_lc: tuple[str, ...]` — lowercase abbreviated names (12)
    - `genitive: tuple[str, ...] | None` — genitive forms (Russian/Ukrainian only)
    - `month_to_int: Mapping[str, int]` — all forms → 1-12
  - The structure is JSON-serialisable so a future change can dump it for
    tooling.

**Refactored language modules**
- Each `qddate/patterns/<lang>.py` imports from the new module instead of
  declaring its own lists/dicts. Names like `EN_MONTHS`, `de_mname2mon`
  remain as module-level constants (re-exported from the table) so existing
  tests that import them continue to work.
- Pyparsing grammar in each file is unchanged — it consumes the constants
  by name.

**Refactored detection logic in `qddate/qdparser.py`**
- The hand-maintained `_LANGUAGE_MONTHS` dict is replaced by
  `MONTHS_BY_LANGUAGE` (read from `qddate.patterns`).
- Adding a new language now requires only a single entry in the table.

**Drop-in compatibility**
- All existing public names (`EN_MONTHS`, `de_mname2mon`, etc.) remain
  importable. The OpenSpec guarantees no test breakage.

## Out of scope

- Replacing pyparsing `one_of(MONTHS)` patterns with the table (we just
  share the data, not the grammar generation).
- Adding new languages.

## Impact

- **Breaking?** No. Every existing import works through re-exports.
- **Affected:** Anyone editing the language modules will be guided to the
  table as the canonical place.
- **Risk:** A subtle behavioural drift if a language module's *old* list
  diverged slightly from what the table says. Mitigation: a parity test
  asserts `MONTHS_BY_LANGUAGE[code].month_to_int == <lang>_mname2mon` for
  every shipped language.
- **Rollback:** Self-contained revert.