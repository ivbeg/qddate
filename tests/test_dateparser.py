import datetime

import pytest

from qddate import DateParser


@pytest.fixture(scope="module")
def parser():
    return DateParser()


@pytest.fixture
def fresh_parser():
    """Fixture that creates a new parser instance for each test"""
    return DateParser()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Basic formats
        ("01.12.2009", datetime.datetime(2009, 12, 1)),
        ("2013-01-12", datetime.datetime(2013, 1, 12)),
        ("31.05.2001", datetime.datetime(2001, 5, 31)),
        ("7/12/2009", datetime.datetime(2009, 12, 7)),
        ("11/29/1991", datetime.datetime(1991, 11, 29)),
        ("05/16/99", datetime.datetime(99, 5, 16)),
        # English formats
        ("6 Jan 2009", datetime.datetime(2009, 1, 6)),
        ("Jan 8, 1098", datetime.datetime(1098, 1, 8)),
        ("JAN 1, 2001", datetime.datetime(2001, 1, 1)),
        ("5 August 2001", datetime.datetime(2001, 8, 5)),
        ("3 jun 2009", datetime.datetime(2009, 6, 3)),
        ("Thursday 4 April 2019", datetime.datetime(2019, 4, 4)),
        ("July 01, 2015", datetime.datetime(2015, 7, 1)),
        ("Fri, 3 July 2015", datetime.datetime(2015, 7, 3)),
        ("Fri 24 Jul 2015", datetime.datetime(2015, 7, 24)),
        ("August 10th, 2015", datetime.datetime(2015, 8, 10)),
        # Russian formats
        ("3 Января 2003 года", datetime.datetime(2003, 1, 3)),
        ("05 Января 2003", datetime.datetime(2003, 1, 5)),
        ("15 февраля 2007 года", datetime.datetime(2007, 2, 15)),
        ("2 Июня 2015", datetime.datetime(2015, 6, 2)),
        ("9 июля 2015 г.", datetime.datetime(2015, 7, 9)),
        ("23 июня 2015", datetime.datetime(2015, 6, 23)),
        ("3 Июля, 2015", datetime.datetime(2015, 7, 3)),
        ("21 Фeвpyapи 2015", datetime.datetime(2015, 2, 21)),
        ("1 нoeмвpи 2013", datetime.datetime(2013, 11, 1)),
        # French formats
        ("Le 8 juillet 2015", datetime.datetime(2015, 7, 8)),
        ("8 juillet 2015", datetime.datetime(2015, 7, 8)),
        # Portuguese formats
        ("26 de julho de 2015", datetime.datetime(2015, 7, 26)),
        # Spanish formats
        ("17 de Junio de 2015", datetime.datetime(2015, 6, 17)),
        ("junio 9, 2015", datetime.datetime(2015, 6, 9)),
        # Turkish formats
        ("17 Ocak 2015", datetime.datetime(2015, 1, 17)),
        ("9 eylül 2022 tarihinde", datetime.datetime(2022, 9, 9)),
        # German formats
        ("28. Juli 2015", datetime.datetime(2015, 7, 28)),
        # Polish formats
        ("5 stycznia 2020", datetime.datetime(2020, 1, 5)),
        ("17 Marca 2018 r.", datetime.datetime(2018, 3, 17)),
        # Dates with text after
        ("12.03.1999 Hello people", datetime.datetime(1999, 3, 12)),
        # Dates with time
        ("16 May 2009 14:10", datetime.datetime(2009, 5, 16, 14, 10)),
        ("01.03.2009 14:53", datetime.datetime(2009, 3, 1, 14, 53)),
        ("01.03.2009 14:53:12", datetime.datetime(2009, 3, 1, 14, 53, 12)),
        ("22.12.2009 17:56", datetime.datetime(2009, 12, 22, 17, 56)),
        ("23 Jul 2015, 09:00 BST", datetime.datetime(2015, 7, 23, 9, 0)),
        ("9 Июля 2015 [11:23]", datetime.datetime(2015, 7, 9, 11, 23)),
        ("12-08-2015 - 09:00", datetime.datetime(2015, 8, 12)),
    ],
)
def test_parse_supported_text(parser, text, expected):
    """Test that parse correctly handles various supported date formats"""
    assert parser.parse(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "totally invalid date",
        "",
        "   ",
        "26 / 06 15",
        "14th April 2015:",
        "пятница, июля 17, 2015",
        "Июль 16, 2015",
        "Wednesday 22 Apr 2015",
        "08 Jul, 2015",
        "Вторник, 18 Август 2015 18:51",
        "19 август в 16:03",
        "7 August, 2015",
        "Авг 11, 2015",
        "Июль 16th, 2012 | 11:08 пп",
    ],
)
def test_parse_returns_none_for_unsupported_text(parser, text):
    """Test that parse returns None for unsupported or invalid date strings"""
    assert parser.parse(text) is None


