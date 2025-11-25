#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Here is all dirty matched code
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

# Pre-computed basekey lists as constants for performance optimization
_ALPHA_ENGLISH_BASEKEYS = [
    "dt:date:eng1",
    "dt:date:date_eng1x",
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
]

_PT_BASEKEYS = [
    "dt:date:pt_base",
    "dt:date:pt_base_lc",
    "dt:date:pt_base_article",
    "dt:date:pt_base_lc_article",
]

_ES_BASEKEYS = [
    "dt:date:es_base",
    "dt:date:es_base_lc",
    "dt:date:es_base_article",
    "dt:date:es_base_lc_article",
    "dt:date:es_rare_1",
    "dt:date:es_rare_2",
]

_IT_BASEKEYS = [
    "dt:date:it_base",
    "dt:date:it_base_lc",
    "dt:date:it_base_article",
    "dt:date:it_base_lc_article",
    "dt:date:it_rare_1",
    "dt:date:it_rare_2",
]

_ALPHA_NON_ENGLISH_BASEKEYS = [
    "dt:date:weekday_rus",
    "dt:date:weekday_rus_lc1",
    "dt:date:rare_5",
    "dt:date:rare_6",
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
]

_DE_BASEKEYS = ["dt:date:de_base", "dt:date:de_base_lc"]

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
    "dt:date:fr_base",
    "dt:date:fr_base_lc",
]

_BG_BASEKEYS = ["dt:date:bg_base", "dt:date:bg_base_lc"]


def matchPrefix(text):
    """
    This is silver bullet, cornerstone and magic wand of speed of this algorithm
    it filters patterns using manually selected rules. Yes, yes, it's "dirty" code and it could be beautified in
    many ways but this library intended to be fast, not beautiful. Without matching is x1.3 slower so let it be.
    :param text: text with date to match
    :return: list of patterns to run against
    """
    text_len = len(text)
    if text_len == 0:
        return []
    
    if not text[0].isdigit():
        fc = text[0].lower()
#        fc = fc if len(fc) > 1 else text[0].lower()
        if fc.isalpha() and ord(fc) in range(ord("a"), ord("z") + 1):
            # Use pre-computed lists for better performance
            basekeys = _ALPHA_ENGLISH_BASEKEYS.copy()
            basekeys.extend(_PT_BASEKEYS)
            basekeys.extend(_ES_BASEKEYS)
            basekeys.extend(_IT_BASEKEYS)
        else:
            basekeys = _ALPHA_NON_ENGLISH_BASEKEYS.copy()
    else:
        if text_len > 2 and (text[1] == "." or text[2] == "."):
            basekeys = _DOT_SEPARATOR_BASEKEYS.copy()
            basekeys.extend(_DE_BASEKEYS)
        elif text_len > 2 and (text[1] == "," or text[2] == ","):
            basekeys = ["dt:date:date_rus"]
        elif text_len > 2 and (text[1] == "/" or text[2] == "/"):
            basekeys = _SLASH_SEPARATOR_BASEKEYS.copy()
        elif text_len > 2 and (text[1] == "-" or text[2] == "-"):
            basekeys = _DASH_SEPARATOR_BASEKEYS.copy()
        elif text_len > 4 and text[4] == "-":
            basekeys = ["dt:date:date_iso8601", "dt:date:date_9"]
        elif text_len > 4 and text[4] == ".":
            basekeys = ["dt:date:date_10"]
        else:
            # Use pre-computed lists for better performance
            basekeys = _DEFAULT_DIGIT_BASEKEYS.copy()
            basekeys.extend(_EXTENDED_DIGIT_BASEKEYS)
            basekeys.extend(_PT_BASEKEYS)
            basekeys.extend(_DE_BASEKEYS)
            basekeys.extend(_BG_BASEKEYS)
            basekeys.extend(_ES_BASEKEYS)
            basekeys.extend(_IT_BASEKEYS)
    #        print('Basekeys', basekeys, 'for', text)
    return basekeys
