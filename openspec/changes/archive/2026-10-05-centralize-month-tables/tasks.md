# Tasks: Centralize month tables

## Phase 1 — write `qddate/patterns/months.py`

- [ ] Create `qddate/patterns/months.py` with:
      - `@dataclass(frozen=True) class LanguageMonths`
      - `MONTHS_BY_LANGUAGE: dict[str, LanguageMonths]`
      - Each of the 14 shipped languages populated from the existing per-language
        lists in `<lang>.py` (en, ru, de, fr, es, it, nl, pt, pl, cz, ro, uk,
        tr, bg).
- [ ] Add a `month_to_int` property on `LanguageMonths` that returns the
      combined dict of every variant → month integer.

## Phase 2 — parity tests

- [ ] Add `tests/test_months_table.py` with:
      - `test_months_table_covers_all_shipped_languages` — every language
        code in `SUPPORTED_LANGUAGES` is in `MONTHS_BY_LANGUAGE`.
      - `test_each_language_month_to_int_matches_legacy` — for every
        language, `MONTHS_BY_LANGUAGE[code].month_to_int` equals the
        combined dict of `<lang>_<name>_mname2mon` plus
        `<lang>_<abbrev>_mname2mon`.
      - `test_all_months_have_12_entries` — every `full` and `full_lc`
        tuple has 12 entries and contains no duplicates.
      - `test_each_variant_distinct` — no name appears in two different
        variants of the same language (would indicate data drift).

## Phase 3 — refactor language modules

- [ ] For each of `en.py`, `ru.py`, `de.py`, `fr.py`, `es.py`, `it.py`,
      `nl.py`, `pt.py`, `pl.py`, `cz.py`, `ro.py`, `uk.py`, `tr.py`, `bg.py`:
      - Replace the local month-name lists with imports from
        `qddate.patterns.months`.
      - Re-export `LANG_MONTHS`, `LANG_MONTHS_LC`, `LANG_MONTHS_ABBREV`,
        `LANG_MONTHS_ABBREV_LC`, `lang_mname2mon`,
        `langabbrev_mname2mon` from the table for back-compat.
- [ ] Verify each module's pyparsing grammar still compiles by running the
      full test suite.

## Phase 4 — refactor detection logic

- [ ] In `qddate/qdparser.py`, replace the hand-maintained
      `_LANGUAGE_MONTHS` dict (with `_RUSSIAN_MONTHS`, `_FRENCH_MONTHS`,
      ..., `_BULGARIAN_MONTHS`) by reading from
      `qddate.patterns.MONTHS_BY_LANGUAGE`.
- [ ] The detection algorithm itself does not change; only the source of
      the data does.

## Phase 5 — delete duplicates

- [ ] Remove the now-redundant `_RUSSIAN_MONTHS`, `_FRENCH_MONTHS`, etc.
      frozensets from `qddate/qdparser.py`. Keep `_LANGUAGE_MONTHS` (now
      derived from the table) and the public test surface.

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `python -m mypy qddate/__init__.py qddate/qdparser.py` clean.
- [ ] `ruff check qddate tests scripts` clean.
- [ ] `python -W error::DeprecationWarning -c "import qddate"` clean.