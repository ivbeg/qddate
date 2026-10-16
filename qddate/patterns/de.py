# -*- coding: utf-8 -*-
"""German month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. The legacy ``DE_MONTHS`` / ``DE_MONTHS_LC`` /
``DE_MONTHS_SHORT`` / ``DE_MONTHS_SHORT_LC`` attributes are re-exported for
backward compatibility with downstream tests and consumers.
"""

from pyparsing import (
    Literal,
    Optional,
    Word,
    nums,
    one_of,
)

from .months import MONTHS_BY_LANGUAGE

_DE = MONTHS_BY_LANGUAGE["de"]

# Back-compat re-exports: every downstream consumer / test reads these names.
DE_MONTHS = list(_DE.full)
DE_MONTHS_LC = list(_DE.full_lc)
DE_MONTHS_SHORT = list(_DE.abbrev)
DE_MONTHS_SHORT_LC = list(_DE.abbrev_lc)

DE_WEEKDAYS = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
]
DE_WEEKDAYS_LC = [
    "montag",
    "dienstag",
    "mittwoch",
    "donnerstag",
    "freitag",
    "samstag",
    "sonntag",
]

# German months map (derived from the same table).
de_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS) if m)
delc_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_LC) if m)
deshort_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_SHORT) if m)
deshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(DE_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_DE = {
    "pat:de:months":
    one_of(DE_MONTHS).set_parse_action(lambda t: de_mname2mon[t[0]]),
    "pat:de:months_lc":
    one_of(DE_MONTHS_LC).set_parse_action(lambda t: delc_mname2mon[t[0]]),
    "pat:de:months_short":
    one_of(DE_MONTHS_SHORT).set_parse_action(lambda t: deshort_mname2mon[t[0]]),
    "pat:de:months_short_lc":
    one_of(DE_MONTHS_SHORT_LC).set_parse_action(lambda t: deshortlc_mname2mon[t[0]]),
    "pat:de:weekdays":
    one_of(DE_WEEKDAYS),
    "pat:de:weekdays_lc":
    one_of(DE_WEEKDAYS_LC),
}

PATTERNS_DE = [
    # German patterns
    {
        "key":
        "dt:date:de_base",
        "name":
        "Base german date with month name",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_DE["pat:de:months"].set_results_name("month") +
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
        "dt:date:de_base_lc",
        "name":
        "Base german date with month name and lowcase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_DE["pat:de:months_lc"].set_results_name("month") +
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
    # Weekday patterns
    {
        "key":
        "dt:date:de_weekday",
        "name":
        "German date with weekday",
        "pattern":
        BASE_PATTERNS_DE["pat:de:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 15,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:de_weekday_lc",
        "name":
        "German date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_DE["pat:de:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 15,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Abbreviated month patterns
    {
        "key":
        "dt:date:de_short",
        "name":
        "German date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_short"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 18
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:de_short_lc",
        "name":
        "German date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(Literal(".")).suppress() +
        BASE_PATTERNS_DE["pat:de:months_short_lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 18
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Rare patterns (month-first)
    {
        "key":
        "dt:date:de_rare_1",
        "name":
        "German date month-first format",
        "pattern":
        BASE_PATTERNS_DE["pat:de:months"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:de_rare_2",
        "name":
        "German date month-first lowercase",
        "pattern":
        BASE_PATTERNS_DE["pat:de:months_lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
]
