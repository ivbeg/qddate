"""Chinese, Japanese and Korean numeric dates (Q12 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

``2022年5月5日`` and ``2022년 5월 5일`` returned ``None``. The patterns belong
to no language, like the numeric ones.
"""
import datetime

import pytest

from qddate import DateParser

REFERENCE = datetime.datetime(2026, 10, 22, 12, 0)


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.mark.parametrize("text, expected, precision", [
    ("2022年5月5日", datetime.datetime(2022, 5, 5), "day"),
    ("2022年05月05日", datetime.datetime(2022, 5, 5), "day"),
    ("2022年5月5号", datetime.datetime(2022, 5, 5), "day"),
    ("２０２２年５月５日", datetime.datetime(2022, 5, 5), "day"),
    ("2022년 5월 5일", datetime.datetime(2022, 5, 5), "day"),
    ("2022년5월5일", datetime.datetime(2022, 5, 5), "day"),
    # A time of day after the date.
    ("2022年5月5日 14:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日 14:30:15", datetime.datetime(2022, 5, 5, 14, 30, 15), "second"),
    ("2022年5月5日 14時30分", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日14时30分", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日 14時", datetime.datetime(2022, 5, 5, 14, 0), "hour"),
    ("2022年5月5日午後2時30分", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日 下午2:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日 上午9:05", datetime.datetime(2022, 5, 5, 9, 5), "minute"),
    ("2022년 5월 5일 오후 2:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022년 5월 5일 14시 30분", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    # A weekday after the day.
    ("2022年5月5日(木) 14:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022年5月5日（木曜日）", datetime.datetime(2022, 5, 5), "day"),
    ("2022年5月5日 星期四", datetime.datetime(2022, 5, 5), "day"),
    ("2022年5月5日 木曜日 14:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022년 5월 5일 (목) 14:30", datetime.datetime(2022, 5, 5, 14, 30), "minute"),
    ("2022년 5월 5일 목요일", datetime.datetime(2022, 5, 5), "day"),
])
def test_cjk_date(parser, text, expected, precision):
    match = parser.match_typed(text)
    assert match.datetime == expected
    assert match.precision == precision
    assert match.language is None
    assert match.has_year is True


@pytest.mark.parametrize("text, expected", [
    ("5月5日", datetime.datetime(2026, 5, 5)),
    ("12月25日 10:00", datetime.datetime(2026, 12, 25, 10, 0)),
    ("5월 5일", datetime.datetime(2026, 5, 5)),
])
def test_cjk_date_without_year(parser, text, expected):
    match = parser.match_typed(text, reference=REFERENCE)
    assert match.datetime == expected
    assert match.has_year is False
    assert parser.match(text, allow_no_year=False) is None


@pytest.mark.parametrize("text", [
    "2022年13月5日",
    "2022年5月32日",
    "2022 5 5",
])
def test_not_a_cjk_date(parser, text):
    match = parser.match(text)
    assert match is None or not match["pattern"]["key"].startswith("dt:date:date_cjk")


def test_an_afternoon_hour_above_twelve_is_not_read(parser):
    """"午後13時" is not a 12-hour time; the date alone is read."""
    assert parser.parse("2022年5月5日 午後13時") == datetime.datetime(2022, 5, 5)


def test_every_language_hint_tries_them(parser):
    for hint in ("en", "ru", "de", None):
        assert parser.parse("2022年5月5日", languages=hint) == datetime.datetime(2022, 5, 5)


def test_format_date_round_trip(parser):
    match = parser.match_typed("2022年5月5日")
    assert match.format_date() == "2022年05月05日"
    assert parser.parse(match.format_date()) == match.datetime
