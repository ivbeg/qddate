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

# German months map
de_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS) if m)
delc_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_LC) if m)

BASE_PATTERNS_DE = {
    "pat:de:months": oneOf(DE_MONTHS).setParseAction(lambda t: de_mname2mon[t[0]]),
    "pat:de:months_lc": oneOf(DE_MONTHS_LC).setParseAction(
        lambda t: delc_mname2mon[t[0]]
    ),
}

PATTERNS_DE = [
    # German patterns
    {
        "key": "dt:date:de_base",
        "name": "Base german date with month name",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_DE["pat:de:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:de_base_lc",
        "name": "Base german date with month name and lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_DE["pat:de:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
