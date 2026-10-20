"""Regression tests for the 2026-10 corpus verification pass.

- Language detection narrowed to one language when the month name is shared:
  German "Juni"/"Juli" went to Dutch, German "Mai" to French, Bulgarian
  "Август"/"Май"/"Март" to Russian, and the German/Bulgarian patterns never ran.
- ``dt:date:date_rus`` declared ``min=11`` (``9 Мая 1998`` has 10 characters).
- ``dt:date:weekday_rus``/``weekday_rus_lc1`` declared ``max=20``/``25`` although
  they require ``г.``/``года``, and had no ``day``/``month`` result names, so a
  match never became a date.
- ``Воскресенье`` (Sunday) was spelled ``Воскресение``.
- Other length minimums one character too high (``1.мая.1945``, ``Май 6, 2020``,
  ``7 Юли 1918``, ``9 Maj 1997``) and ``date_rus_lc1`` stamped as space-separated
  although it accepts ``17/апреля/1908``.
- ``dt:date:date_rus`` made the year optional without the ``noyear`` flag, so
  ``4 Сентября в 04:06:33`` matched with no year and ``parse()`` returned
  ``None``; it also swallowed a trailing time without naming its parts, so
  ``4 Сентября 2020 в 04:06:33`` parsed to midnight.
- ``DateParser(pivot_year=True)`` was accepted and meant pivot year 1.
- ``match()`` took the highest priority and only then the longest match, so a
  pattern matching just the date beat its time variant on the exact-length
  bonus: ``14 Avril 1995 20:16:12`` parsed without its time and
  ``9 Июня 1927 15:18:03`` without its seconds. Length bounds narrower than
  the grammar (``Mon 1/1/2020``, ``Sábado 1 Maio 2020``) could not be widened
  before.
"""
import datetime
import itertools

import pytest

from qddate import DateParser
from qddate.patterns.months import MONTHS_BY_LANGUAGE
from qddate.qdparser import _lang_month_names


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.fixture(scope="module")
def legacy_parser():
    with pytest.warns(DeprecationWarning):
        return DateParser(use_fingerprint=False)


_SHARED_MONTH_DATES = [
    # German weekday + month name shared with Dutch / French / English
    ("Montag, 18 Juni 1953", datetime.datetime(1953, 6, 18)),
    ("Dienstag, 3 Juni 2020", datetime.datetime(2020, 6, 3)),
    ("Montag, 18 Juli 1953", datetime.datetime(1953, 7, 18)),
    ("Montag, 18 Mai 1953", datetime.datetime(1953, 5, 18)),
    ("Montag, 30 April 2009", datetime.datetime(2009, 4, 30)),
    ("Montag, 5 Oktober 2009", datetime.datetime(2009, 10, 5)),
    ("Freitag, 3. August 2018", datetime.datetime(2018, 8, 3)),
    # Dutch weekday + month name shared with English / German
    ("Maandag, 30 April 2009", datetime.datetime(2009, 4, 30)),
    # No weekday: the first language (French) finds nothing, German does
    ("30. Mai 1953", datetime.datetime(1953, 5, 30)),
    # Bulgarian month names shared with Russian
    ("11 Август 2009", datetime.datetime(2009, 8, 11)),
    ("11 Май 2009", datetime.datetime(2009, 5, 11)),
    ("11 Март 2009", datetime.datetime(2009, 3, 11)),
]


@pytest.mark.parametrize("text,expected", _SHARED_MONTH_DATES)
def test_shared_month_name_parses(parser, text, expected):
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text,expected", _SHARED_MONTH_DATES)
def test_shared_month_name_parses_legacy_filter(legacy_parser, text, expected):
    assert legacy_parser.parse(text) == expected


@pytest.mark.parametrize("text,languages,expected", [
    ("Montag, 18 Juni 1953", "de", datetime.datetime(1953, 6, 18)),
    ("30. Mai 1953", "de", datetime.datetime(1953, 5, 30)),
    ("11 Август 2009", "bg", datetime.datetime(2009, 8, 11)),
])
def test_shared_month_name_with_language_allow_list(text, languages, expected):
    assert DateParser(languages=languages).parse(text) == expected


