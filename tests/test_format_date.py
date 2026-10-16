"""Round-trip tests for ``format_date()``."""

import datetime

import pytest

import qddate
from qddate import DateMatch, DateParser, format_date
from qddate.qdparser import format_date as _format_date_module


@pytest.fixture
def parser():
    return DateParser()


def test_module_level_format_date_roundtrip(parser):
    """Module-level format_date accepts base pattern keys (use the parser
    instance method for generated keys)."""
    match = parser.match("6 Jan 2009")
    assert match is not None
    base_key = match["pattern"]["key"]
    # Strip any ":time_N" / ":t_right" / ":text_N" suffix to get the base key.
    for suffix in (":time_1", ":time_2", ":time_3", ":t_right", ":text_1", ":text_2"):
        if base_key.endswith(suffix):
            base_key = base_key[: -len(suffix)]
            break
    result = _format_date_module(datetime.datetime(2009, 1, 6), pattern_key=base_key)
    # The formatted string should contain the day, English month abbrev, and year.
    assert "6" in result and "Jan" in result and "2009" in result


def test_match_format_date(parser):
    m = parser.match_typed("6 Jan 2009")
    assert isinstance(m, DateMatch)
    out = m.format_date()
    # Round-trip — `parse()` of the formatted string returns the same datetime.
    rt = parser.parse(out)
    assert rt == m.datetime


def test_russian_locale_roundtrip(parser):
    m = parser.match_typed("05 Января 2003")
    assert m is not None
    # `DateMatch.format_date()` uses the format string attached to the match;
    # round-tripping through parse() should land on the same datetime.
    out = m.format_date()
    rt = parser.parse(out)
    assert rt.year == m.datetime.year
    assert rt.month == m.datetime.month
    assert rt.day == m.datetime.day


def test_unknown_pattern_key_raises():
    with pytest.raises(ValueError, match="not:a:real:key"):
        format_date(datetime.datetime(2020, 1, 1), pattern_key="not:a:real:key")


def test_parser_format_date_instance_method(parser):
    dt = datetime.datetime(2009, 1, 6)
    # Pull a known pattern key from the metadata
    out = parser.format_date(dt, pattern_key="dt:date:date_eng1_short")
    assert "6" in out and "Jan" in out and "2009" in out


def test_format_date_exposed_via_qddate_package():
    assert qddate.format_date is _format_date_module


def test_empty_format_falls_back_to_isoformat(parser):
    # Construct a DateMatch by hand with empty format string to exercise the
    # fallback path.
    m = DateMatch(
        datetime=datetime.datetime(2020, 1, 2, 0, 0),
        pattern_key="manual:placeholder",
        language="en",
        format="",  # empty triggers isoformat fallback
        raw="2020-01-02",
    )
    assert m.format_date() == "2020-01-02T00:00:00"
