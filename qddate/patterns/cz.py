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

# Incomplete

CZ_WEEKDAYS = ["Pondělí", "Úterý", "Středa", "Čtvrtek", "Pátek", "Sobota", "Neděle"]
CZ_WEEKDAYS_LC = ["pondělí", "úterý", "středa", "čtvrtek", "pátek", "sobota", "neděle"]
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

BASE_PATTERNS_CZ = {
    "pat:cz:weekdays": oneOf(CZ_WEEKDAYS),
    "pat:cz:weekdays_lc": oneOf(CZ_WEEKDAYS_LC),
    "pat:cz:months": oneOf(CZ_MONTHS).setParseAction(lambda t: cz_mname2mon[t[0]]),
    "pat:cz:months_lc": oneOf(CZ_MONTHS_LC).setParseAction(
        lambda t: czlc_mname2mon[t[0]]
    ),
}

PATTERNS_CZ = []
