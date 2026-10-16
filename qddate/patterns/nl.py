# -*- coding: utf-8 -*-
"""Dutch month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``NL_MONTHS*`` constants are re-exported.
"""

from pyparsing import (
    Literal,
    Optional,
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_NL = MONTHS_BY_LANGUAGE["nl"]

NL_MONTHS = list(_NL.full)
NL_MONTHS_LC = list(_NL.full_lc)

NL_WEEKDAYS = [
    "Maandag",
    "Dinsdag",
    "Woensdag",
    "Donderdag",
    "Vrijdag",
    "Zaterdag",
    "Zondag",
]
NL_WEEKDAYS_LC = [
    "maandag",
    "dinsdag",
    "woensdag",
    "donderdag",
    "vrijdag",
    "zaterdag",
    "zondag",
]

NL_MONTHS_SHORT = list(_NL.abbrev)
NL_MONTHS_SHORT_LC = list(_NL.abbrev_lc)

nl_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS) if m)
nllc_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_LC) if m)
nlshort_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_SHORT) if m)
nlshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_NL = {
    "pat:nl:months":
    one_of(NL_MONTHS).set_parse_action(lambda t: nl_mname2mon[t[0]]),
    "pat:nl:months_lc":
    one_of(NL_MONTHS_LC).set_parse_action(lambda t: nllc_mname2mon[t[0]]),
    "pat:nl:months_short":
    one_of(NL_MONTHS_SHORT).set_parse_action(lambda t: nlshort_mname2mon[t[0]]),
    "pat:nl:months_short_lc":
    one_of(NL_MONTHS_SHORT_LC).set_parse_action(lambda t: nlshortlc_mname2mon[t[0]]),
    "pat:nl:weekdays":
    one_of(NL_WEEKDAYS),
    "pat:nl:weekdays_lc":
    one_of(NL_WEEKDAYS_LC),
}

PATTERNS_NL = [
    # Dutch patterns
    {
        "key":
        "dt:date:nl_base",
        "name":
        "Base Dutch date with month name",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_NL["pat:nl:months"].set_results_name("month") +
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
        "dt:date:nl_base_lc",
        "name":
        "Base Dutch date with month name lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_NL["pat:nl:months_lc"].set_results_name("month") +
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
    # Weekday patterns
    {
        "key":
        "dt:date:nl_weekday",
        "name":
        "Dutch date with weekday",
        "pattern":
        BASE_PATTERNS_NL["pat:nl:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months"].set_results_name("month") +
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
        "dt:date:nl_weekday_lc",
        "name":
        "Dutch date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_NL["pat:nl:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_lc"].set_results_name("month") +
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
        "dt:date:nl_short",
        "name":
        "Dutch date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_short"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 18
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:nl_short_lc",
        "name":
        "Dutch date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_short_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 18
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Month-first patterns (less common but used)
    {
        "key":
        "dt:date:nl_rare_1",
        "name":
        "Dutch date month-first format",
        "pattern":
        BASE_PATTERNS_NL["pat:nl:months"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:nl_rare_2",
        "name":
        "Dutch date month-first lowercase",
        "pattern":
        BASE_PATTERNS_NL["pat:nl:months_lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
]
