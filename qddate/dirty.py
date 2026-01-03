#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Here is all dirty matched code
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

# Pre-computed basekey lists as constants for performance optimization
_ALPHA_ENGLISH_BASEKEYS = [
    "dt:date:eng1",
    "dt:date:eng3",
    "dt:date:date_eng2",
    "dt:date:date_eng2_lc",
    "dt:date:date_eng2_short",
    "dt:date:date_eng3",
    "dt:date:date_eng3_nolc",
    "dt:date:weekday_eng",
    "dt:date:weekday_eng_lc",
    "dt:date:weekday_eng_wshort",
    "dt:date:weekday_eng_iso",
    "dt:date:weekday_short_eng_iso",
    "dt:date:fr_base_article",
    "dt:date:fr_base_lc_article",
    "dt:date:weekday_eng_mshort_wshort",
    "dt:date:weekday_eng_mixed",
]

_PT_BASEKEYS = [
    "dt:date:pt_base",
    "dt:date:pt_base_lc",
    "dt:date:pt_base_article",
    "dt:date:pt_base_lc_article",
    "dt:date:pt_short",
    "dt:date:pt_short_lc",
    "dt:date:pt_short_monthfirst",
    "dt:date:pt_short_lc_monthfirst",
    "dt:date:pt_weekday_short",
    "dt:date:pt_weekday_short_lc",
]

_ES_BASEKEYS = [
    "dt:date:es_base",
    "dt:date:es_base_lc",
    "dt:date:es_base_article",
    "dt:date:es_base_lc_article",
    "dt:date:es_rare_1",
    "dt:date:es_rare_2",
    "dt:date:es_short",
    "dt:date:es_short_lc",
    "dt:date:es_short_monthfirst",
    "dt:date:es_short_lc_monthfirst",
    "dt:date:es_weekday",
    "dt:date:es_weekday_lc",
]

_IT_BASEKEYS = [
    "dt:date:it_base",
    "dt:date:it_base_lc",
    "dt:date:it_base_article",
    "dt:date:it_base_lc_article",
    "dt:date:it_rare_1",
    "dt:date:it_rare_2",
]

_NL_BASEKEYS = [
    "dt:date:nl_base",
    "dt:date:nl_base_lc",
    "dt:date:nl_short",
    "dt:date:nl_short_lc",
]

_NL_ALPHA_BASEKEYS = [
    "dt:date:nl_weekday",
    "dt:date:nl_weekday_lc",
    "dt:date:nl_rare_1",
    "dt:date:nl_rare_2",
]

_ALPHA_NON_ENGLISH_BASEKEYS = [
    "dt:date:weekday_rus",
    "dt:date:weekday_rus_lc1",
    "dt:date:rare_5",
    "dt:date:rare_6",
    "dt:date:rus_rare_5",
    "dt:date:rus_rare_6",
]

_DOT_SEPARATOR_BASEKEYS = [
    "dt:date:date_2",
    "dt:date:date_4",
    "dt:date:date_rus3",
    "dt:date:date_4_point",
    "dt:date:date_eng1",
    "dt:date:noyear_1",
    "dt:date:rare_2",
    "dt:date:rare_3",
    "dt:date:rus_rare_2",
    "dt:date:rus_rare_3",
]

_DE_BASEKEYS = ["dt:date:de_base", "dt:date:de_base_lc", "dt:date:de_rare_1", "dt:date:de_rare_2", "dt:date:de_weekday", "dt:date:de_weekday_lc"]

_FR_BASEKEYS = [
    "dt:date:fr_base",
    "dt:date:fr_base_lc",
    "dt:date:fr_base_article",
    "dt:date:fr_base_lc_article",
    "dt:date:fr_short",
    "dt:date:fr_short_lc",
    "dt:date:fr_short_monthfirst",
    "dt:date:fr_short_lc_monthfirst",
    "dt:date:fr_weekday",
    "dt:date:fr_weekday_lc",
]

_SLASH_SEPARATOR_BASEKEYS = [
    "dt:date:date_1",
    "dt:date:date_9",
    "dt:date:date_8",
    "dt:date:date_usa",
    "dt:date:date_usa_1",
    "dt:date:rare_1",
]

