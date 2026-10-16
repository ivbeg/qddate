"""Parity tests for the centralized ``MONTHS_BY_LANGUAGE`` table.

Every shipped language's ``*_mname2mon`` dict (and its ``*lc``,
``*short``, ``*orig`` siblings) must produce a set of (name → month) entries
that matches what ``MONTHS_BY_LANGUAGE[code].month_to_int`` says.
"""

import importlib

import pytest

from qddate.patterns import SUPPORTED_LANGUAGES
from qddate.patterns.months import MONTHS_BY_LANGUAGE, get_months


def test_table_covers_all_shipped_languages():
    """Every code in ``SUPPORTED_LANGUAGES`` must appear in the table."""
    assert set(MONTHS_BY_LANGUAGE) == set(SUPPORTED_LANGUAGES)


@pytest.mark.parametrize("code", sorted(SUPPORTED_LANGUAGES))
def test_each_language_has_12_full_entries(code):
    """The ``full`` and ``full_lc`` tuples are always 12 calendar entries."""
    data = get_months(code)
    assert len(data.full) == 12
    assert len(data.full_lc) == 12


@pytest.mark.parametrize("code", sorted(SUPPORTED_LANGUAGES))
def test_each_language_has_12_full_entries_or_explicit_empty(code):
    """``full`` and ``full_lc`` are always 12 entries; ``abbrev`` / ``abbrev_lc``
    may be empty for languages (or one of the rarer languages) that don't
    use a separate abbreviation."""
    data = get_months(code)
    assert len(data.full) == 12, f"{code}: full should be 12 entries"
    assert len(data.full_lc) == 12, f"{code}: full_lc should be 12 entries"


@pytest.mark.parametrize("code", sorted(SUPPORTED_LANGUAGES))
def test_each_language_abbrev_entries_are_12_or_empty(code):
    data = get_months(code)
    for var in (data.abbrev, data.abbrev_lc):
        assert len(var) == 0 or len(var) == 12, (
            f"{code}: abbreviation variant has {len(var)} entries (expected 0 or 12)"
        )


@pytest.mark.parametrize("code", sorted(SUPPORTED_LANGUAGES))
def test_no_impossible_duplicate_names_per_language(code):
    """Names that appear in multiple variants of the same language map to
    the same month.

    Some languages don't have separate abbreviations for some months (e.g.
    English "May", German "Mai"), so the same name legitimately appears in
    both ``full`` and ``abbrev``. The legacy code allows it; we only assert
    that every duplicate maps to the **same** month.
    """
    data = get_months(code)
    all_pairs: list[tuple[str, int]] = []
    for src in (data.full, data.full_lc, data.abbrev, data.abbrev_lc,
                data.genitive or (), data.genitive_lc or (),
                data.short or (), data.short_lc or ()):
        for i, name in enumerate(src, 1):
            all_pairs.append((name, i))

    by_name: dict[str, list[int]] = {}
    for name, month in all_pairs:
        by_name.setdefault(name, []).append(month)
    conflicts = {n: ms for n, ms in by_name.items() if len(set(ms)) > 1}
    assert not conflicts, (
        f"Language {code!r}: same name maps to different months: {conflicts}"
    )


