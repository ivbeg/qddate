# -*- coding: utf-8 -*-
"""Polish month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``PL_MONTHS*`` constants are re-exported;
``pl_mname2mon`` is the unified lookup across nominative and genitive variants.
"""

from pyparsing import (
    CaselessLiteral,
    Optional,
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_PL = MONTHS_BY_LANGUAGE["pl"]

PL_MONTHS = list(_PL.full)
PL_MONTHS_LC = list(_PL.full_lc)
PL_MONTHS_GEN = list(_PL.genitive or ())
PL_MONTHS_GEN_LC = list(_PL.genitive_lc or ())

# Unified lookup: every variant → month number. Built once at import.
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
    one_of(PL_MONTHS).set_parse_action(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_lc":
    one_of(PL_MONTHS_LC).set_parse_action(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_gen":
    one_of(PL_MONTHS_GEN).set_parse_action(lambda t: pl_mname2mon[t[0]]),
    "pat:pl:months_gen_lc":
    one_of(PL_MONTHS_GEN_LC).set_parse_action(lambda t: pl_mname2mon[t[0]]),
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
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_PL["pat:pl:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") +
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
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_PL["pat:pl:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") +
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
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_PL["pat:pl:months_gen"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") +
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
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_PL["pat:pl:months_gen_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") +
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
