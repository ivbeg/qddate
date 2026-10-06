# -*- coding: utf-8 -*-
"""Czech month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``CZ_MONTHS*`` constants are re-exported;
``cz_mname2mon_all`` is the unified lookup across nominative and genitive
variants.
"""

from pyparsing import (
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_CZ = MONTHS_BY_LANGUAGE["cz"]

# Incomplete
CZ_WEEKDAYS = [
    "Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"
]
CZ_WEEKDAYS_LC = [
    "pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"
]
CZ_MONTHS = list(_CZ.full)
CZ_MONTHS_LC = list(_CZ.full_lc)
CZ_MONTHS_GEN = list(_CZ.genitive or ())
CZ_MONTHS_GEN_LC = list(_CZ.genitive_lc or ())

cz_mname2mon = dict((m, i + 1) for i, m in enumerate(CZ_MONTHS) if m)
czlc_mname2mon = dict((m, i + 1) for i, m in enumerate(CZ_MONTHS_LC) if m)

# Unified lookup covering every supported form.
cz_mname2mon_all = {}
for idx in range(12):
    for name_list in (CZ_MONTHS, CZ_MONTHS_LC, CZ_MONTHS_GEN, CZ_MONTHS_GEN_LC):
        name = name_list[idx]
        if name:
            cz_mname2mon_all[name] = idx + 1

BASE_PATTERNS_CZ = {
    "pat:cz:weekdays":
    one_of(CZ_WEEKDAYS),
    "pat:cz:weekdays_lc":
    one_of(CZ_WEEKDAYS_LC),
    "pat:cz:months":
    one_of(CZ_MONTHS).set_parse_action(lambda t: cz_mname2mon[t[0]]),
    "pat:cz:months_lc":
    one_of(CZ_MONTHS_LC).set_parse_action(lambda t: czlc_mname2mon[t[0]]),
    "pat:cz:months_gen":
    one_of(CZ_MONTHS_GEN).set_parse_action(lambda t: cz_mname2mon_all[t[0]]),
    "pat:cz:months_gen_lc":
    one_of(CZ_MONTHS_GEN_LC).set_parse_action(lambda t: cz_mname2mon_all[t[0]]),
}

PATTERNS_CZ = [
    # Czech date patterns
    {
        "key":
        "dt:date:cz_base",
        "name":
        "Base Czech date with month name (nominative)",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_CZ["pat:cz:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
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
        "dt:date:cz_base_lc",
        "name":
        "Base Czech date with month name lowercase (nominative)",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_CZ["pat:cz:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
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
        "dt:date:cz_gen",
        "name":
        "Czech date with month name in genitive form",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_CZ["pat:cz:months_gen"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
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
        "dt:date:cz_gen_lc",
        "name":
        "Czech date with month name in genitive form (lowercase)",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_CZ["pat:cz:months_gen_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 22
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]
