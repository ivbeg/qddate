# -*- coding: utf-8 -*-
"""Russian month-name date patterns.

Month-name data is sourced from the canonical ``MONTHS_BY_LANGUAGE`` table in
``qddate/patterns/months``. Legacy ``RUS_MONTHS*`` constants are re-exported;
``RUS_MONTHS_ORIG*`` carry the nominative form and ``RUS_MONTHS*`` carry the
genitive form used after a numeric day.
"""

from pyparsing import (
    Literal,
    Optional,
    Word,
    nums,
    one_of,
)

from .base import BASE_DATE_PATTERNS
from .months import MONTHS_BY_LANGUAGE

_RU = MONTHS_BY_LANGUAGE["ru"]

# Nominative ("Январь") = the table's ``full`` variant.
RUS_MONTHS_ORIG = list(_RU.full)
RUS_MONTHS_ORIG_LC = list(_RU.full_lc)
# Genitive ("Января") = the table's ``genitive`` variant.
RUS_MONTHS = list(_RU.genitive or ())
RUS_MONTHS_LC = list(_RU.genitive_lc or ())

RUS_WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресенье",
    # Misspelling the pattern used to require; kept so such inputs still match.
    "Воскресение",
]
RUS_WEEKDAYS_LC = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
    "воскресение",
]
RUS_YEARS = ["г.", "года"]
# Word written between a date and its time of day ("4 Сентября 2020 в 04:06").
# DateParser accepts it before the time in the generated time variants.
RUS_TIME_PREFIXES = ["в"]

ru_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS) if m)
rulc_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_LC) if m)
ru_origmname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG) if m)
rulc_origmname2mon = dict(
    (m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG_LC) if m)

BASE_PATTERNS_RU = {
    "pat:rus:years":
    one_of(RUS_YEARS),
    "pat:rus:weekdays":
    one_of(RUS_WEEKDAYS),
    "pat:rus:weekdays_lc":
    one_of(RUS_WEEKDAYS_LC),
    #  months names
    "pat:rus:months":
    one_of(RUS_MONTHS).set_parse_action(lambda t: ru_mname2mon[t[0]]),
    "pat:rus:months:lc":
    one_of(RUS_MONTHS_LC).set_parse_action(lambda t: rulc_mname2mon[t[0]]),
    # Original months names, very rarely in use
    "pat:rus:monthsorig":
    one_of(RUS_MONTHS_ORIG).set_parse_action(lambda t: ru_origmname2mon[t[0]]),
    "pat:rus:monthsorig:lc":
    one_of(RUS_MONTHS_ORIG_LC).set_parse_action(
        lambda t: rulc_origmname2mon[t[0]]),
}

PATTERNS_RU = [
    # Russian patterns
    {
        "key":
        "dt:date:date_rus",
        "name":
        "Date with russian month",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].set_results_name("month") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_rus2",
        "name":
        "Date with russian month and year word",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].set_results_name("month") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year") +
        Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {
            "min": 10,
            "max": 23
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_rus3",
        "name":
        "Date with russian year",
        "pattern":
        BASE_DATE_PATTERNS["pat:date:d.m.yyyy"] +
        BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {
            "min": 11,
            "max": 20
        },
        "format":
        "%d.%m.%Y",
    },
    {
        "key":
        "dt:date:date_rus_lc1",
        "name":
        "Date with russian month",
        "pattern":
        (Word(nums, min=1, max=2).set_results_name("day") +
         Optional(",").suppress() +
         BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
         Optional(",").suppress() + Word(nums, exact=4).set_results_name("year")) |
        (Word(nums, min=1, max=2).set_results_name("day") +
         Literal("/").suppress() +
         BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
         Literal("/").suppress() + Word(nums, exact=4).set_results_name("year")),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_rus_lc2",
        "name":
        "Date with russian month with year word",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year") +
        Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {
            "min": 10,
            "max": 25
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_rus",
        "name":
        "Date with russian month and weekday",
        "pattern":
        BASE_PATTERNS_RU["pat:rus:weekdays"] + Optional(",") +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_RU["pat:rus:months"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year") +
        BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {
            "min": 13,
            "max": 35
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_rus_lc1",
        "name":
        "Date with russian month and weekday",
        "pattern":
        BASE_PATTERNS_RU["pat:rus:weekdays"] + Optional(",") +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year") +
        BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {
            "min": 13,
            "max": 35
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:rus_rare_2",
        "name":
        "Date with russian month with dots as divider",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].set_results_name("month") +
        Optional(".").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d.%m.%Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:rus_rare_3",
        "name":
        "Date with russian month with dots as divider with low case months",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(".").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
        Literal(".").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d.%m.%Y",
        "filter":
        1,
    },
    # KHMB Bank http://www.kbhmb.ru/news/
    {
        "key":
        "dt:date:rus_rare_5",
        "name":
        "Russian date stars with month name",
        "pattern":
        BASE_PATTERNS_RU["pat:rus:monthsorig"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 22
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Bank Rus format http://www.bankrus.ru/about/info/g1/news
    {
        "key":
        "dt:date:rus_rare_6",
        "name":
        "Russian date stars with weekday and follows with month name",
        "pattern":
        BASE_PATTERNS_RU["pat:rus:weekdays_lc"].suppress() +
        Literal(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 13,
            "max": 30
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_rus_noyear",
        "name":
        "Date with russian month without year",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() +
        (BASE_PATTERNS_RU["pat:rus:months"] |
         BASE_PATTERNS_RU["pat:rus:months:lc"]).set_results_name("month"),
        "length": {
            "min": 5,
            "max": 12
        },
        "format":
        "%d %m",
        "noyear":
        True,
        "filter":
        1,
    },
]
