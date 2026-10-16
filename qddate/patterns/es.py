# -*- coding: utf-8 -*-
"""Spanish month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``ES_MONTHS*`` constants are re-exported.
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

_ES = MONTHS_BY_LANGUAGE["es"]

ES_MONTHS = list(_ES.full)
ES_MONTHS_LC = list(_ES.full_lc)
ES_MONTHS_SHORT = list(_ES.abbrev)
ES_MONTHS_SHORT_LC = list(_ES.abbrev_lc)

ES_WEEKDAYS = [
    "Lunes",
    "Martes",
    "Miércoles",
    "Jueves",
    "Viernes",
    "Sábado",
    "Domingo",
]
ES_WEEKDAYS_LC = [
    "lunes",
    "martes",
    "miércoles",
    "jueves",
    "viernes",
    "sábado",
    "domingo",
]

es_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS) if m)
eslc_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_LC) if m)
esshort_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_SHORT) if m)
esshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_ES = {
    "pat:es:months":
    one_of(ES_MONTHS).set_parse_action(lambda t: es_mname2mon[t[0]]),
    "pat:es:months_lc":
    one_of(ES_MONTHS_LC).set_parse_action(lambda t: eslc_mname2mon[t[0]]),
    "pat:es:months_short":
    one_of(ES_MONTHS_SHORT, caseless=True).set_parse_action(lambda t: esshort_mname2mon[t[0].capitalize()]),
    "pat:es:months_short_lc":
    one_of(ES_MONTHS_SHORT_LC).set_parse_action(lambda t: esshortlc_mname2mon[t[0]]),
    "pat:es:weekdays":
    one_of(ES_WEEKDAYS),
    "pat:es:weekdays_lc":
    one_of(ES_WEEKDAYS_LC),
}

PATTERNS_ES = [
    # Spanish patterns
    {
        "key":
        "dt:date:es_base",
        "name":
        "Base spanish date with month name not article",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_ES["pat:es:months"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
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
        "dt:date:es_base_lc",
        "name":
        "Base spanish date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_ES["pat:es:months_lc"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
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
        "dt:date:es_base_article",
        "name":
        "Base spanish date with month name and articles",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_ES["pat:es:months"].set_results_name("month") +
        (CaselessLiteral("de").suppress() | Literal(",").suppress()) +
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
        "dt:date:es_base_lc_article",
        "name":
        "Base spanish date with month name and articles and lowcase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_ES["pat:es:months_lc"].set_results_name("month") +
        (CaselessLiteral("de").suppress() | Literal(",").suppress()) +
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
        "dt:date:es_rare_1",
        "name":
        "Spanish date stars with month name",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months"].set_results_name("month") +
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
        "dt:date:es_rare_2",
        "name":
        "Spanish date stars with month name lowcase",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_lc"].set_results_name("month") +
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
    # Abbreviated month patterns
    {
        "key":
        "dt:date:es_short",
        "name":
        "Spanish date with abbreviated month",
        "pattern":
        (Word(nums, min=1, max=2).set_results_name("day") +
         BASE_PATTERNS_ES["pat:es:months_short"].set_results_name("month") +
         Word(nums, exact=4).set_results_name("year")) |
        (Word(nums, min=1, max=2).set_results_name("day") +
         CaselessLiteral("de").suppress() +
         BASE_PATTERNS_ES["pat:es:months_short"].set_results_name("month") +
         CaselessLiteral("de").suppress() +
         Word(nums, exact=4).set_results_name("year")),
        "length": {
            "min": 9,
            "max": 20
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:es_short_lc",
        "name":
        "Spanish date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_ES["pat:es:months_short_lc"].set_results_name("month") +
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
        "dt:date:es_short_monthfirst",
        "name":
        "Spanish date with abbreviated month (month first)",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_short"].set_results_name("month") +
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
        "dt:date:es_short_lc_monthfirst",
        "name":
        "Spanish date with abbreviated month lowercase (month first)",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_short_lc"].set_results_name("month") +
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
    # Weekday patterns
    {
        "key":
        "dt:date:es_weekday",
        "name":
        "Spanish date with weekday",
        "pattern":
        BASE_PATTERNS_ES["pat:es:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_ES["pat:es:months"].set_results_name("month") +
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
        "dt:date:es_weekday_lc",
        "name":
        "Spanish date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_ES["pat:es:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_ES["pat:es:months_lc"].set_results_name("month") +
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
]