_DASH_SEPARATOR_BASEKEYS = ["dt:date:date_iso8601", "dt:date:date_iso8601_short"]

_DEFAULT_DIGIT_BASEKEYS = [
    "dt:date:date_3",
    "dt:date:date_5",
    "dt:date:date_6",
    "dt:date:date_7",
    "dt:date:date_rus",
    "dt:date:date_rus2",
    "dt:date:date_rus_lc1",
    "dt:date:date_rus_lc2",
    "dt:date:date_eng1",
    "dt:date:date_eng1_short",
    "dt:date:date_eng1_lc",
    "dt:date:date_eng1xx",
    "dt:date:date_eng1x",
]

_EXTENDED_DIGIT_BASEKEYS = [
    "dt:date:date_1",
    "dt:date:date_9",
    "dt:date:date_8",
    "dt:date:date_usa",
    "dt:date:date_usa_1",
    "dt:date:rare_1",
    "dt:date:rare_2",
    "dt:date:rare_3",
    "dt:date:rare_4",
    "dt:date:date_5",
]

_BG_BASEKEYS = ["dt:date:bg_base", "dt:date:bg_base_lc"]

_TR_BASEKEYS = ["dt:date:tr_base", "dt:date:tr_base_lc"]

_PL_BASEKEYS = [
    "dt:date:pl_base",
    "dt:date:pl_base_lc",
    "dt:date:pl_gen",
    "dt:date:pl_gen_lc",
]

_CZ_BASEKEYS = [
    "dt:date:cz_base",
    "dt:date:cz_base_lc",
    "dt:date:cz_gen",
    "dt:date:cz_gen_lc",
]

# Combined lists for O(1) access without runtime concatenation
# Using tuples for immutability and slight performance benefit
_ALPHA_ENGLISH_FULL = tuple(
    _ALPHA_ENGLISH_BASEKEYS
    + _PT_BASEKEYS
    + _ES_BASEKEYS
    + _IT_BASEKEYS
    + _NL_ALPHA_BASEKEYS
    + _FR_BASEKEYS
)
_DOT_SEPARATOR_FULL = tuple(_DOT_SEPARATOR_BASEKEYS + _DE_BASEKEYS)
_DEFAULT_DIGIT_FULL = tuple(
    _DEFAULT_DIGIT_BASEKEYS
    + _EXTENDED_DIGIT_BASEKEYS
    + _PT_BASEKEYS
    + _DE_BASEKEYS
    + _BG_BASEKEYS
    + _ES_BASEKEYS
    + _IT_BASEKEYS
    + _TR_BASEKEYS
    + _PL_BASEKEYS
    + _NL_BASEKEYS
    + _CZ_BASEKEYS
    + _FR_BASEKEYS
)
_RUS_SEPARATOR_BASEKEYS = ("dt:date:date_rus",)
_DASH_LONG_BASEKEYS = ("dt:date:date_iso8601", "dt:date:date_9")
_DOT_LONG_BASEKEYS = ("dt:date:date_10",)


# Combined pattern sets for accuracy-first matching
# These unions ensure we don't miss valid patterns due to overly restrictive filtering
_ALL_ALPHA_PATTERNS = tuple(set(_ALPHA_ENGLISH_FULL + tuple(_ALPHA_NON_ENGLISH_BASEKEYS)))
_ALL_SEPARATOR_PATTERNS = tuple(set(
    list(_DOT_SEPARATOR_FULL) + 
    list(_SLASH_SEPARATOR_BASEKEYS) + 
    list(_DASH_SEPARATOR_BASEKEYS) + 
    list(_RUS_SEPARATOR_BASEKEYS)
))


