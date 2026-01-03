import datetime

import pytest

from qddate import DateParser
from qddate.qdparser import (
    scan_char_sets,
    CHAR_SET_DIGITS,
    CHAR_SET_LATIN,
    CHAR_SET_CYRILLIC,
    CHAR_SET_ACCENTED,
    CHAR_SET_SEPARATORS,
)


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
        ("пятница, июля 17, 2015", datetime.datetime(2015, 7, 17)),
        ("Июль 16, 2015", datetime.datetime(2015, 7, 16)),
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
        # New supported formats
        ("7 August, 2015", datetime.datetime(2015, 8, 7)),
        ("August 10th, 2015", datetime.datetime(2015, 8, 10)),
        ("Wednesday 22 Apr 2015", datetime.datetime(2015, 4, 22)),
        # Czech formats
        ("15 Leden 2015", datetime.datetime(2015, 1, 15)),
        ("5 ledna 2020", datetime.datetime(2020, 1, 5)),
        ("23 Prosince 2023", datetime.datetime(2023, 12, 23)),
        ("12 července 2022", datetime.datetime(2022, 7, 12)),
        # German formats (expanded)
        ("28. Juli 2015", datetime.datetime(2015, 7, 28)),
        ("15. juli 2015", datetime.datetime(2015, 7, 15)),
        # English abbreviations
        ("24 Jul 2015", datetime.datetime(2015, 7, 24)),
        ("Jan 15, 2020", datetime.datetime(2020, 1, 15)),
        ("Fri 24 Jul 2015", datetime.datetime(2015, 7, 24)),
        # Dutch formats
        ("15 Januari 2024", datetime.datetime(2024, 1, 15)),
        ("3 maart 2023", datetime.datetime(2023, 3, 3)),
        ("Maandag, 28 Juli 2015", datetime.datetime(2015, 7, 28)),
        # Bulgarian formats
        ("15 Мapт 2024", datetime.datetime(2024, 3, 15)),
        ("3 дeкeмвpи 2023", datetime.datetime(2023, 12, 3)),
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
        "08 Jul, 2015",
        # These formats are not supported (German abbreviated months with periods)
        "15. Jul 2023",
        "5. jan 2020",
        "12. Dez 2022",
        # These formats are not supported (English abbreviated with comma/ordinal)
        "8 Sep, 2023",
        "Mon, 5 Jan 2020",
        "8th Jul 2015",
        # These formats are not supported (German weekday with abbreviated months)
        "Montag, 28. Juli 2015",
        "Freitag, 3. August 2018",
        "montag, 15. juli 2015",
        "Вторник, 18 Август 2015 18:51",
        "19 август в 16:03",
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


def test_language_filtering_single_language():
    """Test that language filtering works with a single language"""
    # Russian-only parser should parse Russian dates
    parser_ru = DateParser(languages="ru")
    assert parser_ru.parse("3 Января 2003 года") == datetime.datetime(2003, 1, 3)
    assert parser_ru.parse("15 февраля 2007 года") == datetime.datetime(2007, 2, 15)
    
    # Russian-only parser should NOT parse English dates
    assert parser_ru.parse("6 Jan 2009") is None
    assert parser_ru.parse("January 3, 2003") is None


def test_language_filtering_multiple_languages():
    """Test that language filtering works with multiple languages"""
    # English and German parser should parse both
    parser_en_de = DateParser(languages=["en", "de"])
    
    # English dates should work
    assert parser_en_de.parse("6 Jan 2009") == datetime.datetime(2009, 1, 6)
    assert parser_en_de.parse("January 3, 2003") == datetime.datetime(2003, 1, 3)
    
    # German dates should work
    assert parser_en_de.parse("28. Juli 2015") == datetime.datetime(2015, 7, 28)
    
    # Russian dates should NOT work
    assert parser_en_de.parse("3 Января 2003 года") is None


def test_language_filtering_english_only():
    """Test that English-only parser works correctly"""
    parser_en = DateParser(languages="en")
    
    # English dates should work
    assert parser_en.parse("6 Jan 2009") == datetime.datetime(2009, 1, 6)
    assert parser_en.parse("01.12.2009") == datetime.datetime(2009, 12, 1)  # Numeric format
    assert parser_en.parse("2013-01-12") == datetime.datetime(2013, 1, 12)  # ISO format
    
    # Russian dates should NOT work
    assert parser_en.parse("3 Января 2003 года") is None


def test_language_filtering_backward_compatibility():
    """Test that default behavior (no languages parameter) uses all languages"""
    parser_all = DateParser()
    
    # Should parse dates from multiple languages
    assert parser_all.parse("6 Jan 2009") == datetime.datetime(2009, 1, 6)  # English
    assert parser_all.parse("3 Января 2003 года") == datetime.datetime(2003, 1, 3)  # Russian
    assert parser_all.parse("28. Juli 2015") == datetime.datetime(2015, 7, 28)  # German


def test_language_filtering_invalid_language():
    """Test that invalid language codes raise ValueError"""
    with pytest.raises(ValueError, match="Unsupported language"):
        DateParser(languages="invalid")
    
    with pytest.raises(ValueError, match="Unsupported language"):
        DateParser(languages=["en", "invalid"])


def test_language_filtering_empty_list():
    """Test that empty languages list uses all patterns (backward compatible)"""
    parser = DateParser(languages=[])
    
    # Should parse dates from multiple languages (all patterns)
    assert parser.parse("6 Jan 2009") == datetime.datetime(2009, 1, 6)  # English
    assert parser.parse("3 Января 2003 года") == datetime.datetime(2003, 1, 3)  # Russian


