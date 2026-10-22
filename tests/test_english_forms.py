"""English abbreviations and forms (Q10 of ``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

``Sept. 5, 2022``, ``Sep 5th 2022`` and ``5-May-2022`` returned ``None``.
"""
import datetime

import pytest

from qddate import DateParser


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.mark.parametrize("text, expected, key", [
    # An abbreviated month with a dot, AP style.
    ("Sept. 5, 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    ("Dec. 25, 2022", datetime.datetime(2022, 12, 25), "dt:date:date_eng5"),
    ("Sep. 5 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    ("SEPT. 5, 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    # An ordinal day after an abbreviated month.
    ("Sep 5th 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    ("Sep 5th, 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    ("Sept 5th 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng5"),
    # An ordinal day before "Sept" or an abbreviation with a dot.
    ("5th Sept 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng6"),
    ("5th Sept. 2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng6"),
    ("5th Dec. 2022", datetime.datetime(2022, 12, 5), "dt:date:date_eng6"),
    # Dashes with a four-digit year.
    ("5-May-2022", datetime.datetime(2022, 5, 5), "dt:date:date_eng4"),
    ("05-May-2022", datetime.datetime(2022, 5, 5), "dt:date:date_eng4"),
    ("5-may-2022", datetime.datetime(2022, 5, 5), "dt:date:date_eng4"),
    ("5-Sept-2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng4"),
    ("5-September-2022", datetime.datetime(2022, 9, 5), "dt:date:date_eng4"),
])
def test_english_form(parser, text, expected, key):
    match = parser.match(text)
    assert match["pattern"]["key"] == key
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text, expected", [
    ("Jan. 1, 2020 at 3 PM", datetime.datetime(2020, 1, 1, 15, 0)),
    ("05-May-2022 10:30", datetime.datetime(2022, 5, 5, 10, 30)),
    ("Sep 5th 2022, 14:10", datetime.datetime(2022, 9, 5, 14, 10)),
])
def test_with_time(parser, text, expected):
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text, key", [
    # Forms that parsed before keep their pattern.
    ("May 5th, 2022", "dt:date:date_eng2"),
    ("Sep 5, 2022", "dt:date:date_eng2_short"),
    ("5th Dec 2022", "dt:date:date_eng_abbrev_postfix"),
    ("5 Dec. 2022", "dt:date:date_eng1_short"),
    ("5-May-22", "dt:date:date_eng4_short"),
])
def test_existing_forms_keep_their_pattern(parser, text, key):
    assert parser.match(text)["pattern"]["key"] == key
