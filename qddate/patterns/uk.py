# -*- coding: utf-8 -*-
"""Ukrainian month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``UK_MONTHS*`` constants are re-exported;
``uk_mname2mon`` is the unified lookup across nominative, genitive, and
short variants.
"""

from pyparsing import Word, nums, one_of

from .months import MONTHS_BY_LANGUAGE

_UK = MONTHS_BY_LANGUAGE["uk"]

# Ukrainian month names occur in both nominative (standalone) and genitive
# (date) forms.  Keep both forms because news and publication metadata use
# either convention.
UK_MONTHS = list(_UK.full)
UK_MONTHS_LC = list(_UK.full_lc)
UK_MONTHS_GEN = list(_UK.genitive or ())
UK_MONTHS_GEN_LC = list(_UK.genitive_lc or ())
UK_MONTHS_SHORT = list(_UK.short or _UK.abbrev)
UK_MONTHS_SHORT_LC = list(_UK.short_lc or _UK.abbrev_lc)

uk_mname2mon = {}
for idx in range(12):
    for names in (UK_MONTHS, UK_MONTHS_LC, UK_MONTHS_GEN, UK_MONTHS_GEN_LC,
                  UK_MONTHS_SHORT, UK_MONTHS_SHORT_LC):
        if idx < len(names) and names[idx]:
            uk_mname2mon[names[idx]] = idx + 1

BASE_PATTERNS_UK = {
    "pat:uk:months": one_of(UK_MONTHS).set_parse_action(lambda t: uk_mname2mon[t[0]]),
    "pat:uk:months_lc": one_of(UK_MONTHS_LC).set_parse_action(
        lambda t: uk_mname2mon[t[0]]),
    "pat:uk:months_gen": one_of(UK_MONTHS_GEN).set_parse_action(lambda t: uk_mname2mon[t[0]]),
    "pat:uk:months_gen_lc": one_of(UK_MONTHS_GEN_LC).set_parse_action(lambda t: uk_mname2mon[t[0]]),
    "pat:uk:months_short": one_of(UK_MONTHS_SHORT).set_parse_action(lambda t: uk_mname2mon[t[0]]),
    "pat:uk:months_short_lc": one_of(UK_MONTHS_SHORT_LC).set_parse_action(
        lambda t: uk_mname2mon[t[0]]),
}


def _date_pattern(month_key):
    return (Word(nums, min=1, max=2).set_results_name("day") +
            BASE_PATTERNS_UK[month_key].set_results_name("month") +
            Word(nums, exact=4).set_results_name("year"))


PATTERNS_UK = [
    {"key": "dt:date:uk_base", "name": "Base Ukrainian date with month name",
     "pattern": _date_pattern("pat:uk:months"), "length": {"min": 11, "max": 22},
     "format": "%d %m %Y", "filter": 1},
    {"key": "dt:date:uk_base_lc", "name": "Base Ukrainian date with lowercase month name",
     "pattern": _date_pattern("pat:uk:months_lc"), "length": {"min": 11, "max": 22},
     "format": "%d %m %Y", "filter": 1},
    {"key": "dt:date:uk_gen", "name": "Ukrainian date with month name in genitive form",
     "pattern": _date_pattern("pat:uk:months_gen"), "length": {"min": 11, "max": 22},
     "format": "%d %m %Y", "filter": 1},
    {"key": "dt:date:uk_gen_lc", "name": "Ukrainian date with lowercase genitive month name",
     "pattern": _date_pattern("pat:uk:months_gen_lc"), "length": {"min": 11, "max": 22},
     "format": "%d %m %Y", "filter": 1},
    {"key": "dt:date:uk_short", "name": "Ukrainian date with abbreviated month name",
     "pattern": _date_pattern("pat:uk:months_short"), "length": {"min": 10, "max": 15},
     "format": "%d %m %Y", "filter": 1},
    {"key": "dt:date:uk_short_lc", "name": "Ukrainian date with lowercase abbreviated month name",
     "pattern": _date_pattern("pat:uk:months_short_lc"), "length": {"min": 10, "max": 15},
     "format": "%d %m %Y", "filter": 1},
]
