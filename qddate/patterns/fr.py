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


FR_MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]
FR_MONTHS_LC = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]

# French months map
fr_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS) if m)
frlc_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_LC) if m)

BASE_PATTERNS_FR = {
    "pat:fr:months": oneOf(FR_MONTHS).setParseAction(lambda t: fr_mname2mon[t[0]]),
    "pat:fr:months_lc": oneOf(FR_MONTHS_LC).setParseAction(
        lambda t: frlc_mname2mon[t[0]]
    ),
}

PATTERNS_FR = [
    # French patterns
    {
        "key": "dt:date:fr_base",
        "name": "Base french date with month name not archive",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:fr_base_lc",
        "name": "Base french date with month name and lowcase, no article",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:fr_base_article",
        "name": "Base french date with month name and articles",
        "pattern": CaselessLiteral("Le").suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:fr_base_lc_article",
        "name": "Base french date with month name and articles and lowcase",
        "pattern": CaselessLiteral("le").suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
