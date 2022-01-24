# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    alphas,
    oneOf,
    lineStart,
    lineEnd,
    Optional,
    restOfLine,
    Literal,
    ParseException,
    CaselessLiteral,
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

# Spanish months map
it_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS) if m)
itlc_mname2mon = dict((m, i + 1) for i, m in enumerate(IT_MONTHS_LC) if m)

BASE_PATTERNS_IT = {
    "pat:it:months": oneOf(IT_MONTHS).setParseAction(lambda t: it_mname2mon[t[0]]),
    "pat:it:months_lc": oneOf(IT_MONTHS_LC).setParseAction(
        lambda t: itlc_mname2mon[t[0]]
    ),
}


PATTERNS_IT = [
    # Italian date patterns
    {
        "key": "dt:date:it_base",
        "name": "Base italian date with month name not article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_IT["pat:it:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:it_base_lc",
        "name": "Base italian date with month name and lowcase, no article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:it_base_article",
        "name": "Base italian date with month name and articles",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_IT["pat:it:months"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:it_base_lc_article",
        "name": "Base italian date with month name and articles and lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:it_rare_1",
        "name": "Italian date stars with month name",
        "pattern": BASE_PATTERNS_IT["pat:it:months"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 25},
        "format": "%M %d %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:it_rare_2",
        "name": "Italian date stars with month name lowcase",
        "pattern": BASE_PATTERNS_IT["pat:it:months_lc"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 25},
        "format": "%M %d %Y",
        "filter": 1,
    },
]
