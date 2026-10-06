"""Tests for ``DateParser.parse_relative()``.

The relative-date grammar is opt-in (an explicit method call) and the
``relative=True`` constructor flag controls whether ``parse()`` also tries it.
"""

import datetime

from qddate import DateParser

REFERENCE = datetime.datetime(2026, 6, 15, 12, 0, 0)


def test_parse_relative_today():
    p = DateParser()
    result = p.parse_relative("today", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 15, 12, 0, 0)


def test_parse_relative_yesterday():
    p = DateParser()
    result = p.parse_relative("yesterday", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 14, 12, 0, 0)


def test_parse_relative_tomorrow():
    p = DateParser()
    result = p.parse_relative("tomorrow", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 16, 12, 0, 0)


def test_parse_relative_n_days_ago_digit():
    p = DateParser()
    result = p.parse_relative("3 days ago", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 12, 12, 0, 0)


def test_parse_relative_n_days_ago_word():
    p = DateParser()
    result = p.parse_relative("three days ago", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 12, 12, 0, 0)


def test_parse_relative_in_n_days():
    p = DateParser()
    result = p.parse_relative("in 5 days", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 20, 12, 0, 0)


def test_parse_relative_n_weeks_ago():
    p = DateParser()
    result = p.parse_relative("2 weeks ago", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 1, 12, 0, 0)


def test_parse_relative_n_months_ago():
    p = DateParser()
    result = p.parse_relative("1 month ago", reference=REFERENCE)
    assert result == datetime.datetime(2026, 5, 15, 12, 0, 0)


def test_parse_relative_n_years_ago():
    p = DateParser()
    result = p.parse_relative("1 year ago", reference=REFERENCE)
    assert result.year == 2025


def test_parse_relative_russian_today():
    p = DateParser()
    result = p.parse_relative("сегодня", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 15, 12, 0, 0)


def test_parse_relative_russian_yesterday():
    p = DateParser()
    result = p.parse_relative("вчера", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 14, 12, 0, 0)


def test_parse_relative_russian_tomorrow():
    p = DateParser()
    result = p.parse_relative("завтра", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 16, 12, 0, 0)


def test_parse_relative_russian_n_days_ago():
    p = DateParser()
    result = p.parse_relative("3 дня назад", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 12, 12, 0, 0)


def test_parse_relative_russian_cherez_n_days():
    p = DateParser()
    result = p.parse_relative("через 5 дней", reference=REFERENCE)
    assert result == datetime.datetime(2026, 6, 20, 12, 0, 0)


def test_parse_relative_returns_none_for_non_relative_input():
    p = DateParser()
    assert p.parse_relative("totally random text", reference=REFERENCE) is None
    assert p.parse_relative("6 Jan 2009", reference=REFERENCE) is None
    assert p.parse_relative("", reference=REFERENCE) is None


def test_parse_relative_default_reference_is_now():
    """When no reference is provided, ``parse_relative`` defaults to ``now()``."""
    p = DateParser()
    before = datetime.datetime.now()
    result = p.parse_relative("today")
    after = datetime.datetime.now()
    assert before.date() <= result.date() <= after.date()


def test_parse_does_not_match_relative_by_default():
    """Default ``parse()`` does NOT match relative phrases (back-compat)."""
    p = DateParser()
    assert p.parse("today") is None
    assert p.parse("yesterday") is None
    assert p.parse("3 days ago") is None
