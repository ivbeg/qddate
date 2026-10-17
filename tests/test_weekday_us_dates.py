"""A weekday before a month-first (US) date, as on EU INSPIRE and many US sites."""
import datetime

import pytest

from qddate import DateParser


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.mark.parametrize("text,expected,key", [
    ("Monday, January 31, 2022", datetime.datetime(2022, 1, 31), "dt:date:weekday_eng_us"),
    ("Wednesday, September 30, 2026", datetime.datetime(2026, 9, 30), "dt:date:weekday_eng_us"),
    ("Friday May 1 2026", datetime.datetime(2026, 5, 1), "dt:date:weekday_eng_us"),
    ("Mon, January 31, 2022", datetime.datetime(2022, 1, 31), "dt:date:weekday_eng_wshort_us"),
    ("Mon, Jan 31, 2022", datetime.datetime(2022, 1, 31), "dt:date:weekday_eng_abbrev_wshort_us"),
    ("Tue Feb 1, 2022", datetime.datetime(2022, 2, 1), "dt:date:weekday_eng_abbrev_wshort_us"),
])
def test_weekday_then_month_first(parser, text, expected, key):
    assert parser.parse(text) == expected
    assert parser.match(text)["pattern"]["basekey"] == key


@pytest.mark.parametrize("text,key", [
    ("Monday, 31 January 2022", "dt:date:weekday_eng"),
    ("Thursday, Jun 25, 2026", "dt:date:weekday_eng_abbrev3"),
    ("Mon, 5 Jan 2020", "dt:date:weekday_eng_abbrev2"),
    ("January 31, 2022", "dt:date:date_eng3_nolc"),
])
def test_existing_weekday_patterns_unchanged(parser, text, key):
    assert parser.match(text)["pattern"]["basekey"] == key
