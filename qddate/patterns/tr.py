# -*- coding: utf-8 -*-
"""Turkish month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``TR_MONTHS*`` constants are re-exported.
"""

from pyparsing import Optional, Word, nums, one_of

from .months import MONTHS_BY_LANGUAGE

_TR = MONTHS_BY_LANGUAGE["tr"]

TR_MONTHS = list(_TR.full)
TR_MONTHS_LC = list(_TR.full_lc)

tr_mname2mon = dict((m, i + 1) for i, m in enumerate(TR_MONTHS) if m)
trlc_mname2mon = dict((m, i + 1) for i, m in enumerate(TR_MONTHS_LC) if m)

BASE_PATTERNS_TR = {
    "pat:tr:months":
    one_of(TR_MONTHS).set_parse_action(lambda t: tr_mname2mon[t[0]]),
    "pat:tr:months_lc":
    one_of(TR_MONTHS_LC).set_parse_action(lambda t: trlc_mname2mon[t[0]]),
}

TURKISH_SUFFIX = Optional(
    one_of(["tarihinde", "tarihli"], caseless=True)).suppress()

PATTERNS_TR = [
    {
        "key":
        "dt:date:tr_base",
        "name":
        "Base Turkish date with capitalized month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_TR["pat:tr:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") + TURKISH_SUFFIX,
        "length": {
            "min": 11,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:tr_base_lc",
        "name":
        "Base Turkish date with lowercase month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_TR["pat:tr:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") + TURKISH_SUFFIX,
        "length": {
            "min": 11,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]