@pytest.mark.parametrize("text,expected", [
    ("Montag, 18 Juni 1953", ["de"]),
    ("Montag, 18 Mai 1953", ["de"]),
    ("Maandag, 28 Juli 2015", ["nl"]),
    ("Lundi 18 Mai 1953", ["fr"]),
])
def test_weekday_decides_shared_month_name(parser, text, expected):
    assert parser._detect_language(text) == expected


@pytest.mark.parametrize("text,claims", [
    ("30. Mai 1953", ["fr", "de"]),
    ("28. Juli 2015", ["nl", "de"]),
    ("5 April 2009", ["en", "nl", "de"]),
    ("11 Август 2009", ["ru", "bg"]),
    ("31 de maio de 2025", ["pt"]),
])
def test_language_claims_list_every_language(parser, text, claims):
    assert parser._language_claims(text) == claims


@pytest.mark.parametrize("text,key", [
    # A shared month name still tries the first language first, so dates that
    # parsed before keep their pattern (and DateMatch.language).
    ("5 April 2009", "dt:date:date_eng1"),
    ("16 mai 2025", "dt:date:fr_base_lc"),
    ("28. Juli 2015", "dt:date:nl_base"),
])
def test_shared_month_name_keeps_first_language_pattern(parser, text, key):
    assert parser.match(text)["pattern"]["key"] == key


def test_shared_detection_month_names_mean_the_same_month():
    """The fallback lets any claiming language parse a shared month name; that is
    only safe while each shared name is the same month in every language."""
    names = {code: _lang_month_names(code) for code in MONTHS_BY_LANGUAGE}
    for a, b in itertools.combinations(sorted(names), 2):
        for name in names[a] & names[b]:
            assert (MONTHS_BY_LANGUAGE[a].month_to_int[name]
                    == MONTHS_BY_LANGUAGE[b].month_to_int[name]), (name, a, b)


# ---------------------------------------------------------------------------
# Russian patterns
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected,key", [
    ("9 Мая 1998", datetime.datetime(1998, 5, 9), "dt:date:date_rus"),
    ("9 мая 1998", datetime.datetime(1998, 5, 9), "dt:date:date_rus_lc1"),
    ("Пятница, 5 Мая 2020 года", datetime.datetime(2020, 5, 5), "dt:date:weekday_rus"),
    ("Понедельник, 25 Сентября 1979 года", datetime.datetime(1979, 9, 25),
     "dt:date:weekday_rus"),
    ("Суббота 1 Мая 2021 г.", datetime.datetime(2021, 5, 1), "dt:date:weekday_rus"),
    ("Понедельник, 25 сентября 1979 года", datetime.datetime(1979, 9, 25),
     "dt:date:weekday_rus_lc1"),
    ("Воскресенье, 5 мая 2020 года", datetime.datetime(2020, 5, 5),
     "dt:date:weekday_rus_lc1"),
    # The old misspelling still matches.
    ("Воскресение, 5 мая 2020 года", datetime.datetime(2020, 5, 5),
     "dt:date:weekday_rus_lc1"),
])
def test_russian_dates(parser, text, expected, key):
    res = parser.match(text)
    assert res is not None
    assert res["pattern"]["key"] == key
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text,expected,key", [
    ("1.мая.1945", datetime.datetime(1945, 5, 1), "dt:date:rus_rare_3"),
    ("Май 6, 2020", datetime.datetime(2020, 5, 6), "dt:date:rus_rare_5"),
    ("7 Юли 1918", datetime.datetime(1918, 7, 7), "dt:date:bg_base"),
    ("8 юни 1923", datetime.datetime(1923, 6, 8), "dt:date:bg_base_lc"),
    ("9 Maj 1997", datetime.datetime(1997, 5, 9), "dt:date:pl_base"),
    ("9 maj 1997", datetime.datetime(1997, 5, 9), "dt:date:pl_base_lc"),
    ("17/апреля/1908", datetime.datetime(1908, 4, 17), "dt:date:date_rus_lc1"),
])
def test_short_or_slashed_dates(parser, text, expected, key):
    res = parser.match(text)
    assert res is not None
    assert res["pattern"]["basekey"] == key
    assert parser.parse(text) == expected


