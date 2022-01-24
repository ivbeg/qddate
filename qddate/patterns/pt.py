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

PT_MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
PT_MONTHS_LC = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]

# Portugal months map
pt_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS) if m)
ptlc_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS_LC) if m)

BASE_PATTERNS_PT = {
    "pat:pt:months": oneOf(PT_MONTHS).setParseAction(lambda t: pt_mname2mon[t[0]]),
    "pat:pt:months_lc": oneOf(PT_MONTHS_LC).setParseAction(
        lambda t: ptlc_mname2mon[t[0]]
    ),
}

PATTERNS_PT = [
    # Portugal patterns
    {
        "key": "dt:date:pt_base",
        "name": "Base portugal date with month name not article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:pt_base_lc",
        "name": "Base portugal date with month name and lowcase, no article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:pt_base_article",
        "name": "Base portugal date with month name and articles",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:pt_base_lc_article",
        "name": "Base portugal date with month name and articles and lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + CaselessLiteral("de").suppress()
        + BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month")
        + CaselessLiteral("de").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 26},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
