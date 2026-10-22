"""Per-call options and the richer ``DateMatch`` added in 1.1.0 (Q14–Q17 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

- Q14: ``languages=`` on ``match()``/``match_all()``/``parse()``/
  ``match_typed()``: a soft preference, one parser for every page language.
- Q15: ``date_order=`` (constructor and call) for ambiguous numeric dates.
- Q16: ``reference=`` and ``prefer=`` for dates without a year.
- Q17: ``DateMatch.span``, ``precision``, ``tzinfo`` and ``has_year``.
"""
import datetime
import warnings

import pytest

from qddate import DateMatch, DateParser
from qddate.qdparser import NOYEAR_ROLLOVER_GRACE


@pytest.fixture(scope="module")
def parser():
    return DateParser()


# --- Q14: languages= per call -----------------------------------------------

def test_language_hint_picks_the_language_of_a_shared_month(parser):
    """"Juni" is German and Dutch; without a hint detection takes Dutch."""
    assert parser.match("18 Juni 1953")["pattern"]["key"] == "dt:date:nl_base"
    assert parser.match("18 Juni 1953", languages="de")["pattern"]["key"] == "dt:date:de_base"
    assert parser.match("18 Juni 1953", languages=["de", "en"])["pattern"]["key"] == "dt:date:de_base"


def test_language_hint_is_soft(parser):
    """A text the hinted languages cannot read is read by the others."""
    assert parser.match("5 мая 2022", languages="en")["pattern"]["key"] == "dt:date:date_rus_lc1"
    # Month first is English (``date_usa``); a Russian hint does not exclude it.
    assert parser.parse("05/13/2022", languages="ru") == datetime.datetime(2022, 5, 13)


def test_language_hint_keeps_numeric_patterns(parser):
    """Language-neutral numeric patterns belong to every hint."""
    assert parser.match("05.05.2022", languages="ru")["pattern"]["key"] == "dt:date:date_2"


@pytest.mark.parametrize("languages", [None, [], "de", ["de"], ("de",), {"de"}])
def test_language_hint_forms(parser, languages):
    assert parser.parse("18 Juni 1953", languages=languages) == datetime.datetime(1953, 6, 18)


def test_language_hint_rejects_unknown_codes(parser):
    with pytest.raises(ValueError, match="Unsupported language"):
        parser.match("18 Juni 1953", languages="xx")
    with pytest.raises(TypeError):
        parser.match("18 Juni 1953", languages=5)


def test_language_hint_on_every_method(parser):
    assert parser.parse("18 Juni 1953", languages="de") == datetime.datetime(1953, 6, 18)
    assert parser.match_typed("18 Juni 1953", languages="de").pattern_key == "dt:date:de_base"
    keys = [m["pattern"]["key"] for m in parser.match_all("18 Juni 1953", languages="de")]
    assert keys[0] == "dt:date:de_base"
    assert list(parser.parse_many(["18 Juni 1953"], languages="de")) == [
        datetime.datetime(1953, 6, 18)]


def test_match_all_lists_hinted_languages_first(parser):
    without = [m["pattern"]["key"] for m in parser.match_all("01/02/2020")]
    hinted = [m["pattern"]["key"] for m in parser.match_all("01/02/2020", languages="ru")]
    assert sorted(without) == sorted(hinted)
    assert "dt:date:date_usa" in hinted
    # date_usa is English: it comes after every match of the hint.
    assert hinted[-1] == "dt:date:date_usa"


def test_language_indexes_are_cached_not_rebuilt():
    parser = DateParser()
    patterns = parser.patterns
    parser.match("18 Juni 1953", languages="de")
    parser.match("5 May 2022", languages=["de"])
    assert parser.patterns is patterns
    assert list(parser._language_indexes) == [frozenset({"de"})]
    parser.match("5 May 2022", languages=["en", "de"])
    assert set(parser._language_indexes) == {frozenset({"de"}), frozenset({"en", "de"})}


def test_language_hint_with_session():
    parser = DateParser()
    parser.start_session(["dt:date:de_base", "dt:date:nl_base"])
    assert parser.match("18 Juni 1953", languages="de")["pattern"]["key"] == "dt:date:de_base"
    assert parser.match("05.05.2022", languages="de") is None
    parser.end_session()
    assert parser.match("05.05.2022", languages="de")["pattern"]["key"] == "dt:date:date_2"