def test_language_filtering_with_numeric_formats():
    """Test that numeric date formats work with language filtering"""
    # Numeric formats (like 01.12.2009) are in English patterns
    parser_en = DateParser(languages="en")
    assert parser_en.parse("01.12.2009") == datetime.datetime(2009, 12, 1)
    assert parser_en.parse("2013-01-12") == datetime.datetime(2013, 1, 12)
    
    # Should also work with Russian parser (if numeric patterns are included)
    parser_ru = DateParser(languages="ru")
    # Russian parser might not have numeric patterns, so this might be None
    # This tests the actual behavior
    result = parser_ru.parse("01.12.2009")
    # Result could be None or a datetime depending on implementation
    # We just verify it doesn't crash
    assert result is None or isinstance(result, datetime.datetime)


# Character set scanning tests
def test_scan_char_sets_digits_only():
    """Test character set scanning with digits only"""
    result = scan_char_sets("123456")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_LATIN not in result
    assert CHAR_SET_CYRILLIC not in result
    assert CHAR_SET_ACCENTED not in result


def test_scan_char_sets_latin_only():
    """Test character set scanning with Latin letters only"""
    result = scan_char_sets("January")
    assert CHAR_SET_LATIN in result
    assert CHAR_SET_DIGITS not in result
    assert CHAR_SET_CYRILLIC not in result
    assert CHAR_SET_ACCENTED not in result


def test_scan_char_sets_cyrillic():
    """Test character set scanning with Cyrillic characters"""
    result = scan_char_sets("Января")
    assert CHAR_SET_CYRILLIC in result
    assert CHAR_SET_DIGITS not in result
    assert CHAR_SET_LATIN not in result
    assert CHAR_SET_ACCENTED not in result


def test_scan_char_sets_accented():
    """Test character set scanning with accented characters"""
    result = scan_char_sets("juillet")
    # Check for French accented characters
    result2 = scan_char_sets("července")
    assert CHAR_SET_ACCENTED in result2 or CHAR_SET_LATIN in result2
    # Czech accented characters should be detected
    result3 = scan_char_sets("červen")
    assert CHAR_SET_ACCENTED in result3


def test_scan_char_sets_mixed():
    """Test character set scanning with mixed character sets"""
    result = scan_char_sets("15 Января 2003")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_CYRILLIC in result
    assert CHAR_SET_SEPARATORS in result


def test_scan_char_sets_separators():
    """Test character set scanning with separators"""
    result = scan_char_sets("01.12.2009")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_SEPARATORS in result
    assert "." in "01.12.2009"  # Verify separator is present


def test_scan_char_sets_empty_string():
    """Test character set scanning with empty string"""
    result = scan_char_sets("")
    assert result == set()


def test_scan_char_sets_numeric_date():
    """Test character set scanning with numeric date format"""
    result = scan_char_sets("01/12/2009")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_SEPARATORS in result


def test_scan_char_sets_english_date():
    """Test character set scanning with English date format"""
    result = scan_char_sets("6 Jan 2009")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_LATIN in result


def test_scan_char_sets_french_date():
    """Test character set scanning with French date format"""
    result = scan_char_sets("8 juillet 2015")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_LATIN in result
    # French may have accented characters depending on the word


def test_scan_char_sets_czech_date():
    """Test character set scanning with Czech date format"""
    result = scan_char_sets("15 Leden 2015")
    assert CHAR_SET_DIGITS in result
    assert CHAR_SET_LATIN in result
    # Czech with accented characters
    result2 = scan_char_sets("5 ledna 2020")
    assert CHAR_SET_DIGITS in result2
    # May have accented characters if present


# Pattern filtering tests
def test_pattern_filtering_cyrillic_input(parser):
    """Test that Cyrillic input filters out non-Cyrillic patterns"""
    # Russian date should match
    result = parser.parse("3 Января 2003 года")
    assert result == datetime.datetime(2003, 1, 3)
    
    # English date should still work (has Latin characters)
    result2 = parser.parse("6 Jan 2009")
    assert result2 == datetime.datetime(2009, 1, 6)


def test_pattern_filtering_numeric_only(parser):
    """Test that numeric-only input works correctly"""
    # Numeric dates should work
    result = parser.parse("01.12.2009")
    assert result == datetime.datetime(2009, 12, 1)


def test_pattern_filtering_preserves_matches(parser):
    """Test that character set filtering doesn't break existing matches"""
    # Test various date formats that should all still work
    test_cases = [
        ("01.12.2009", datetime.datetime(2009, 12, 1)),
        ("6 Jan 2009", datetime.datetime(2009, 1, 6)),
        ("3 Января 2003 года", datetime.datetime(2003, 1, 3)),
        ("8 juillet 2015", datetime.datetime(2015, 7, 8)),
        ("15 Leden 2015", datetime.datetime(2015, 1, 15)),
    ]
    
    for text, expected in test_cases:
        result = parser.parse(text)
        assert result == expected, f"Failed for: {text}"


def test_pattern_filtering_with_noprefix(parser):
    """Test that character set filtering works with noprefix=True"""
    # With noprefix, character set filtering should still work
    result = parser.parse("3 Января 2003 года", noprefix=True)
    assert result == datetime.datetime(2003, 1, 3)


def test_pattern_filtering_short_strings(parser):
    """Test that short strings don't trigger character set filtering"""
    # Very short strings (< 6 chars) should not use character set filtering
    # but should still work
    result = parser.parse("01.12")
    # This might return None if no pattern matches, but shouldn't crash
    assert result is None or isinstance(result, datetime.datetime)

