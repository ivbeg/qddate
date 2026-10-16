# -*- coding: utf-8 -*-
"""Bulgarian month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months`` (pure Cyrillic forms). The legacy module also
shipped a handful of mixed-script spellings (e.g. ``Янyapи`` with Latin
``y``/``a``/``p``/``и``) that real datasets still contain; they are appended as
supplementary parser entries below and remain reachable through
``bg_mname2mon`` / ``bglc_mname2mon``. The canonical table does not need them:
it already exposes the canonical Cyrillic equivalents that the parity test
maps them onto.
"""

from pyparsing import (
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_BG = MONTHS_BY_LANGUAGE["bg"]

# Canonical Cyrillic forms, sourced from MONTHS_BY_LANGUAGE.
BG_MONTHS = list(_BG.full)
BG_MONTHS_LC = list(_BG.full_lc)

# Mixed Latin/Cyrillic legacy spellings (preserved for backward compatibility;
# the canonical Cyrillic form covers the same logical month).
BG_MONTHS_LEGACY = [
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
BG_MONTHS_LEGACY_LC = [
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

# Combined parsing lists (canonical + legacy mixed-script).
BG_MONTHS_ALL = BG_MONTHS + [m for m in BG_MONTHS_LEGACY if m not in BG_MONTHS]
BG_MONTHS_LC_ALL = BG_MONTHS_LC + [m for m in BG_MONTHS_LEGACY_LC if m not in BG_MONTHS_LC]

bg_mname2mon = dict((m, i + 1) for i, m in enumerate(BG_MONTHS) if m)
bglc_mname2mon = dict((m, i + 1) for i, m in enumerate(BG_MONTHS_LC) if m)
# Add the legacy mixed-script entries (point at the same calendar month).
for legacy_list, canonical_list in (
    (BG_MONTHS_LEGACY, BG_MONTHS),
    (BG_MONTHS_LEGACY_LC, BG_MONTHS_LC),
):
    for i, name in enumerate(legacy_list):
        if name and name not in (bglc_mname2mon if canonical_list is BG_MONTHS_LC else bg_mname2mon):
            month_num = canonical_list[i] and (
                bglc_mname2mon.get(canonical_list[i])
                or (i + 1)
            )
            if canonical_list is BG_MONTHS_LC:
                bglc_mname2mon[name] = month_num or (i + 1)
            else:
                bg_mname2mon[name] = month_num or (i + 1)

BASE_PATTERNS_BG = {
    "pat:bg:months":
    one_of(BG_MONTHS_ALL).set_parse_action(lambda t: bg_mname2mon.get(t[0], 1)),
    "pat:bg:months_lc":
    one_of(BG_MONTHS_LC_ALL).set_parse_action(lambda t: bglc_mname2mon.get(t[0], 1)),
}

PATTERNS_BG = [
    # Bulgarian patterns
    {
        "key":
        "dt:date:bg_base",
        "name":
        "Base bulgarian date with month name",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_BG["pat:bg:months"].set_results_name("month") +
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
        "dt:date:bg_base_lc",
        "name":
        "Base bulgarian date with month name and lowcase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_BG["pat:bg:months_lc"].set_results_name("month") +
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
