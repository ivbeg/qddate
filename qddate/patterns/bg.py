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


BG_MONTHS = [
    "Янyapи",
    "Фeвpyapи",
    "Мapт",
    "Апpил",
    "Май",
    "Юни",
    "Юли",
    "Авгycт",
    "Сeптeмвpи",
    "Октoмвpи",
    "Нoeмвpи",
    "Дeкeмвpи",
]
BG_MONTHS_LC = [
    "янyapи",
    "фeвpyapи",
    "мapт",
    "aпpил",
    "май",
    "юни",
    "юли",
    "aвгycт",
    "ceптeмвpи",
    "oктoмвpи",
    "нoeмвpи",
    "дeкeмвpи",
]

# Bulgarian months map
bg_mname2mon = dict((m, i + 1) for i, m in enumerate(BG_MONTHS) if m)
bglc_mname2mon = dict((m, i + 1) for i, m in enumerate(BG_MONTHS_LC) if m)

BASE_PATTERNS_BG = {
    "pat:bg:months": oneOf(BG_MONTHS).setParseAction(lambda t: bg_mname2mon[t[0]]),
    "pat:bg:months_lc": oneOf(BG_MONTHS_LC).setParseAction(
        lambda t: bglc_mname2mon[t[0]]
    ),
}

PATTERNS_BG = [
    # Bulgarian patterns
    {
        "key": "dt:date:bg_base",
        "name": "Base bulgarian date with month name",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_BG["pat:bg:months"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:bg_base_lc",
        "name": "Base bulgarian date with month name and lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_BG["pat:bg:months_lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
