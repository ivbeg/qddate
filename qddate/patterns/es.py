# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    Literal,
    CaselessLiteral,
    Optional,
)

ES_MONTHS = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
]
ES_MONTHS_LC = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

ES_MONTHS_SHORT = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]
ES_MONTHS_SHORT_LC = [
    "ene",
    "feb",
    "mar",
    "abr",
    "may",
    "jun",
    "jul",
    "ago",
    "sep",
    "oct",
    "nov",
    "dic",
]

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

# Spanish months map
es_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS) if m)
eslc_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_LC) if m)
esshort_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_SHORT) if m)
esshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_ES = {
    "pat:es:months":
    oneOf(ES_MONTHS).setParseAction(lambda t: es_mname2mon[t[0]]),
    "pat:es:months_lc":
    oneOf(ES_MONTHS_LC).setParseAction(lambda t: eslc_mname2mon[t[0]]),
    "pat:es:months_short":
    oneOf(ES_MONTHS_SHORT, caseless=True).setParseAction(lambda t: esshort_mname2mon[t[0].capitalize()]),
    "pat:es:months_short_lc":
    oneOf(ES_MONTHS_SHORT_LC).setParseAction(lambda t: esshortlc_mname2mon[t[0]]),
    "pat:es:weekdays":
    oneOf(ES_WEEKDAYS),
    "pat:es:weekdays_lc":
    oneOf(ES_WEEKDAYS_LC),
}

PATTERNS_ES = [
    # Spanish patterns
    {
        "key":
        "dt:date:es_base",
        "name":
        "Base spanish date with month name not article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_ES["pat:es:months"].setResultsName("month") +
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
        "dt:date:es_base_lc",
        "name":
        "Base spanish date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month") +
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
        "dt:date:es_base_article",
        "name":
        "Base spanish date with month name and articles",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_ES["pat:es:months"].setResultsName("month") +
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
        "dt:date:es_base_lc_article",
        "name":
        "Base spanish date with month name and articles and lowcase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month") +
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
        "dt:date:es_rare_1",
        "name":
        "Spanish date stars with month name",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months"].setResultsName("month") +
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
        "dt:date:es_rare_2",
        "name":
        "Spanish date stars with month name lowcase",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month") +
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
    # Abbreviated month patterns
    {
        "key":
        "dt:date:es_short",
        "name":
        "Spanish date with abbreviated month",
        "pattern":
        (Word(nums, min=1, max=2).setResultsName("day") +
         BASE_PATTERNS_ES["pat:es:months_short"].setResultsName("month") +
         Word(nums, exact=4).setResultsName("year")) |
        (Word(nums, min=1, max=2).setResultsName("day") +
         CaselessLiteral("de").suppress() +
         BASE_PATTERNS_ES["pat:es:months_short"].setResultsName("month") +
         CaselessLiteral("de").suppress() +
         Word(nums, exact=4).setResultsName("year")),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_ES["pat:es:months_short_lc"].setResultsName("month") +
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
        "dt:date:es_short_monthfirst",
        "name":
        "Spanish date with abbreviated month (month first)",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_short"].setResultsName("month") +
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
        "dt:date:es_short_lc_monthfirst",
        "name":
        "Spanish date with abbreviated month lowercase (month first)",
        "pattern":
        BASE_PATTERNS_ES["pat:es:months_short_lc"].setResultsName("month") +
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
    # Weekday patterns
    {
        "key":
        "dt:date:es_weekday",
        "name":
        "Spanish date with weekday",
        "pattern":
        BASE_PATTERNS_ES["pat:es:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_ES["pat:es:months"].setResultsName("month") +
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
        "dt:date:es_weekday_lc",
        "name":
        "Spanish date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_ES["pat:es:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month") +
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
]
