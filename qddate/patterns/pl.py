# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    CaselessLiteral,
    Optional,
)

PL_MONTHS = [
    "Styczeń",
    "Luty",
    "Marzec",
    "Kwiecień",
    "Maj",
    "Czerwiec",
    "Lipiec",
    "Sierpień",
    "Wrzesień",
    "Październik",
    "Listopad",
    "Grudzień",
]

PL_MONTHS_LC = [
    "styczeń",
    "luty",
    "marzec",
    "kwiecień",
    "maj",
    "czerwiec",
    "lipiec",
    "sierpień",
    "wrzesień",
    "październik",
    "listopad",
    "grudzień",
]

PL_MONTHS_GEN = [
    "Stycznia",
    "Lutego",
    "Marca",
    "Kwietnia",
    "Maja",
    "Czerwca",
    "Lipca",
    "Sierpnia",
    "Września",
    "Października",
    "Listopada",
    "Grudnia",
]

PL_MONTHS_GEN_LC = [
    "stycznia",
    "lutego",
    "marca",
    "kwietnia",
    "maja",
    "czerwca",
    "lipca",
    "sierpnia",
    "września",
    "października",
    "listopada",
    "grudnia",
]

# Build a lookup map that understands all supported labels
pl_mname2mon = {}
for idx in range(12):
    for name_list in (
        PL_MONTHS,
        PL_MONTHS_LC,
        PL_MONTHS_GEN,
        PL_MONTHS_GEN_LC,
    ):
        name = name_list[idx]
        if name:
            pl_mname2mon[name] = idx + 1


BASE_PATTERNS_PL = {
    "pat:pl:months":
    oneOf(PL_MONTHS).setParseAction(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_lc":
    oneOf(PL_MONTHS_LC).setParseAction(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_gen":
    oneOf(PL_MONTHS_GEN).setParseAction(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_gen_lc":
    oneOf(PL_MONTHS_GEN_LC).setParseAction(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:year_suffix":
    Optional(
        (
            CaselessLiteral("roku") ^ CaselessLiteral("r.") ^
            CaselessLiteral("r")
        ).suppress()
    ),
}


PATTERNS_PL = [
    # Polish patterns
    {
        "key":
        "dt:date:pl_base",
        "name":
        "Base polish date with month name (nominative)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PL["pat:pl:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_PL["pat:pl:year_suffix"],
        "length": {
            "min": 11,
            "max": 28
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pl_base_lc",
        "name":
        "Base polish date with month name lower-case (nominative)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PL["pat:pl:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_PL["pat:pl:year_suffix"],
        "length": {
            "min": 11,
            "max": 28
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pl_gen",
        "name":
        "Polish date with month name in genitive form",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PL["pat:pl:months_gen"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_PL["pat:pl:year_suffix"],
        "length": {
            "min": 11,
            "max": 28
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pl_gen_lc",
        "name":
        "Polish date with month name in genitive form (lower-case)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PL["pat:pl:months_gen_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_PL["pat:pl:year_suffix"],
        "length": {
            "min": 11,
            "max": 28
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]

