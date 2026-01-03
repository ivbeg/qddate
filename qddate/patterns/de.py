# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    Optional,
    Literal,
)

DE_MONTHS = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]
DE_MONTHS_LC = [
    "januar",
    "februar",
    "märz",
    "april",
    "mai",
    "juni",
    "juli",
    "august",
    "september",
    "oktober",
    "november",
    "dezember",
]

DE_WEEKDAYS = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]
DE_WEEKDAYS_LC = [
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
]

DE_MONTHS_SHORT = [
    "Jan",
    "Feb",
    "Mär",
    "Apr",
    "Mai",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Okt",
    "Nov",
    "Dez",
]
DE_MONTHS_SHORT_LC = [
    "jan",
    "feb",
    "mär",
    "apr",
    "mai",
    "jun",
    "jul",
    "aug",
    "sep",
    "okt",
    "nov",
    "dez",
]

# German months map
de_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS) if m)
delc_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_LC) if m)
deshort_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_SHORT) if m)
deshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_DE = {
    "pat:de:months":
    oneOf(DE_MONTHS).setParseAction(lambda t: de_mname2mon[t[0]]),
    "pat:de:months_lc":
    oneOf(DE_MONTHS_LC).setParseAction(lambda t: delc_mname2mon[t[0]]),
    "pat:de:months_short":
    oneOf(DE_MONTHS_SHORT).setParseAction(lambda t: deshort_mname2mon[t[0]]),
    "pat:de:months_short_lc":
    oneOf(DE_MONTHS_SHORT_LC).setParseAction(lambda t: deshortlc_mname2mon[t[0]]),
    "pat:de:weekdays":
    oneOf(DE_WEEKDAYS),
    "pat:de:weekdays_lc":
    oneOf(DE_WEEKDAYS_LC),
}

PATTERNS_DE = [
    # German patterns
    {
        "key":
        "dt:date:de_base",
        "name":
        "Base german date with month name",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_DE["pat:de:months"].setResultsName("month") +
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
        "dt:date:de_base_lc",
        "name":
        "Base german date with month name and lowcase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_DE["pat:de:months_lc"].setResultsName("month") +
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
        "dt:date:de_weekday",
        "name":
        "German date with weekday",
        "pattern":
        BASE_PATTERNS_DE["pat:de:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months"].setResultsName("month") +
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
        "dt:date:de_weekday_lc",
        "name":
        "German date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_DE["pat:de:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_lc"].setResultsName("month") +
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
        "dt:date:de_short",
        "name":
        "German date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_short"].setResultsName("month") +
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
        "dt:date:de_short_lc",
        "name":
        "German date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_short_lc"].setResultsName("month") +
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
    # Rare patterns (month-first)
    {
        "key":
        "dt:date:de_rare_1",
        "name":
        "German date month-first format",
        "pattern":
        BASE_PATTERNS_DE["pat:de:months"].setResultsName("month") +
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
        "dt:date:de_rare_2",
        "name":
        "German date month-first lowercase",
        "pattern":
        BASE_PATTERNS_DE["pat:de:months_lc"].setResultsName("month") +
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
