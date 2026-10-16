"""Regression coverage for Romanian month-name parsing."""

import datetime
import json
from pathlib import Path

import pytest

from qddate import DateParser
from qddate.patterns import SUPPORTED_LANGUAGES

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "romanian_dates.json"
ROMANIAN_DATES = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def parser_ro():
    return DateParser(languages="ro")


@pytest.mark.parametrize("entry", ROMANIAN_DATES["full_months"])
@pytest.mark.parametrize("case", ["lower", "title"])
def test_all_full_romanian_month_names(parser_ro, entry, case):
    text = f"15 {entry[case]} 2024"
    assert parser_ro.parse(text) == datetime.datetime(2024, entry["month"], 15)


@pytest.mark.parametrize("entry", ROMANIAN_DATES["abbreviated_months"])
@pytest.mark.parametrize("case", ["lower", "title"])
def test_all_abbreviated_romanian_month_names(parser_ro, entry, case):
    text = f"15 {entry[case]} 2024"
    assert parser_ro.parse(text) == datetime.datetime(2024, entry["month"], 15)


@pytest.mark.parametrize("entry", ROMANIAN_DATES["listing_regressions"])
def test_data_gov_ro_listing_regressions(parser_ro, entry):
    expected = datetime.datetime(entry["year"], entry["month"], entry["day"])
    assert parser_ro.parse(entry["text"]) == expected


def test_default_parser_detects_distinct_romanian_month():
    parser = DateParser()
    result = parser.match("19 Februarie 2026")
    assert result is not None
    assert result["pattern"]["language"] == "ro"
    assert parser.parse("4 decembrie 2025") == datetime.datetime(2025, 12, 4)


def test_shared_month_uses_romanian_metadata_when_filtered(parser_ro):
    result = parser_ro.match("21 Mai 2026")
    assert result is not None
    assert result["pattern"]["language"] == "ro"
    assert result["pattern"]["basekey"].startswith("dt:date:ro_")


def test_generated_time_and_trailing_variants_inherit_metadata(parser_ro):
    text = "31 Martie 2025, 14:30 actualizare"
    result = parser_ro.match(text)
    assert result is not None
    assert result["pattern"]["language"] == "ro"
    assert result["pattern"]["separator"] == "space"
    assert parser_ro.parse(text) == datetime.datetime(2025, 3, 31, 14, 30)


def test_abbreviation_period_is_required(parser_ro):
    assert parser_ro.parse("23 apr 2025") is None
    assert parser_ro.parse("23 apr. 2025") == datetime.datetime(2025, 4, 23)


def test_romanian_filter_excludes_other_languages(parser_ro):
    assert parser_ro.parse("21 janvier 2026") is None
    assert parser_ro.parse("21 Dezember 2026") is None


def test_supported_languages_include_ro_exactly_once():
    assert SUPPORTED_LANGUAGES.count("ro") == 1
    assert len(SUPPORTED_LANGUAGES) == 14