# ---------------------------------------------------------------------------
# Russian dates without a year, and the "в" before a time
# ---------------------------------------------------------------------------

_THIS_YEAR = datetime.date.today().year


@pytest.mark.parametrize("text,month_day_time,key", [
    ("4 Сентября в 04:06:33", (9, 4, 4, 6, 33), "dt:date:date_rus_noyear:time_2"),
    ("4 сентября в 04:06:33", (9, 4, 4, 6, 33), "dt:date:date_rus_noyear:time_2"),
    ("13 Марта в 05:31", (3, 13, 5, 31, 0), "dt:date:date_rus_noyear:time_1"),
    ("4 Сентября 04:06", (9, 4, 4, 6, 0), "dt:date:date_rus_noyear:time_1"),
    ("4 Сентября", (9, 4, 0, 0, 0), "dt:date:date_rus_noyear"),
    ("5 мая", (5, 5, 0, 0, 0), "dt:date:date_rus_noyear"),
])
def test_russian_date_without_year(parser, text, month_day_time, key):
    """A yearless Russian date takes the current year, like ``05.12``."""
    res = parser.match(text)
    assert res is not None
    assert res["pattern"]["key"] == key
    assert parser.parse(text) == datetime.datetime(_THIS_YEAR, *month_day_time)


@pytest.mark.parametrize("text", [
    "4 Сентября в 04:06:33", "4 сентября в 04:06:33", "4 Сентября", "5 мая",
])
def test_russian_date_without_year_needs_allow_no_year(parser, legacy_parser, text):
    assert parser.match(text, allow_no_year=False) is None
    assert parser.parse(text, allow_no_year=False) is None
    assert legacy_parser.parse(text, allow_no_year=False) is None


@pytest.mark.parametrize("text,expected,key", [
    ("4 Сентября 2020 в 04:06:33", datetime.datetime(2020, 9, 4, 4, 6, 33),
     "dt:date:date_rus:time_2"),
    ("4 Сентября 2020 04:06:33", datetime.datetime(2020, 9, 4, 4, 6, 33),
     "dt:date:date_rus:time_2"),
    ("4 Сентября 2020 в 04:06", datetime.datetime(2020, 9, 4, 4, 6),
     "dt:date:date_rus:time_1"),
    ("2 Января 1981 года в 21:04", datetime.datetime(1981, 1, 2, 21, 4),
     "dt:date:date_rus2:time_1"),
    ("4 сентября 2020 г. в 04:06:33", datetime.datetime(2020, 9, 4, 4, 6, 33),
     "dt:date:date_rus_lc2:time_2"),
    ("4 Сентября 2020", datetime.datetime(2020, 9, 4), "dt:date:date_rus"),
])
def test_russian_date_keeps_time(parser, legacy_parser, text, expected, key):
    """The time after a Russian date, with or without ``в``, is parsed."""
    res = parser.match(text)
    assert res is not None
    assert res["pattern"]["key"] == key
    assert parser.parse(text) == expected
    assert legacy_parser.parse(text) == expected


def test_time_word_is_russian_only(parser):
    """``в`` before a time is accepted only after a Russian date."""
    assert parser.parse("16 May 2009 в 14:10") == datetime.datetime(2009, 5, 16)
    assert parser.parse("16 May 2009 14:10") == datetime.datetime(2009, 5, 16, 14, 10)


# ---------------------------------------------------------------------------
# pivot_year type check
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", [True, False, "1968", 1968.0])
def test_pivot_year_rejects_bool_and_non_integers(value):
    """``True`` is an ``int`` equal to 1: it mapped only ``00`` to 2000 and
    ``05`` to 1905. It and other non-integers now raise."""
    with pytest.raises(TypeError, match="4-digit year such as 1968"):
        DateParser(pivot_year=value, generate=False)