def matchPrefix(text):
    """
    Accuracy-first pattern prefix matcher.
    
    This function analyzes the prefix of the input text and returns a comprehensive
    set of pattern basekeys that could potentially match. The approach prioritizes
    accuracy over speed by being more inclusive - when in doubt, include more patterns
    rather than risk missing valid dates.
    
    Key improvements over speed-first version:
    - Checks for separators across more positions (not just 1, 2, 4)
    - Returns union of relevant pattern sets rather than exclusive sets
    - Handles edge cases better (leading spaces, unusual formats)
    - More conservative filtering - only excludes patterns when highly confident
    
    :param text: text with date to match (typically first 6 characters)
    :return: list of pattern basekeys to run against
    """
    text_len = len(text)
    if text_len == 0:
        return []

    # Strip leading whitespace for analysis (but preserve original for matching)
    text_stripped = text.lstrip()
    if not text_stripped:
        # All whitespace - return all patterns (comprehensive fallback)
        all_patterns = list(_DEFAULT_DIGIT_FULL) + list(_ALL_ALPHA_PATTERNS) + list(_ALL_SEPARATOR_PATTERNS)
        return list(set(all_patterns))
    
    first_char = text_stripped[0]
    result_patterns = []
    
    # Check if text starts with a letter (alpha-based patterns)
    if not first_char.isdigit():
        fc = first_char.lower()
        
        # Include all alpha patterns when we see a letter
        # This covers English and non-English patterns
        if fc.isalpha():
            result_patterns.extend(_ALL_ALPHA_PATTERNS)
            # Also include digit patterns that might match with leading text
            # (e.g., "Wed 12/31/2023")
            result_patterns.extend(_ALL_SEPARATOR_PATTERNS)
            return list(set(result_patterns))  # Remove duplicates
    
    # Text starts with a digit - analyze separator positions more comprehensively
    # Check for separators across multiple positions, not just specific ones
    separators_found = set()
    has_dot = False
    has_slash = False
    has_dash = False
    has_comma = False
    has_space = False
    
    # Scan first 10 characters for separators (more thorough than original)
    # This catches separators at various positions, not just 1, 2, 4
    scan_len = min(10, len(text_stripped))
    for i in range(1, scan_len):
        char = text_stripped[i]
        if char == '.':
            has_dot = True
            separators_found.add('dot')
        elif char == '/':
            has_slash = True
            separators_found.add('slash')
        elif char == '-':
            has_dash = True
            separators_found.add('dash')
        elif char == ',':
            has_comma = True
            separators_found.add('comma')
        elif char == ' ':
            has_space = True
            separators_found.add('space')
        # Early exit optimization: if we've found all common separators, we can stop
        if len(separators_found) >= 4:
            break
    
    # Build result set based on what we found
    # Be inclusive - if multiple separator types found, include all relevant patterns
    # This ensures we don't miss dates due to format ambiguity
    
    if has_dot:
        result_patterns.extend(_DOT_SEPARATOR_FULL)
        result_patterns.extend(_DOT_LONG_BASEKEYS)
    
    if has_slash:
        result_patterns.extend(_SLASH_SEPARATOR_BASEKEYS)
    
    if has_dash:
        result_patterns.extend(_DASH_SEPARATOR_BASEKEYS)
        result_patterns.extend(_DASH_LONG_BASEKEYS)
    
    if has_comma:
        result_patterns.extend(_RUS_SEPARATOR_BASEKEYS)
        # Comma can also appear in some English formats
        result_patterns.extend(_ALPHA_ENGLISH_FULL)
    
    if has_space:
        # Space is common in many formats - include alpha patterns
        result_patterns.extend(_ALPHA_ENGLISH_FULL)
        result_patterns.extend(_ALPHA_NON_ENGLISH_BASEKEYS)
        # Also digit-based patterns with spaces (e.g., Russian dates)
        result_patterns.extend(_DEFAULT_DIGIT_FULL)
    
    # Always include default digit patterns as fallback
    # This handles cases like "20231215" (no separators), unusual formats,
    # or formats that don't match any specific separator category
    result_patterns.extend(_DEFAULT_DIGIT_FULL)
    
    # If no separators found, also check if it might be ISO format
    # (even if dash isn't in first 10 chars, it might be later)
    if not separators_found and text_len >= 4 and text_stripped[:4].isdigit():
        result_patterns.extend(_DASH_SEPARATOR_BASEKEYS)
    
    # Remove duplicates and return
    return list(set(result_patterns))
