# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    Optional,
    Literal,
)

NL_MONTHS = [
    "Januari",
    "Februari",
    "Maart",
    "April",
    "Mei",
    "Juni",
    "Juli",
    "Augustus",
    "September",
    "Oktober",
    "November",
    "December",
]
NL_MONTHS_LC = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]

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

NL_MONTHS_SHORT = [
    "Jan",
    "Feb",
    "Mrt",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Okt",
    "Nov",
    "Dec",
]
NL_MONTHS_SHORT_LC = [
    "jan",
    "feb",
    "mrt",
    "apr",
    "mei",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dec",
]

# Dutch months map
nl_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS) if m)
nllc_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_LC) if m)
nlshort_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_SHORT) if m)
nlshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(NL_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_NL = {
    "pat:nl:months":
    oneOf(NL_MONTHS).setParseAction(lambda t: nl_mname2mon[t[0]]),
    "pat:nl:months_lc":
    oneOf(NL_MONTHS_LC).setParseAction(lambda t: nllc_mname2mon[t[0]]),
    "pat:nl:months_short":
    oneOf(NL_MONTHS_SHORT).setParseAction(lambda t: nlshort_mname2mon[t[0]]),
    "pat:nl:months_short_lc":
    oneOf(NL_MONTHS_SHORT_LC).setParseAction(lambda t: nlshortlc_mname2mon[t[0]]),
    "pat:nl:weekdays":
    oneOf(NL_WEEKDAYS),
    "pat:nl:weekdays_lc":
    oneOf(NL_WEEKDAYS_LC),
}

PATTERNS_NL = [
    # Dutch patterns
    {
        "key":
        "dt:date:nl_base",
        "name":
        "Base Dutch date with month name",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_NL["pat:nl:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_NL["pat:nl:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_short"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_NL["pat:nl:months_short_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_NL["pat:nl:months"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_NL["pat:nl:months_lc"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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