def test_parse_with_noprefix(parser):
    """Test that noprefix parameter works correctly"""
    text = "01.12.2009"
    result_with_prefix = parser.parse(text)
    result_without_prefix = parser.parse(text, noprefix=True)
    assert result_with_prefix == result_without_prefix
    assert result_with_prefix == datetime.datetime(2009, 12, 1)


def test_match_method(parser):
    """Test that match method returns correct structure"""
    text = "01.12.2009"
    result = parser.match(text)
    
    assert result is not None
    assert "values" in result
    assert "pattern" in result
    assert "key" in result["pattern"]
    
    # Verify the values can be used to construct datetime
    d = {"month": 0, "day": 0, "year": 0}
    for k, v in list(result["values"].items()):
        d[k] = int(v)
    dt = datetime.datetime(**d)
    assert dt == datetime.datetime(2009, 12, 1)


def test_match_returns_none_for_invalid(parser):
    """Test that match returns None for invalid dates"""
    result = parser.match("totally invalid date")
    assert result is None


def test_match_with_noprefix(parser):
    """Test match method with noprefix parameter"""
    text = "01.12.2009"
    result_with_prefix = parser.match(text)
    result_without_prefix = parser.match(text, noprefix=True)
    
    # Both should succeed, but may match different patterns
    assert result_with_prefix is not None
    assert result_without_prefix is not None


def test_match_with_noyear(parser):
    """Test match method with noyear parameter"""
    # This tests the noyear flag functionality
    text = "01.12.2009"
    result = parser.match(text, noyear=True)
    assert result is not None


def test_start_session_end_session(fresh_parser):
    """Test session caching functionality"""
    text = "01.12.2009"
    
    # First, get a successful match to find pattern keys
    result = fresh_parser.match(text)
    assert result is not None
    pattern_key = result["pattern"]["key"]
    
    # Start session with cached patterns
    fresh_parser.startSession([pattern_key])
    assert fresh_parser.cachedpats is not None
    assert len(fresh_parser.cachedpats) > 0
    
    # Should still work with cached patterns
    result2 = fresh_parser.parse(text)
    assert result2 == datetime.datetime(2009, 12, 1)
    
    # End session
    fresh_parser.endSession()
    assert fresh_parser.cachedpats is None
    
    # Should still work after ending session
    result3 = fresh_parser.parse(text)
    assert result3 == datetime.datetime(2009, 12, 1)


def test_parser_initialization_with_generate_false():
    """Test parser initialization with generate=False"""
    parser = DateParser(generate=False)
    # With generate=False, patterns should not be expanded
    # This is a basic smoke test
    assert parser.patterns is not None


def test_parser_initialization_with_base_only():
    """Test parser initialization with base_only=True"""
    parser = DateParser(base_only=True)
    # With base_only=True, should have fewer patterns
    # This is a basic smoke test
    assert parser.patterns is not None
    result = parser.parse("01.12.2009")
    assert result == datetime.datetime(2009, 12, 1)


def test_parser_handles_short_strings(parser):
    """Test that parser handles very short strings gracefully"""
    # Very short strings should return None without crashing
    assert parser.parse("") is None
    assert parser.parse("1") is None
    assert parser.parse("12") is None
    assert parser.parse("123") is None


def test_parser_handles_unicode(parser):
    """Test that parser correctly handles unicode strings"""
    # Test various unicode date formats
    unicode_tests = [
        ("3 Января 2003 года", datetime.datetime(2003, 1, 3)),
        ("9 июля 2015 г.", datetime.datetime(2015, 7, 9)),
        ("Le 8 juillet 2015", datetime.datetime(2015, 7, 8)),
    ]
    
    for text, expected in unicode_tests:
        result = parser.parse(text)
        assert result == expected


def test_parser_consistency(parser):
    """Test that parser returns consistent results for same input"""
    text = "01.12.2009"
    result1 = parser.parse(text)
    result2 = parser.parse(text)
    result3 = parser.parse(text)
    
    assert result1 == result2 == result3
    assert result1 == datetime.datetime(2009, 12, 1)