@pytest.mark.parametrize("code", sorted(SUPPORTED_LANGUAGES))
def test_month_to_int_compatible_with_legacy_dict(code):
    """The table's month_to_int must contain every (name, month) pair the
    legacy per-language dict used to expose.

    Languages that declare multiple mname2mon dicts (e.g. ``pl_mname2mon``
    plus ``pllc_mname2mon``) have all of them folded in here.
    """
    data = get_months(code)
    table_pairs = set(data.month_to_int.items())

    # Map the per-language module path. English lives in ``base``.
    LANG_PATHS = {
        "en": "qddate.patterns.base",
        "ru": "qddate.patterns.ru",
        "de": "qddate.patterns.de",
        "fr": "qddate.patterns.fr",
        "es": "qddate.patterns.es",
        "it": "qddate.patterns.it",
        "nl": "qddate.patterns.nl",
        "pt": "qddate.patterns.pt",
        "pl": "qddate.patterns.pl",
        "cz": "qddate.patterns.cz",
        "ro": "qddate.patterns.ro",
        "uk": "qddate.patterns.uk",
        "tr": "qddate.patterns.tr",
        "bg": "qddate.patterns.bg",
    }
    import sys
    full_name = LANG_PATHS[code]
    if full_name not in sys.modules:
        importlib.import_module(full_name)
    mod = sys.modules[full_name]

    # Collect every (name, month) pair the legacy module exposed via
    # `*_mname2mon` dicts and matching month lists.
    legacy_pairs: set[tuple[str, int]] = set()

    list_attr_to_dict_attr = {
        # (month-name list attribute) -> (matching mname2mon dict attribute)
        "ENG_MONTHS": "en_mname2mon",
        "ENG_MONTHS_LC": "enlc_mname2mon",
        "ENG_MONTHS_SHORT": "ensh_mname2mon",
        "RUS_MONTHS": "ru_mname2mon",
        "RUS_MONTHS_LC": "rulc_mname2mon",
        "RUS_MONTHS_ORIG": "ru_origmname2mon",
        "RUS_MONTHS_ORIG_LC": "rulc_origmname2mon",
        "DE_MONTHS": "de_mname2mon",
        "DE_MONTHS_LC": "delc_mname2mon",
        "DE_MONTHS_SHORT": "deshort_mname2mon",
        "DE_MONTHS_SHORT_LC": "deshortlc_mname2mon",
        "FR_MONTHS": "fr_mname2mon",
        "FR_MONTHS_LC": "frlc_mname2mon",
        "FR_MONTHS_SHORT": "frshort_mname2mon",
        "FR_MONTHS_SHORT_LC": "frshortlc_mname2mon",
        "ES_MONTHS": "es_mname2mon",
        "ES_MONTHS_LC": "eslc_mname2mon",
        "ES_MONTHS_SHORT": "esshort_mname2mon",
        "ES_MONTHS_SHORT_LC": "esshortlc_mname2mon",
        "IT_MONTHS": "it_mname2mon",
        "IT_MONTHS_LC": "itlc_mname2mon",
        "IT_MONTHS_SHORT": "itshort_mname2mon",
        "IT_MONTHS_SHORT_LC": "itshortlc_mname2mon",
        "NL_MONTHS": "nl_mname2mon",
        "NL_MONTHS_LC": "nllc_mname2mon",
        "NL_MONTHS_SHORT": "nlshort_mname2mon",
        "NL_MONTHS_SHORT_LC": "nlshortlc_mname2mon",
        "PT_MONTHS": "pt_mname2mon",
        "PT_MONTHS_LC": "ptlc_mname2mon",
        "PT_MONTHS_SHORT": "ptshort_mname2mon",
        "PT_MONTHS_SHORT_LC": "ptshortlc_mname2mon",
        "PL_MONTHS": "pl_mname2mon",
        "PL_MONTHS_LC": "pl_mname2mon",  # Polish uses one big dict
        "PL_MONTHS_GEN": "pl_mname2mon",
        "PL_MONTHS_GEN_LC": "pl_mname2mon",
        "CZ_MONTHS": "cz_mname2mon",
        "CZ_MONTHS_LC": "czlc_mname2mon",
        "CZ_MONTHS_GEN": "cz_mname2mon_all",
        "CZ_MONTHS_GEN_LC": "cz_mname2mon_all",
        "RO_MONTHS": "ro_mname2mon",
        "RO_MONTHS_LC": "rolc_mname2mon",
        "RO_MONTHS_SHORT": "roshort_mname2mon",
        "RO_MONTHS_SHORT_LC": "roshortlc_mname2mon",
        "UK_MONTHS": "uk_mname2mon",
        "UK_MONTHS_LC": "uk_mname2mon",
        "UK_MONTHS_GEN": "uk_mname2mon",
        "UK_MONTHS_GEN_LC": "uk_mname2mon",
        "UK_MONTHS_SHORT": "uk_mname2mon",
        "UK_MONTHS_SHORT_LC": "uk_mname2mon",
        "TR_MONTHS": "tr_mname2mon",
        "TR_MONTHS_LC": "trlc_mname2mon",
        "BG_MONTHS": "bg_mname2mon",
        "BG_MONTHS_LC": "bglc_mname2mon",
    }

    for list_attr, dict_attr in list_attr_to_dict_attr.items():
        if not hasattr(mod, list_attr):
            continue
        names = getattr(mod, list_attr)
        mname2mon = getattr(mod, dict_attr, None)
        if mname2mon is None:
            continue
        # Verify the dict mapping for this list is itself consistent.
        for i, name in enumerate(names, 1):
            assert mname2mon[name] == i, (
                f"{code}/{list_attr}: expected {name} → {i} in {dict_attr}, "
                f"got {mname2mon[name]}"
            )
        # Fold into the combined set.
        legacy_pairs.update(mname2mon.items())

    # The table should contain at least every legacy entry.
    missing_in_table = legacy_pairs - table_pairs
    extra_in_table = table_pairs - legacy_pairs
    # Bulgarian legacy uses mixed Latin/Cyrillic (a known typo class) that
    # we intentionally don't propagate into the canonical table. Treat as a
    # soft warning rather than a hard failure; the canonical Cyrillic forms
    # are the right ones.
    if missing_in_table and code == "bg":
        # Verify the missing entries are all the Latin-script variants of
        # the canonical Cyrillic forms.
        from qddate.patterns.months import MONTHS_BY_LANGUAGE as TBL
        canonical_names = set(TBL[code].full_lc) | set(TBL[code].full)
        # Map Latin-script char → Cyrillic-script char (Bulgarian legacy uses
        # Latin letters for a/y/e/p/c/x/o that look like Cyrillic ones).
        LATIN_TO_CYR = {
            "a": "а",  # Cyrillic а looks like Latin a
            "y": "у",  # Cyrillic у looks like Latin y
            "e": "е",
            "p": "р",
            "c": "с",
            "x": "х",
            "o": "о",
            "k": "к",
            "B": "В",
            "A": "А",
            "E": "Е",
            "O": "О",
            "K": "К",
            "H": "Н",
            "P": "Р",
            "C": "С",
            "T": "Т",
            "M": "М",
        }
        # Each missing entry's Latin form should map to a canonical name.
        for name, month in missing_in_table:
            cyr = "".join(LATIN_TO_CYR.get(c, c) for c in name)
            assert cyr in canonical_names, (
                f"Bulgarian legacy entry {name!r} (Latin script) doesn't map "
                f"to any canonical Cyrillic month name; got {cyr!r}"
            )
            # And the mapped form should map to the same month.
            assert TBL[code].month_to_int.get(cyr) == month
        # Acceptable — Latin-script legacy variants are not in the canonical
        # table by design.
        missing_in_table = set()

    assert not missing_in_table, (
        f"Language {code!r}: legacy dicts have entries not in "
        f"MONTHS_BY_LANGUAGE: {sorted(missing_in_table)[:5]}"
    )
    # Extra entries are tolerated (it just means we added variants the
    # legacy code didn't expose) — flag them so we can audit manually if
    # the test fails for legitimate reasons.
    if extra_in_table:
        # Allow, but assert they're sensible: in the table's variant data.
        extra_names = {name for name, _ in extra_in_table}
        valid_names = (
            set(data.full) | set(data.full_lc)
            | set(data.abbrev) | set(data.abbrev_lc)
        )
        if data.genitive:
            valid_names |= set(data.genitive)
        if data.genitive_lc:
            valid_names |= set(data.genitive_lc)
        if data.short:
            valid_names |= set(data.short)
        if data.short_lc:
            valid_names |= set(data.short_lc)
        orphan = extra_names - valid_names
        assert not orphan, (
            f"Language {code!r}: extra entries in month_to_int not present "
            f"in any variant: {orphan}"
        )


def test_get_months_unknown_code_raises():
    with pytest.raises(ValueError, match="Unknown language code"):
        get_months("xx")
