"""Time-of-day forms added in 1.1.0 (Q5–Q8 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

- Q5: the 12-hour clock after a date, ``AM``/``PM``/``a.m.``/``p.m.``.
- Q6: the time before the date, separated by ``,``, ``|``, ``-`` or a space.
- Q7: zones after the time: ``+03:00``, ``Z``, ``GMT``/``UTC`` with an offset
  and abbreviations (``MSK``/``МСК``, ``CET``, ``BST``, ``PDT``, …).
- Q8: ``14h30`` / ``14 h 30``.

Before, these lost the time (the date matched alone and ``parse()`` gave
midnight), returned ``None`` (time first), or ignored the zone.
"""
import datetime

import pytest

from qddate import DateParser
from qddate.qdparser import parse_timezone

UTC = datetime.timezone.utc


def _tz(hours, minutes=0):
    return datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.fixture(scope="module")
def tz_parser():
    return DateParser(tz_aware=True)


# --- Q5: 12-hour clock -------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("May 5, 2022 at 3:45 PM", datetime.datetime(2022, 5, 5, 15, 45)),
    ("May 5, 2022 3:45 pm", datetime.datetime(2022, 5, 5, 15, 45)),
    ("May 5, 2022 3:45PM", datetime.datetime(2022, 5, 5, 15, 45)),
    ("May 5, 2022, 3:45 p.m.", datetime.datetime(2022, 5, 5, 15, 45)),
    ("5 May 2022 11:05:09 A.M.", datetime.datetime(2022, 5, 5, 11, 5, 9)),
    ("May 5, 2022 12:00 AM", datetime.datetime(2022, 5, 5, 0, 0)),
    ("May 5, 2022 12:30 PM", datetime.datetime(2022, 5, 5, 12, 30)),
    ("May 5, 2022 at 3 p.m.", datetime.datetime(2022, 5, 5, 15, 0)),
    ("5/5/2022 3:45 PM", datetime.datetime(2022, 5, 5, 15, 45)),
])
def test_twelve_hour_clock(parser, text, expected):
    assert parser.parse(text) == expected


def test_twelve_hour_values_are_24_hour_numbers(parser):
    """``match()`` values stay numbers: the hour is converted and no
    ``ampm`` key is added, so callers that ``int()`` every value keep working."""
    values = parser.match("May 5, 2022 at 3:45 PM")["values"].as_dict()
    assert values["hour"] == "15"
    assert "ampm" not in values


@pytest.mark.parametrize("text, expected", [
    # 13 is not a 12-hour hour: the 24-hour reading wins, PM is left over.
    ("5 May 2022 13:00 PM", datetime.datetime(2022, 5, 5, 13, 0)),
    # A word starting with "am"/"pm" is not a marker.
    ("May 5, 2022 at 3:45 PMx", datetime.datetime(2022, 5, 5)),
])
def test_twelve_hour_clock_rejects(parser, text, expected):
    assert parser.parse(text) == expected


# --- Q6: time before the date -----------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("12:30, 5 мая 2022", datetime.datetime(2022, 5, 5, 12, 30)),
    ("12:30 05.05.2022", datetime.datetime(2022, 5, 5, 12, 30)),
    ("14:30 | 5 May 2022", datetime.datetime(2022, 5, 5, 14, 30)),
    ("14:30 - 5 May 2022", datetime.datetime(2022, 5, 5, 14, 30)),
    ("12:30:15 05.05.2022", datetime.datetime(2022, 5, 5, 12, 30, 15)),
    ("3:45 PM, May 5, 2022", datetime.datetime(2022, 5, 5, 15, 45)),
    ("14h30, le 5 mai 2022", datetime.datetime(2022, 5, 5, 14, 30)),
    ("12:30 05.05.2022 Новости", datetime.datetime(2022, 5, 5, 12, 30)),
])
def test_time_before_date(parser, text, expected):
    assert parser.parse(text) == expected


def test_time_before_date_key(parser):
    assert parser.match("12:30 05.05.2022")["pattern"]["key"] == "dt:date:date_2:time_left"


@pytest.mark.parametrize("text", [
    "12:30 -15 комментариев",
    "10:00 Zürich",
    "12:30",
])
def test_time_without_date(parser, text):
    assert parser.match(text) is None


# --- Q7: zones ---------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("2022-05-05T10:00:00+03:00", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(3))),
    ("2022-05-05T10:00:00Z", datetime.datetime(2022, 5, 5, 10, tzinfo=UTC)),
    ("2022-05-05T10:00+03:00", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(3))),
    ("05.05.2022 10:00 GMT+3", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(3))),
    ("05.05.2022 10:00 UTC-05:30", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(-5, -30))),
    ("5 мая 2022 г., 12:30 МСК", datetime.datetime(2022, 5, 5, 12, 30, tzinfo=_tz(3))),
    ("5 мая 2022 в 12:30 мск", datetime.datetime(2022, 5, 5, 12, 30, tzinfo=_tz(3))),
    ("05.05.2022 10:00 BST", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(1))),
    ("05.05.2022 10:00 CEST", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(2))),
    ("May 5, 2022 at 3:45 PM PDT", datetime.datetime(2022, 5, 5, 15, 45, tzinfo=_tz(-7))),
    ("Thu, 05 May 2022 10:00:00 GMT", datetime.datetime(2022, 5, 5, 10, tzinfo=UTC)),
    ("5 May 2022 10:00 -0500", datetime.datetime(2022, 5, 5, 10, tzinfo=_tz(-5))),
    ("12:30 МСК, 5 мая 2022", datetime.datetime(2022, 5, 5, 12, 30, tzinfo=_tz(3))),
    # The legacy forms keep working.
    ("01.12.2009 14:53:12 +0000", datetime.datetime(2009, 12, 1, 14, 53, 12, tzinfo=UTC)),
    ("01.12.2009 14:53:12 +300", datetime.datetime(2009, 12, 1, 14, 53, 12, tzinfo=_tz(3))),
])
def test_zone_after_time(tz_parser, text, expected):
    result = tz_parser.parse(text)
    assert result == expected
    assert result.utcoffset() == expected.utcoffset()