def test_pivot_year_accepts_integers():
    assert DateParser(pivot_year=1968).parse("05/16/20") == datetime.datetime(2020, 5, 16)
    assert DateParser(pivot_year=None).parse("05/16/99") == datetime.datetime(99, 5, 16)


# ---------------------------------------------------------------------------
# Longest match wins; widened length limits
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("2 Января 1981 21:04:08", datetime.datetime(1981, 1, 2, 21, 4, 8)),
    ("2 Января 1981 в 21:04", datetime.datetime(1981, 1, 2, 21, 4)),
    ("9 Июня 1927 15:18:03", datetime.datetime(1927, 6, 9, 15, 18, 3)),
    ("29 Мая 2005 07:36:05", datetime.datetime(2005, 5, 29, 7, 36, 5)),
    ("22 August 2005 08:47:19", datetime.datetime(2005, 8, 22, 8, 47, 19)),
    ("14 August 1995 23:54", datetime.datetime(1995, 8, 14, 23, 54)),
    ("April 25, 1953 08:02", datetime.datetime(1953, 4, 25, 8, 2)),
    ("May 2, 1915 09:25:57", datetime.datetime(1915, 5, 2, 9, 25, 57)),
    ("14 Avril 1995 20:16:12", datetime.datetime(1995, 4, 14, 20, 16, 12)),
    ("26 Dezember 1964 14:37", datetime.datetime(1964, 12, 26, 14, 37)),
    ("29 de Agosto de 1925 07:30", datetime.datetime(1925, 8, 29, 7, 30)),
    ("12.05.2020 10:30 Moscow", datetime.datetime(2020, 5, 12, 10, 30)),
])
def test_time_after_date_is_kept(parser, legacy_parser, text, expected):
    """The candidate consuming the most input wins over the length bonus."""
    assert parser.parse(text) == expected
    assert legacy_parser.parse(text) == expected


@pytest.mark.parametrize("text,expected,key", [
    # Rejected by the old length bounds; no other pattern matched.
    ("Mon 1/1/2020", datetime.datetime(2020, 1, 1), "dt:date:weekday_short_eng_iso"),
    ("Sábado 1 Maio 2020", datetime.datetime(2020, 5, 1), "dt:date:pt_weekday"),
    ("sábado 1 maio 2020", datetime.datetime(2020, 5, 1), "dt:date:pt_weekday_lc"),
    # Parsed before through another pattern; now their own pattern takes them.
    ("1.5.2005 г.", datetime.datetime(2005, 5, 1), "dt:date:date_rus3"),
    ("9 Mei 1998", datetime.datetime(1998, 5, 9), "dt:date:nl_base"),
    ("1 Mai 1998", datetime.datetime(1998, 5, 1), "dt:date:fr_base"),
])
def test_widened_length_bounds(parser, text, expected, key):
    res = parser.match(text)
    assert res is not None
    assert res["pattern"]["key"] == key
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text,key", [
    ("25 Jan 1936", "dt:date:date_eng1_short"),
    ("Wednesday, 30 September 2020", "dt:date:weekday_eng"),
    ("Sáb, 15 Setembro 2020", "dt:date:pt_weekday_short"),
])
def test_plain_variant_preferred_over_t_right(parser, text, key):
    """A ``:t_right`` variant matching the same text as the plain one does not
    win on the length bonus: its bounds include the trailing text."""
    assert parser.match(text)["pattern"]["key"] == key


@pytest.mark.parametrize("text", [
    "2 Января 1981 21:04:08",
    "14 Avril 1995 20:16:12",
    "01/02/2020",
    "1.5.2005 г.",
    "12.05.2020 10:30 Moscow",
])
def test_match_all_ranks_like_match(parser, text):
    results = parser.match_all(text)
    assert results[0]["pattern"]["key"] == parser.match(text)["pattern"]["key"]
