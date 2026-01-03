# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
)

# Incomplete

CZ_WEEKDAYS = [
    "Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"
]
CZ_WEEKDAYS_LC = [
    "pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"
]
CZ_MONTHS = [
    "Leden",
    "Únor",
    "Březen",
    "Duben",
    "Květen",
    "Červen",
    "Červenec",
    "Srpen",
    "Září",
    "Říjen",
    "Listopad",
    "Prosinec",
]
CZ_MONTHS_LC = [
    "leden",
    "únor",
    "březen",
    "duben",
    "květen",
    "červen",
    "červenec",
    "srpen",
    "září",
    "říjen",
    "listopad",
    "prosinec",
]

# Czech months map
cz_mname2mon = dict((m, i + 1) for i, m in enumerate(CZ_MONTHS) if m)
czlc_mname2mon = dict((m, i + 1) for i, m in enumerate(CZ_MONTHS_LC) if m)

# Genitive forms (used in Czech date expressions like "15. ledna")
CZ_MONTHS_GEN = [
    "Ledna",
    "Února",
    "Března",
    "Dubna",
    "Května",
    "Června",
    "Července",
    "Srpna",
    "Září",
    "Října",
    "Listopadu",
    "Prosince",
]
CZ_MONTHS_GEN_LC = [
    "ledna",
    "února",
    "března",
    "dubna",
    "května",
    "června",
    "července",
    "srpna",
    "září",
    "října",
    "listopadu",
    "prosince",
]

# Build a lookup map that understands all supported month forms
cz_mname2mon_all = {}
for idx in range(12):
    for name_list in (CZ_MONTHS, CZ_MONTHS_LC, CZ_MONTHS_GEN, CZ_MONTHS_GEN_LC):
        name = name_list[idx]
        if name:
            cz_mname2mon_all[name] = idx + 1

BASE_PATTERNS_CZ = {
    "pat:cz:weekdays":
    oneOf(CZ_WEEKDAYS),
    "pat:cz:weekdays_lc":
    oneOf(CZ_WEEKDAYS_LC),
    "pat:cz:months":
    oneOf(CZ_MONTHS).setParseAction(lambda t: cz_mname2mon[t[0]]),
    "pat:cz:months_lc":
    oneOf(CZ_MONTHS_LC).setParseAction(lambda t: czlc_mname2mon[t[0]]),
    "pat:cz:months_gen":
    oneOf(CZ_MONTHS_GEN).setParseAction(lambda t: cz_mname2mon_all[t[0]]),
    "pat:cz:months_gen_lc":
    oneOf(CZ_MONTHS_GEN_LC).setParseAction(lambda t: cz_mname2mon_all[t[0]]),
}

PATTERNS_CZ = [
    # Czech date patterns
    {
        "key":
        "dt:date:cz_base",
        "name":
        "Base Czech date with month name (nominative)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_CZ["pat:cz:months"].setResultsName("month") +
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
        "dt:date:cz_base_lc",
        "name":
        "Base Czech date with month name lowercase (nominative)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_CZ["pat:cz:months_lc"].setResultsName("month") +
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
        "dt:date:cz_gen",
        "name":
        "Czech date with month name in genitive form",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_CZ["pat:cz:months_gen"].setResultsName("month") +
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
        "dt:date:cz_gen_lc",
        "name":
        "Czech date with month name in genitive form (lowercase)",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_CZ["pat:cz:months_gen_lc"].setResultsName("month") +
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
]