def test_language_hint_on_legacy_filter():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        parser = DateParser(use_fingerprint=False)
    assert parser.match("18 Juni 1953", languages="de")["pattern"]["key"] == "dt:date:de_base"
    assert parser.match("5 мая 2022", languages="en")["pattern"]["key"] == "dt:date:date_rus_lc1"


# --- Q15: date_order= -------------------------------------------------------

@pytest.mark.parametrize("text, date_order, expected", [
    ("05/06/2022", None, datetime.datetime(2022, 6, 5)),
    ("05/06/2022", "DMY", datetime.datetime(2022, 6, 5)),
    ("05/06/2022", "MDY", datetime.datetime(2022, 5, 6)),
    ("05/06/2022", "mdy", datetime.datetime(2022, 5, 6)),
    ("05/06/22", "MDY", datetime.datetime(22, 5, 6)),
    ("05/06/2022 10:30", "MDY", datetime.datetime(2022, 5, 6, 10, 30)),
    # Only an ambiguous date follows the order.
    ("13/05/2022", "MDY", datetime.datetime(2022, 5, 13)),
    ("05/13/2022", "DMY", datetime.datetime(2022, 5, 13)),
    # Dotted dates have no month-first pattern.
    ("05.06.2022", "MDY", datetime.datetime(2022, 6, 5)),
    # Eight digits read year first ("1210-11-12") instead of day first.
    ("12101112", None, datetime.datetime(1112, 10, 12)),
    ("12101112", "YMD", datetime.datetime(1210, 11, 12)),
])
def test_date_order_per_call(parser, text, date_order, expected):
    assert parser.parse(text, date_order=date_order) == expected


def test_date_order_in_constructor():
    parser = DateParser(date_order="MDY")
    assert parser.parse("05/06/2022") == datetime.datetime(2022, 5, 6)
    assert parser.match("05/06/2022")["pattern"]["key"] == "dt:date:date_usa"
    # The call overrides the parser.
    assert parser.parse("05/06/2022", date_order="DMY") == datetime.datetime(2022, 6, 5)


def test_date_order_orders_match_all(parser):
    keys = [m["pattern"]["key"] for m in parser.match_all("01/02/2020", date_order="MDY")]
    assert keys[0] == "dt:date:date_usa"
    assert "dt:date:date_1" in keys


def test_date_order_does_not_beat_a_longer_match(parser):
    """The order only decides between matches of the same length."""
    assert parser.parse("05/06/2022 10:30", date_order="MDY") == datetime.datetime(2022, 5, 6, 10, 30)
    assert parser.parse("2022-05-06", date_order="MDY") == datetime.datetime(2022, 5, 6)


@pytest.mark.parametrize("value", ["DM", "", 1])
def test_date_order_rejects(parser, value):
    with pytest.raises(ValueError, match="date_order"):
        parser.parse("05/06/2022", date_order=value)
    with pytest.raises(ValueError, match="date_order"):
        DateParser(generate=False, date_order=value)


# --- Q16: reference= and prefer= ---------------------------------------------

def test_reference_gives_the_year(parser):
    ref = datetime.datetime(2020, 3, 1)
    assert parser.parse("05.12", reference=ref) == datetime.datetime(2020, 12, 5)
    assert parser.parse("4 Сентября в 04:06:33", reference=ref) == datetime.datetime(
        2020, 9, 4, 4, 6, 33)


def test_reference_does_not_change_dates_with_a_year(parser):
    assert parser.parse("05.12.2009", reference=datetime.datetime(2020, 1, 1)) == \
        datetime.datetime(2009, 12, 5)