def test_zone_is_kept_as_written(parser):
    values = parser.match("2022-05-05T10:00:00+03:00")["values"]
    assert values["timezone"] == "+03:00"


def test_zone_ignored_without_tz_aware(parser):
    assert parser.parse("2022-05-05T10:00:00+03:00") == datetime.datetime(2022, 5, 5, 10)


@pytest.mark.parametrize("text, expected", [
    # The French verb "est" is not US Eastern time: abbreviations are capitals.
    ("5 May 2022 10:00 est la date", datetime.datetime(2022, 5, 5, 10)),
    # A word starting with Z is not "Zulu".
    ("05.05.2022 10:00 Zürich", datetime.datetime(2022, 5, 5, 10)),
])
def test_words_after_time_are_not_zones(tz_parser, text, expected):
    result = tz_parser.parse(text)
    assert result == expected
    assert result.tzinfo is None


@pytest.mark.parametrize("text, offset, name", [
    ("Z", datetime.timedelta(0), "UTC"),
    ("UTC", datetime.timedelta(0), "UTC"),
    ("GMT", datetime.timedelta(0), "UTC"),
    ("+0300", datetime.timedelta(hours=3), None),
    ("+03:00", datetime.timedelta(hours=3), None),
    ("-0530", -datetime.timedelta(hours=5, minutes=30), None),
    ("+300", datetime.timedelta(hours=3), None),
    ("GMT+3", datetime.timedelta(hours=3), None),
    ("UTC-05:30", -datetime.timedelta(hours=5, minutes=30), None),
    ("GMT+0300", datetime.timedelta(hours=3), None),
    ("MSK", datetime.timedelta(hours=3), "MSK"),
    ("МСК", datetime.timedelta(hours=3), "МСК"),
    ("PST", datetime.timedelta(hours=-8), "PST"),
    ("ACST", datetime.timedelta(hours=9, minutes=30), "ACST"),
])
def test_parse_timezone(text, offset, name):
    tz = parse_timezone(text)
    assert tz.utcoffset(None) == offset
    if name is not None:
        assert tz.tzname(None) == name


@pytest.mark.parametrize("text", [None, "", "XYZ", "+2500", "+0370", "GMT+", "+"])
def test_parse_timezone_rejects(text):
    assert parse_timezone(text) is None


# --- Q8: "14h30" ------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("05/05/2022 14h30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("le 5 mai 2022 à 14h30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("le 5 mai 2022 à 14 h 30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("5 de maio de 2022 às 9h05", datetime.datetime(2022, 5, 5, 9, 5)),
    ("05/05/2022 14H30", datetime.datetime(2022, 5, 5, 14, 30)),
])
def test_h_time(parser, text, expected):
    assert parser.parse(text) == expected


def test_h_time_needs_minutes(parser):
    """"à 14h" alone is not read: "3 h de route" would read as a time."""
    assert parser.parse("le 5 mai 2022 à 14h") == datetime.datetime(2022, 5, 5)


# --- Words before the time ---------------------------------------------------

@pytest.mark.parametrize("text, expected", [
    ("5. Mai 2022 um 14:30 Uhr", datetime.datetime(2022, 5, 5, 14, 30)),
    ("5 de mayo de 2022 a las 14:30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("5 maggio 2022 alle 14:30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("5 mei 2022 om 14:30", datetime.datetime(2022, 5, 5, 14, 30)),
    # A numeric date has no language: every language's word is accepted.
    ("05.05.2022 в 12:30", datetime.datetime(2022, 5, 5, 12, 30)),
    ("05/05/2022 at 12:30", datetime.datetime(2022, 5, 5, 12, 30)),
])
def test_word_before_time(parser, text, expected):
    assert parser.parse(text) == expected


def test_word_of_another_language_before_time(parser):
    """The Russian "в" stays Russian: after an English month name it is not
    accepted (see ``tests/test_regressions_2026_10.py``)."""
    assert parser.parse("16 May 2009 в 14:10") == datetime.datetime(2009, 5, 16)


def test_pipe_between_date_and_minutes(parser):
    """``:time_1`` accepts "|" and the ISO "T" like ``:time_2`` already did;
    the time was dropped for "21 September 1994 | 11:08"."""
    assert parser.parse("21 September 1994 | 11:08") == datetime.datetime(1994, 9, 21, 11, 8)
    assert parser.parse("2022-05-05T10:00") == datetime.datetime(2022, 5, 5, 10, 0)
