# Design: Centralize month tables

This is the *how* for `changes/centralize-month-tables`. Behaviour is
preserved; the change is a code-organization refactor.

## Current shape (before)

Each language module declares:

```python
# qddate/patterns/en.py
ENG_MONTHS = ["January", "February", ...]    # 12 title-case
ENG_MONTHS_LC = ["january", "february", ...] # 12 lowercase
ENG_MONTHS_ABBREV = ["Jan", "Feb", ...]       # 12 abbreviated title
ENG_MONTHS_ABBREV_LC = ["jan", "feb", ...]    # 12 abbreviated lower
en_mname2mon = {**{n: i for i, n in enumerate(ENG_MONTHS, 1)},
                **{n: i for i, n in enumerate(ENG_MONTHS_LC, 1)}}
enabbrev_mname2mon = {**{n: i for i, n in enumerate(ENG_MONTHS_ABBREV, 1)},
                      **{n: i for i, n in enumerate(ENG_MONTHS_ABBREV_LC, 1)}}
```

Same shape in 14 language modules. Russian adds `RU_MONTHS` (nominative),
`RU_MONTHS_GEN` (genitive), `RU_MONTHS_LC`, `RU_MONTHS_LC_GEN`, plus
`RU_MONTHS_SHORT`, `RU_MONTHS_SHORT_LC`.

`qddate/qdparser.py` keeps its own copy:

```python
_LANGUAGE_MONTHS = {
    "ru": _RUSSIAN_MONTHS,
    "fr": _FRENCH_MONTHS,
    "es": _SPANISH_MONTHS,
    "it": _ITALIAN_MONTHS,
    "pt": _PORTUGUESE_MONTHS,
    "de": _GERMAN_MONTHS,
    "nl": _DUTCH_MONTHS,
    "en": _ENGLISH_MONTHS,
    "tr": _TURKISH_MONTHS,
    "ro": _ROMANIAN_MONTHS,
    "uk": _UKRAINIAN_MONTHS,
    "bg": _BULGARIAN_MONTHS,
    "pl": _POLISH_MONTHS,
    "cz": _CZECH_MONTHS,
}
```

Adding a new language today requires editing three files and manually keeping
the data in sync.

## Target shape (after)

```python
# qddate/patterns/months.py
@dataclass(frozen=True)
class LanguageMonths:
    code: str
    full: tuple[str, ...]
    full_lc: tuple[str, ...]
    abbrev: tuple[str, ...]
    abbrev_lc: tuple[str, ...]
    genitive: tuple[str, ...] | None = None

    @property
    def month_to_int(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for src in (self.full, self.full_lc, self.abbrev, self.abbrev_lc):
            for i, name in enumerate(src, 1):
                out[name] = i
        if self.genitive:
            for i, name in enumerate(self.genitive, 1):
                out[name] = i
        return out


MONTHS_BY_LANGUAGE: dict[str, LanguageMonths] = {
    "en": LanguageMonths(
        code="en",
        full=("January", "February", ..., "December"),
        full_lc=("january", "february", ..., "december"),
        abbrev=("Jan", "Feb", ..., "Dec"),
        abbrev_lc=("jan", "feb", ..., "dec"),
    ),
    "ru": LanguageMonths(
        code="ru",
        full=("Январь", ..., "Декабрь"),
        full_lc=("январь", ..., "декабрь"),
        abbrev=("Янв.", ..., "Сент.", "Окт.", "Нояб.", "Дек."),
        abbrev_lc=("янв.", ..., "дек."),
        genitive=("Января", ..., "Декабря"),
    ),
    # ... 12 more
}
```

Each language module then re-exports for back-compat:

```python
# qddate/patterns/en.py
from .months import MONTHS_BY_LANGUAGE

_MONTHS_DATA = MONTHS_BY_LANGUAGE["en"]
ENG_MONTHS = list(_MONTHS_DATA.full)
ENG_MONTHS_LC = list(_MONTHS_DATA.full_lc)
ENG_MONTHS_ABBREV = list(_MONTHS_DATA.abbrev)
ENG_MONTHS_ABBREV_LC = list(_MONTHS_DATA.abbrev_lc)
en_mname2mon = {**{n: i for i, n in enumerate(ENG_MONTHS, 1)},
                **{n: i for i, n in enumerate(ENG_MONTHS_LC, 1)}}
enabbrev_mname2mon = {**{n: i for i, n in enumerate(ENG_MONTHS_ABBREV, 1)},
                      **{n: i for i, n in enumerate(ENG_MONTHS_ABBREV_LC, 1)}}
```

The pyparsing grammar in each file uses these constants unchanged. The
detection logic in `qddate/qdparser.py` reads `MONTHS_BY_LANGUAGE` instead
of `_LANGUAGE_MONTHS`.

## Migration strategy

1. **Phase 1 — write `months.py`**: build the table from the existing per-
   language lists. Verify each entry matches what the old code used.
2. **Phase 2 — parity tests**: assert the table produces identical sets to
   the old per-language lists. Run existing tests to confirm.
3. **Phase 3 — refactor language modules**: import from the table, keep
   the back-compat constants.
4. **Phase 4 — refactor detection logic**: replace `_LANGUAGE_MONTHS` with
   the table.
5. **Phase 5 — delete duplicates**: remove the now-redundant `_MONTHS_*`
   constants from `qdparser.py` (only the dict and one helper stay).

## Safety net

- **Parity test** in `tests/test_pattern_metadata.py`:
  ```python
  def test_months_by_language_matches_per_language_dicts():
      from qddate.patterns import en, de, fr, es, it, nl, pt, pl, cz, ro, uk, tr, bg, ru
      from qddate.patterns.months import MONTHS_BY_LANGUAGE
      for lang_mod, code in [...]:
          expected = {**lang_mod.<name>_mname2mon, **lang_mod.<abbrev>_mname2mon}
          assert MONTHS_BY_LANGUAGE[code].month_to_int == expected
  ```
- Existing 273-test suite covers every language's parse path.

## Risks

- **Hidden divergence**: if a per-language list accidentally has a typo or
  extra entry, the parity test catches it.
- **Russian genitive forms**: the Russian module has a more elaborate
  structure (genitive for `n <unit> назад` constructions). The table has
  an optional `genitive` field; if any other language later needs one,
  the field is ready.
- **Pyparsing grammar**: left untouched; the new module is pure data.
  Any pyparsing change is a separate concern.