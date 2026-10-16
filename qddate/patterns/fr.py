# -*- coding: utf-8 -*-
"""French month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``FR_MONTHS*`` constants are re-exported.
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

_FR = MONTHS_BY_LANGUAGE["fr"]

FR_MONTHS = list(_FR.full)
FR_MONTHS_LC = list(_FR.full_lc)
FR_MONTHS_SHORT = list(_FR.abbrev)
FR_MONTHS_SHORT_LC = list(_FR.abbrev_lc)

FR_WEEKDAYS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
FR_WEEKDAYS_LC = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

fr_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS) if m)
frlc_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_LC) if m)
frshort_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_SHORT) if m)
frshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_FR = {
    "pat:fr:months":
    one_of(FR_MONTHS).set_parse_action(lambda t: fr_mname2mon[t[0]]),
    "pat:fr:months_lc":
    one_of(FR_MONTHS_LC).set_parse_action(lambda t: frlc_mname2mon[t[0]]),
    "pat:fr:months_short":
    one_of(FR_MONTHS_SHORT, caseless=True).set_parse_action(lambda t: frshort_mname2mon[t[0].capitalize()]),
    "pat:fr:months_short_lc":
    one_of(FR_MONTHS_SHORT_LC).set_parse_action(lambda t: frshortlc_mname2mon[t[0]]),
    "pat:fr:weekdays":
    one_of(FR_WEEKDAYS),
    "pat:fr:weekdays_lc":
    one_of(FR_WEEKDAYS_LC),
}

PATTERNS_FR = [
    # French patterns
    {
        "key":
        "dt:date:fr_base",
        "name":
        "Base french date with month name not archive",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months"].set_results_name("month") +
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
        "dt:date:fr_base_lc",
        "name":
        "Base french date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].set_results_name("month") +
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
        "dt:date:fr_base_article",
        "name":
        "Base french date with month name and articles",
        "pattern":
        CaselessLiteral("Le").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months"].set_results_name("month") +
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
        "dt:date:fr_base_lc_article",
        "name":
        "Base french date with month name and articles and lowcase",
        "pattern":
        CaselessLiteral("le").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].set_results_name("month") +
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
    # Abbreviated month patterns
    {
        "key":
        "dt:date:fr_short",
        "name":
        "French date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months_short"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_lc",
        "name":
        "French date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months_short_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_monthfirst",
        "name":
        "French date with abbreviated month (month first)",
        "pattern":
        (BASE_PATTERNS_FR["pat:fr:months_short"].set_results_name("month") +
         Word(nums, min=1, max=2).set_results_name("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).set_results_name("year")) |
        (BASE_PATTERNS_FR["pat:fr:months"].set_results_name("month") +
         Word(nums, min=1, max=2).set_results_name("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).set_results_name("year")),
        "length": {
            "min": 9,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_lc_monthfirst",
        "name":
        "French date with abbreviated month lowercase (month first)",
        "pattern":
        (BASE_PATTERNS_FR["pat:fr:months_short_lc"].set_results_name("month") +
         Word(nums, min=1, max=2).set_results_name("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).set_results_name("year")) |
        (BASE_PATTERNS_FR["pat:fr:months_lc"].set_results_name("month") +
         Word(nums, min=1, max=2).set_results_name("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).set_results_name("year")),
        "length": {
            "min": 9,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    # Weekday patterns
    {
        "key":
        "dt:date:fr_weekday",
        "name":
        "French date with weekday",
        "pattern":
        BASE_PATTERNS_FR["pat:fr:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months"].set_results_name("month") +
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
        "dt:date:fr_weekday_lc",
        "name":
        "French date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_FR["pat:fr:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].set_results_name("month") +
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
