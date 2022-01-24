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

# Spanish months map
es_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS) if m)
eslc_mname2mon = dict((m, i + 1) for i, m in enumerate(ES_MONTHS_LC) if m)

BASE_PATTERNS_ES = {
    "pat:es:months": oneOf(ES_MONTHS).setParseAction(lambda t: es_mname2mon[t[0]]),
    "pat:es:months_lc": oneOf(ES_MONTHS_LC).setParseAction(
        lambda t: eslc_mname2mon[t[0]]
    ),
}


PATTERNS_ES = [
    # Spanish patterns
    {
        "key": "dt:date:es_base",
        "name": "Base spanish date with month name not article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_ES["pat:es:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:es_base_lc",
        "name": "Base spanish date with month name and lowcase, no article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:es_base_article",
        "name": "Base spanish date with month name and articles",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_ES["pat:es:months"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:es_base_lc_article",
        "name": "Base spanish date with month name and articles and lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:es_rare_1",
        "name": "Spanish date stars with month name",
        "pattern": BASE_PATTERNS_ES["pat:es:months"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 25},
        "format": "%M %d %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:es_rare_2",
        "name": "Spanish date stars with month name lowcase",
        "pattern": BASE_PATTERNS_ES["pat:es:months_lc"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 25},
        "format": "%M %d %Y",
        "filter": 1,
    },
]