@pytest.mark.parametrize("text, reference, prefer, expected", [
    # Read on 2 January, "31.12" is last December.
    ("31.12", datetime.datetime(2026, 1, 2), "past", datetime.datetime(2025, 12, 31)),
    ("31.12", datetime.datetime(2026, 1, 2), None, datetime.datetime(2026, 12, 31)),
    # Within the grace a date stays in the reference year (timezones).
    ("22.10", datetime.datetime(2026, 10, 21), "past", datetime.datetime(2026, 10, 22)),
    ("24.10", datetime.datetime(2026, 10, 21), "past", datetime.datetime(2025, 10, 24)),
    ("05.10", datetime.datetime(2026, 10, 21), "past", datetime.datetime(2026, 10, 5)),
    # Event listings: a passed date is next year's.
    ("05.01", datetime.datetime(2026, 12, 20), "future", datetime.datetime(2027, 1, 5)),
    ("25.12", datetime.datetime(2026, 12, 20), "future", datetime.datetime(2026, 12, 25)),
    # An aware reference is compared by its wall clock.
    ("31.12", datetime.datetime(2026, 1, 2, tzinfo=datetime.timezone.utc), "past",
     datetime.datetime(2025, 12, 31)),
    # 29 February does not exist the year before.
    ("29.02", datetime.datetime(2024, 1, 15), "past", None),
])
def test_prefer(parser, text, reference, prefer, expected):
    assert parser.parse(text, reference=reference, prefer=prefer) == expected


def test_prefer_grace_is_two_days():
    assert NOYEAR_ROLLOVER_GRACE == datetime.timedelta(days=2)


def test_prefer_without_reference_uses_now(parser):
    now = datetime.datetime.now()
    tomorrow_a_year_on = (now + datetime.timedelta(days=10)).strftime("%d.%m")
    result = parser.parse(tomorrow_a_year_on, prefer="past")
    assert result is not None and result < now


def test_prefer_rejects(parser):
    with pytest.raises(ValueError, match="prefer"):
        parser.parse("05.12", prefer="recent")
    with pytest.raises(ValueError, match="prefer"):
        parser.match_typed("05.12", prefer="recent")


def test_reference_on_match_typed(parser):
    result = parser.match_typed("31.12", reference=datetime.datetime(2026, 1, 2), prefer="past")
    assert result.datetime == datetime.datetime(2025, 12, 31)
    assert result.has_year is False


def test_parse_relative_reference(parser):
    ref = datetime.datetime(2020, 5, 5, 12, 0)
    assert parser.parse_relative("yesterday", reference=ref) == datetime.datetime(2020, 5, 4, 12, 0)


# --- Q17: DateMatch fields ---------------------------------------------------

@pytest.mark.parametrize("text, span, precision, has_year", [
    ("5 May 2022", (0, 10), "day", True),
    ("5 May 2022 and more text", (0, 10), "day", True),
    ("5 May 2022 14:10", (0, 16), "minute", True),
    ("01.03.2009 14:53:12", (0, 19), "second", True),
    ("May 5, 2022 at 3 PM", (0, 19), "hour", True),
    ("05.12", (0, 5), "day", False),
    ("4 Сентября в 04:06:33", (0, 21), "second", False),
    ("12:30, 5 мая 2022 Новости", (0, 17), "minute", True),
    # The span counts in the original text, tabs included.
    ("5\tMay 2022 more", (0, 10), "day", True),
])
def test_date_match_fields(parser, text, span, precision, has_year):
    result = parser.match_typed(text)
    assert result.span == span
    assert result.precision == precision
    assert result.has_year is has_year
    assert result.raw == text


def test_date_match_tzinfo_without_tz_aware(parser):
    """``tzinfo`` reports the written zone even when ``datetime`` stays naive."""
    result = parser.match_typed("5 мая 2022 в 12:30 МСК")
    assert result.datetime.tzinfo is None
    assert result.tzinfo.utcoffset(None) == datetime.timedelta(hours=3)
    assert result.tzinfo.tzname(None) == "МСК"
    assert parser.match_typed("5 мая 2022 в 12:30").tzinfo is None


def test_date_match_tzinfo_with_tz_aware():
    result = DateParser(tz_aware=True).match_typed("2022-05-05T10:00:00Z")
    assert result.datetime.tzinfo == datetime.timezone.utc
    assert result.tzinfo == datetime.timezone.utc


def test_date_match_to_dict_has_new_fields(parser):
    d = parser.match_typed("5 May 2022 14:10").to_dict()
    assert d["span"] == (0, 16)
    assert d["precision"] == "minute"
    assert d["tzinfo"] is None
    assert d["has_year"] is True


def test_date_match_old_constructor_still_works():
    m = DateMatch(datetime.datetime(2020, 1, 1), "dt:date:date_1", None, "%d/%m/%Y", "01/01/2020")
    assert m.span == (0, 0)
    assert m.precision == "day"
    assert m.tzinfo is None
    assert m.has_year is True
