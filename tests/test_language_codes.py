"""The ISO 639-1 code ``cs`` for Czech (Q13 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

qddate files Czech under ``cz`` (a country code). Every API that takes a
language code accepts ``cs`` as well; results keep reporting ``cz``.
"""
import datetime

import pytest

from qddate import DateParser
from qddate.patterns import (
    LANGUAGE_ALIASES,
    PATTERNS_CZ,
    SUPPORTED_LANGUAGES,
    get_patterns_for_languages,
    normalize_language,
)
from qddate.patterns.months import get_months

CZECH = "5. května 2022"


def test_alias_table():
    assert LANGUAGE_ALIASES == {"cs": "cz"}
    assert normalize_language("cs") == "cz"
    assert normalize_language("cz") == "cz"
    assert normalize_language("en") == "en"
    # The canonical list is unchanged.
    assert "cs" not in SUPPORTED_LANGUAGES
    assert "cz" in SUPPORTED_LANGUAGES


def test_get_patterns_for_languages():
    assert get_patterns_for_languages("cs") == PATTERNS_CZ
    assert get_patterns_for_languages(["cs", "cz"]) == PATTERNS_CZ
    keys = {p["key"] for p in get_patterns_for_languages(["cs", "de"])}
    assert "dt:date:cz_gen_lc" in keys and "dt:date:de_base" in keys


def test_get_months():
    assert get_months("cs") is get_months("cz")


@pytest.mark.parametrize("languages", ["cs", ["cs"], ("cs", "de"), ["cs", "cz"]])
def test_constructor(languages):
    parser = DateParser(languages=languages)
    assert parser.parse(CZECH) == datetime.datetime(2022, 5, 5)
    # Detection never narrows below the allow-list, with either code.
    assert parser._language_allowlist >= {"cz"}
    assert "cs" not in parser._language_allowlist


@pytest.mark.parametrize("languages", ["cs", ["cs"], {"cs", "de"}])
def test_call_hint(languages):
    parser = DateParser()
    match = parser.match_typed(CZECH, languages=languages)
    assert match.datetime == datetime.datetime(2022, 5, 5)
    # The language of a pattern stays "cz".
    assert match.language == "cz"
    assert parser.parse(CZECH, languages=languages) == datetime.datetime(2022, 5, 5)
    assert parser.match_all(CZECH, languages=languages)[0]["pattern"]["language"] == "cz"


def test_hint_with_either_code_runs_the_same_patterns():
    parser = DateParser()
    parser.match(CZECH, languages="cs")
    parser.match(CZECH, languages="cz")
    # One cached index for the canonical set, not one per spelling.
    assert set(parser._language_indexes) == {frozenset({"cz"})}


def test_unknown_codes_still_raise():
    with pytest.raises(ValueError, match="Unsupported language"):
        DateParser(languages="cze")
    with pytest.raises(ValueError, match="Unsupported language"):
        DateParser().match(CZECH, languages="xx")
    with pytest.raises(ValueError, match="Unsupported language"):
        get_patterns_for_languages(["cs", "xx"])
