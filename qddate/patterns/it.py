# -*- coding: utf-8 -*-
"""Italian month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``IT_MONTHS*`` constants are re-exported.
"""

from pyparsing import (
    CaselessLiteral,
    Literal,
    Optional,
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_IT = MONTHS_BY_LANGUAGE["it"]

IT_WEEKDAYS = [
    "Lunedì",
    "Martedì",
    "Mercoledì",
    "Giovedì",
    "Venerdì",
    "Sabato",
    "Domenica",
]
IT_WEEKDAYS_LC = [
    "lunedì",
    "martedì",
    "mercoledì",
    "giovedì",
    "venerdì",
    "sabato",
    "domenica",
]

IT_MONTHS = list(_IT.full)
IT_MONTHS_LC = list(_IT.full_lc)
IT_MONTHS_SHORT = list(_IT.abbrev)
IT_MONTHS_SHORT_LC = list(_IT.abbrev_lc)

it_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS) if m)
itlc_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_LC) if m)
itshort_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_SHORT) if m)
itshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_IT = {
    "pat:it:months":
    one_of(IT_MONTHS).set_parse_action(lambda t: it_mname2mon[t[0]]),
    "pat:it:months_lc":
    one_of(IT_MONTHS_LC).set_parse_action(lambda t: itlc_mname2mon[t[0]]),
    "pat:it:months_short":
    one_of(IT_MONTHS_SHORT, caseless=True).set_parse_action(lambda t: itshort_mname2mon[t[0].capitalize()]),
    "pat:it:months_short_lc":
    one_of(IT_MONTHS_SHORT_LC).set_parse_action(lambda t: itshortlc_mname2mon[t[0]]),
    "pat:it:weekdays":
    one_of(IT_WEEKDAYS),
    "pat:it:weekdays_lc":
    one_of(IT_WEEKDAYS_LC),
}

PATTERNS_IT = [
    # Italian date patterns
    {
        "key":
        "dt:date:it_base",
        "name":
        "Base italian date with month name not article",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 22
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_base_lc",
        "name":
        "Base italian date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 22
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_base_article",
        "name":
        "Base italian date with month name and articles",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_IT["pat:it:months"].set_results_name("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 26
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_base_lc_article",
        "name":
        "Base italian date with month name and articles and lowcase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_IT["pat:it:months_lc"].set_results_name("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 26
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_rare_1",
        "name":
        "Italian date stars with month name",
        "pattern":
        BASE_PATTERNS_IT["pat:it:months"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%M %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_rare_2",
        "name":
        "Italian date stars with month name lowcase",
        "pattern":
        BASE_PATTERNS_IT["pat:it:months_lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%M %d %Y",
        "filter":
        1,
    },
    # Weekday patterns
    {
        "key":
        "dt:date:it_weekday",
        "name":
        "Italian date with weekday",
        "pattern":
        BASE_PATTERNS_IT["pat:it:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 15,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_weekday_lc",
        "name":
        "Italian date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_IT["pat:it:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 15,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Abbreviated month patterns
    {
        "key":
        "dt:date:it_short",
        "name":
        "Italian date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months_short"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 13
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_short_lc",
        "name":
        "Italian date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_IT["pat:it:months_short_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 13
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_short_monthfirst",
        "name":
        "Italian date with abbreviated month (month first)",
        "pattern":
        BASE_PATTERNS_IT["pat:it:months_short"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:it_short_lc_monthfirst",
        "name":
        "Italian date with abbreviated month lowercase (month first)",
        "pattern":
        BASE_PATTERNS_IT["pat:it:months_short_lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
]
