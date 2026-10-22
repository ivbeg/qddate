"""English dates without a year (Q9 of ``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

``May 5``, ``5 May`` and ``Jan 1`` carry the ``noyear`` flag, like ``05.12``
and ``5 мая``: the year comes from ``reference=`` (the current year by
default), ``prefer="past"`` moves a date after the reference to the previous
year, and ``allow_no_year=False`` skips them.
"""
import datetime

import pytest

from qddate import DateParser

REFERENCE = datetime.datetime(2026, 10, 22, 12, 0)


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.mark.parametrize("text, month, day", [
    ("May 5", 5, 5),
    ("5 May", 5, 5),
    ("Jan 1", 1, 1),
    ("May 5th", 5, 5),
    ("5th May", 5, 5),
    ("December 25", 12, 25),
    ("25 December", 12, 25),
    ("Dec. 25", 12, 25),
    ("Sept. 5", 9, 5),
    ("Sept 5", 9, 5),
    ("SEPT 5", 9, 5),
    ("JAN 1", 1, 1),
    ("1st Mar", 3, 1),
])
def test_english_date_without_year(parser, text, month, day):
    match = parser.match_typed(text, reference=REFERENCE)
    assert match is not None
    assert match.datetime == datetime.datetime(2026, month, day)
    assert match.has_year is False
    assert match.language == "en"
    assert match.precision == "day"
    assert match.span == (0, len(text))


@pytest.mark.parametrize("text, expected", [
    ("May 5 at 3:45 PM", datetime.datetime(2026, 5, 5, 15, 45)),
    ("Dec 25, 10:00", datetime.datetime(2026, 12, 25, 10, 0)),
    ("5 May 14h30", datetime.datetime(2026, 5, 5, 14, 30)),
    ("14:30, May 5", datetime.datetime(2026, 5, 5, 14, 30)),
    ("May 5, 22:30", datetime.datetime(2026, 5, 5, 22, 30)),
])
def test_time_after_or_before(parser, text, expected):
    assert parser.parse(text, reference=REFERENCE) == expected


def test_prefer_past_moves_a_later_date_to_the_previous_year(parser):
    reference = datetime.datetime(2026, 1, 3)
    assert parser.parse("Dec 25", reference=reference, prefer="past") == datetime.datetime(2025, 12, 25)
    assert parser.parse("Jan 1", reference=reference, prefer="past") == datetime.datetime(2026, 1, 1)


def test_allow_no_year_false_skips_them(parser):
    assert parser.match("May 5", allow_no_year=False) is None
    assert parser.match("5 May", allow_no_year=False) is None
    assert parser.match_all("Sept. 5", allow_no_year=False) == []


@pytest.mark.parametrize("text", [
    # "may" and "march" are words: lower-case month names are not read.
    "may 5",
    "5 may",
    # A letter after the month, a digit after the day.
    "5 Marketing tips",
    "Mayor 5",
    "May 2022",
    "May 50",
    # A two-digit year follows: not a date without a year.
    "May 5, 22",
    "May 5th, 21",
])
def test_not_a_date_without_year(parser, text):
    assert parser.match(text) is None


@pytest.mark.parametrize("text, key", [
    ("May 5, 2022", "dt:date:date_eng2_short"),
    ("5 May 2022", "dt:date:date_eng1"),
    ("5 May 22", "dt:date:date_eng4_short"),
])
def test_a_written_year_wins(parser, text, key):
    match = parser.match(text)
    assert match["pattern"]["key"] == key
    assert "year" in match["values"]
