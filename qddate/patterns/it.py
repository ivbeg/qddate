# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    Literal,
    CaselessLiteral,
    Optional,
)

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

IT_MONTHS = [
    "Gennaio",
    "Febbraio",
    "Marzo",
    "Aprile",
    "Maggio",
    "Giugno",
    "Luglio",
    "Agosto",
    "Settembre",
    "Ottobre",
    "Novembre",
    "Dicembre",
]
IT_MONTHS_LC = [
    "gennaio",
    "febbraio",
    "marzo",
    "aprile",
    "maggio",
    "giugno",
    "luglio",
    "agosto",
    "settembre",
    "ottobre",
    "novembre",
    "dicembre",
]

IT_MONTHS_SHORT = [
    "Gen",
    "Feb",
    "Mar",
    "Apr",
    "Mag",
    "Giu",
    "Lug",
    "Ago",
    "Set",
    "Ott",
    "Nov",
    "Dic",
]
IT_MONTHS_SHORT_LC = [
    "gen",
    "feb",
    "mar",
    "apr",
    "mag",
    "giu",
    "lug",
    "ago",
    "set",
    "ott",
    "nov",
    "dic",
]

# Italian months map
it_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS) if m)
itlc_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_LC) if m)
itshort_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_SHORT) if m)
itshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_IT = {
    "pat:it:months":
    oneOf(IT_MONTHS).setParseAction(lambda t: it_mname2mon[t[0]]),
    "pat:it:months_lc":
    oneOf(IT_MONTHS_LC).setParseAction(lambda t: itlc_mname2mon[t[0]]),
    "pat:it:months_short":
    oneOf(IT_MONTHS_SHORT, caseless=True).setParseAction(lambda t: itshort_mname2mon[t[0].capitalize()]),
    "pat:it:months_short_lc":
    oneOf(IT_MONTHS_SHORT_LC).setParseAction(lambda t: itshortlc_mname2mon[t[0]]),
    "pat:it:weekdays":
    oneOf(IT_WEEKDAYS),
    "pat:it:weekdays_lc":
    oneOf(IT_WEEKDAYS_LC),
}

PATTERNS_IT = [
    # Italian date patterns
    {
        "key":
        "dt:date:it_base",
        "name":
        "Base italian date with month name not article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months"].setResultsName("month") +
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
        "dt:date:it_base_lc",
        "name":
        "Base italian date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month") +
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
        "dt:date:it_base_article",
        "name":
        "Base italian date with month name and articles",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_IT["pat:it:months"].setResultsName("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_IT["pat:it:months"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() + Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() + Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months"].setResultsName("month") +
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
        "dt:date:it_weekday_lc",
        "name":
        "Italian date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_IT["pat:it:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month") +
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
        "dt:date:it_short",
        "name":
        "Italian date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months_short"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_IT["pat:it:months_short_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_IT["pat:it:months_short"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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
        BASE_PATTERNS_IT["pat:it:months_short_lc"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).setResultsName("year"),
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
