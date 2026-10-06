import datetime

from qddate import DateParser
from qddate.patterns import SUPPORTED_LANGUAGES
from qddate.patterns.uk import (
    UK_MONTHS,
    UK_MONTHS_GEN,
    UK_MONTHS_GEN_LC,
    UK_MONTHS_LC,
    UK_MONTHS_SHORT,
    UK_MONTHS_SHORT_LC,
)


def test_all_ukrainian_month_forms_parse():
    parser = DateParser(languages="uk")
    for month_index in range(12):
        for names in (UK_MONTHS, UK_MONTHS_LC, UK_MONTHS_GEN, UK_MONTHS_GEN_LC,
                      UK_MONTHS_SHORT, UK_MONTHS_SHORT_LC):
            value = parser.parse("15 %s 2024" % names[month_index])
            assert value == datetime.datetime(2024, month_index + 1, 15)


def test_ukrainian_news_style_date():
    parser = DateParser()
    assert parser.parse("21 травня 2026") == datetime.datetime(2026, 5, 21)
    assert parser.parse("19 лютого 2026") == datetime.datetime(2026, 2, 19)


def test_ukrainian_detection_prefers_ukrainian_patterns():
    parser = DateParser()
    matches = parser.match("21 травня 2026")
    assert matches is not None
    assert matches["pattern"]["language"] == "uk"


def test_ukrainian_language_is_supported():
    assert "uk" in SUPPORTED_LANGUAGES
    assert DateParser(languages="ru").parse("21 травня 2026") is None
