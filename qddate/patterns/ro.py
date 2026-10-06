# -*- coding: utf-8 -*-
"""Romanian month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``RO_MONTHS*`` constants are re-exported.
Note: ``ro.detect_excludes`` (Mai/august) prevents the language detector from
relabelling ambiguous English/Portuguese/German/Dutch text as Romanian.
"""

from pyparsing import Word, nums, one_of

from .months import MONTHS_BY_LANGUAGE

_RO = MONTHS_BY_LANGUAGE["ro"]

RO_MONTHS = list(_RO.full)
RO_MONTHS_LC = list(_RO.full_lc)

# Unicode CLDR Romanian Gregorian abbreviated month forms. The period is part
# of every abbreviation except "mai" and must be present for these patterns.
RO_MONTHS_SHORT = list(_RO.abbrev)
RO_MONTHS_SHORT_LC = list(_RO.abbrev_lc)


ro_mname2mon = {month: index + 1 for index, month in enumerate(RO_MONTHS)}
rolc_mname2mon = {month: index + 1 for index, month in enumerate(RO_MONTHS_LC)}
roshort_mname2mon = {month: index + 1 for index, month in enumerate(RO_MONTHS_SHORT)}
roshortlc_mname2mon = {
    month: index + 1 for index, month in enumerate(RO_MONTHS_SHORT_LC)
}


BASE_PATTERNS_RO = {
    "pat:ro:months": one_of(RO_MONTHS).set_parse_action(lambda tokens: ro_mname2mon[tokens[0]]),
    "pat:ro:months_lc": one_of(RO_MONTHS_LC).set_parse_action(
        lambda tokens: rolc_mname2mon[tokens[0]]
    ),
    "pat:ro:months_short": one_of(RO_MONTHS_SHORT).set_parse_action(
        lambda tokens: roshort_mname2mon[tokens[0]]
    ),
    "pat:ro:months_short_lc": one_of(RO_MONTHS_SHORT_LC).set_parse_action(
        lambda tokens: roshortlc_mname2mon[tokens[0]]
    ),
}


def _day_month_year(month_pattern):
    return (
        Word(nums, min=1, max=2).set_results_name("day")
        + month_pattern.set_results_name("month")
        + Word(nums, exact=4).set_results_name("year")
    )


PATTERNS_RO = [
    {
        "key": "dt:date:ro_base",
        "name": "Romanian date with title-case month name",
        "pattern": _day_month_year(BASE_PATTERNS_RO["pat:ro:months"]),
        "length": {"min": 10, "max": 18},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:ro_base_lc",
        "name": "Romanian date with lowercase month name",
        "pattern": _day_month_year(BASE_PATTERNS_RO["pat:ro:months_lc"]),
        "length": {"min": 10, "max": 18},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:ro_short",
        "name": "Romanian date with abbreviated title-case month",
        "pattern": _day_month_year(BASE_PATTERNS_RO["pat:ro:months_short"]),
        "length": {"min": 10, "max": 13},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:ro_short_lc",
        "name": "Romanian date with abbreviated lowercase month",
        "pattern": _day_month_year(BASE_PATTERNS_RO["pat:ro:months_short_lc"]),
        "length": {"min": 10, "max": 13},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
