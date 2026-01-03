# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    CaselessLiteral,
    Optional,
    Literal,
)

FR_MONTHS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]
FR_MONTHS_LC = [
    "janvier",
    "février",
    "mars",
    "avril",
    "mai",
    "juin",
    "juillet",
    "août",
    "septembre",
    "octobre",
    "novembre",
    "décembre",
]

FR_MONTHS_SHORT = [
    "Janv",
    "Févr",
    "Mars",
    "Avr",
    "Mai",
    "Juin",
    "Juil",
    "Août",
    "Sept",
    "Oct",
    "Nov",
    "Déc",
]
FR_MONTHS_SHORT_LC = [
    "janv",
    "févr",
    "mars",
    "avr",
    "mai",
    "juin",
    "juil",
    "août",
    "sept",
    "oct",
    "nov",
    "déc",
]

FR_WEEKDAYS = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
FR_WEEKDAYS_LC = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

# French months map
fr_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS) if m)
frlc_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_LC) if m)
frshort_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_SHORT) if m)
frshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(FR_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_FR = {
    "pat:fr:months":
    oneOf(FR_MONTHS).setParseAction(lambda t: fr_mname2mon[t[0]]),
    "pat:fr:months_lc":
    oneOf(FR_MONTHS_LC).setParseAction(lambda t: frlc_mname2mon[t[0]]),
    "pat:fr:months_short":
    oneOf(FR_MONTHS_SHORT, caseless=True).setParseAction(lambda t: frshort_mname2mon[t[0].capitalize()]),
    "pat:fr:months_short_lc":
    oneOf(FR_MONTHS_SHORT_LC).setParseAction(lambda t: frshortlc_mname2mon[t[0]]),
    "pat:fr:weekdays":
    oneOf(FR_WEEKDAYS),
    "pat:fr:weekdays_lc":
    oneOf(FR_WEEKDAYS_LC),
}

PATTERNS_FR = [
    # French patterns
    {
        "key":
        "dt:date:fr_base",
        "name":
        "Base french date with month name not archive",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month") +
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
        "dt:date:fr_base_lc",
        "name":
        "Base french date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month") +
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
        "dt:date:fr_base_article",
        "name":
        "Base french date with month name and articles",
        "pattern":
        CaselessLiteral("Le").suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month") +
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
        "dt:date:fr_base_lc_article",
        "name":
        "Base french date with month name and articles and lowcase",
        "pattern":
        CaselessLiteral("le").suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month") +
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
    # Abbreviated month patterns
    {
        "key":
        "dt:date:fr_short",
        "name":
        "French date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months_short"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_lc",
        "name":
        "French date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months_short_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_monthfirst",
        "name":
        "French date with abbreviated month (month first)",
        "pattern":
        (BASE_PATTERNS_FR["pat:fr:months_short"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")) |
        (BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")),
        "length": {
            "min": 9,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:fr_short_lc_monthfirst",
        "name":
        "French date with abbreviated month lowercase (month first)",
        "pattern":
        (BASE_PATTERNS_FR["pat:fr:months_short_lc"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")) |
        (BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")),
        "length": {
            "min": 9,
            "max": 25
        },
        "format":
        "%m %d %Y",
        "filter":
        1,
    },
    # Weekday patterns
    {
        "key":
        "dt:date:fr_weekday",
        "name":
        "French date with weekday",
        "pattern":
        BASE_PATTERNS_FR["pat:fr:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        "dt:date:fr_weekday_lc",
        "name":
        "French date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_FR["pat:fr:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_FR["pat:fr:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 15,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]
