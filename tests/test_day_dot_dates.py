"""A dot after the day: Czech, Polish, Slovak (Q11 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

``5. května 2022`` is the standard Czech spelling and ``5. mája 2022`` the
Slovak one; both returned ``None`` (``5 května 2022`` without the dot already
parsed, Slovak was not supported). Polish rarely writes the dot, but
``5. maja 2022`` is accepted too. German already read ``5. Mai 2022``.
"""
import datetime

import pytest

from qddate import DateParser
from qddate.patterns import SUPPORTED_LANGUAGES


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.mark.parametrize("text, expected, language", [
    # Czech
    ("5. května 2022", datetime.datetime(2022, 5, 5), "cz"),
    ("1. ledna 2020", datetime.datetime(2020, 1, 1), "cz"),
    ("1.ledna 2020", datetime.datetime(2020, 1, 1), "cz"),
    ("15. Leden 2015", datetime.datetime(2015, 1, 15), "cz"),
    ("5 května 2022", datetime.datetime(2022, 5, 5), "cz"),
    # Polish
    ("5. maja 2022", datetime.datetime(2022, 5, 5), "pl"),
    ("5. Stycznia 2020", datetime.datetime(2020, 1, 5), "pl"),
    ("17. marca 2018 r.", datetime.datetime(2018, 3, 17), "pl"),
    # Slovak
    ("5. mája 2022", datetime.datetime(2022, 5, 5), "sk"),
    ("1. januára 2020", datetime.datetime(2020, 1, 1), "sk"),
    ("12. septembra 2022", datetime.datetime(2022, 9, 12), "sk"),
    ("30. decembra 2021", datetime.datetime(2021, 12, 30), "sk"),
    ("5. Mája 2022", datetime.datetime(2022, 5, 5), "sk"),
    ("5 júna 2022", datetime.datetime(2022, 6, 5), "sk"),
    ("5. máj 2022", datetime.datetime(2022, 5, 5), "sk"),
    # German, unchanged
    ("5. Mai 2022", datetime.datetime(2022, 5, 5), "de"),
])
def test_day_with_a_dot(parser, text, expected, language):
    match = parser.match_typed(text)
    assert match.datetime == expected
    assert match.language == language


def test_time_after_the_date(parser):
    assert parser.parse("5. května 2022 14:30") == datetime.datetime(2022, 5, 5, 14, 30)
    assert parser.parse("5. októbra 2022 14:30") == datetime.datetime(2022, 10, 5, 14, 30)


def test_slovak_is_a_supported_language():
    assert "sk" in SUPPORTED_LANGUAGES
    parser = DateParser(languages="sk")
    assert parser.parse("5. mája 2022") == datetime.datetime(2022, 5, 5)
    # Czech is not in the allow-list.
    assert parser.parse("5. května 2022") is None


def test_shared_month_names_keep_their_language(parser):
    """Slovak "september", "augusta" or "marca" do not relabel other languages:
    names shared with English or Polish do not claim Slovak."""
    assert parser.match_typed("5 September 2022").language == "en"
    assert parser.match_typed("5 marca 2022").language == "pl"
    assert parser.parse("5. augusta 2022", languages="sk") == datetime.datetime(2022, 8, 5)
