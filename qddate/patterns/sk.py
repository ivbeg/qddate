# -*- coding: utf-8 -*-
"""Slovak month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Slovak writes the day with a dot and the month in
the genitive (``5. mája 2022``); the nominative (``5. máj 2022``) and a day
without a dot are accepted too, as for Czech.
"""

from pyparsing import (
    Optional,
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_SK = MONTHS_BY_LANGUAGE["sk"]

SK_WEEKDAYS = [
    "Pondelok", "Utorok", "Streda", "Štvrtok", "Piatok", "Sobota", "Nedeľa"
]
SK_WEEKDAYS_LC = [
    "pondelok", "utorok", "streda", "štvrtok", "piatok", "sobota", "nedeľa"
]
SK_MONTHS = list(_SK.full)
SK_MONTHS_LC = list(_SK.full_lc)
SK_MONTHS_GEN = list(_SK.genitive or ())
SK_MONTHS_GEN_LC = list(_SK.genitive_lc or ())

# Every form (nominative and genitive, capitalised and lower-case) → month.
sk_mname2mon = dict(_SK.month_to_int)

BASE_PATTERNS_SK = {
    "pat:sk:months":
    one_of(SK_MONTHS).set_parse_action(lambda t: sk_mname2mon[t[0]]),
    "pat:sk:months_lc":
    one_of(SK_MONTHS_LC).set_parse_action(lambda t: sk_mname2mon[t[0]]),
    "pat:sk:months_gen":
    one_of(SK_MONTHS_GEN).set_parse_action(lambda t: sk_mname2mon[t[0]]),
    "pat:sk:months_gen_lc":
    one_of(SK_MONTHS_GEN_LC).set_parse_action(lambda t: sk_mname2mon[t[0]]),
}


def _sk_pattern(key, name, months):
    """Day, optional dot, month name of ``months`` and a four-digit year."""
    return {
        "key": key,
        "name": name,
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_SK[months].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 18
        },
        "format": "%d %m %Y",
        "filter": 1,
    }


PATTERNS_SK = [
    _sk_pattern("dt:date:sk_base", "Base Slovak date with month name (nominative)",
                "pat:sk:months"),
    _sk_pattern("dt:date:sk_base_lc", "Base Slovak date with month name lowercase (nominative)",
                "pat:sk:months_lc"),
    _sk_pattern("dt:date:sk_gen", "Slovak date with month name in genitive form",
                "pat:sk:months_gen"),
    _sk_pattern("dt:date:sk_gen_lc", "Slovak date with month name in genitive form (lowercase)",
                "pat:sk:months_gen_lc"),
]
