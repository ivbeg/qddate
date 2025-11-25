# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    Optional,
    Literal,
)

from .base import BASE_DATE_PATTERNS

RUS_MONTHS_ORIG = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
]
RUS_MONTHS_ORIG_LC = [
    "январь",
    "февраль",
    "март",
    "апрель",
    "май",
    "июнь",
    "июль",
    "август",
    "сентябрь",
    "октябрь",
    "ноябрь",
    "декабрь",
]
RUS_MONTHS = [
    "Января",
    "Февраля",
    "Марта",
    "Апреля",
    "Мая",
    "Июня",
    "Июля",
    "Августа",
    "Сентября",
    "Октября",
    "Ноября",
    "Декабря",
]
RUS_MONTHS_LC = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]
RUS_WEEKDAYS = [
    "Понедельник",
    "Вторник",
    "Среда",
    "Четверг",
    "Пятница",
    "Суббота",
    "Воскресение",
]
RUS_WEEKDAYS_LC = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресение",
]
RUS_YEARS = ["г.", "года"]

# Russian months map
ru_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS) if m)
rulc_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_LC) if m)
ru_origmname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG) if m)
rulc_origmname2mon = dict(
    (m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG_LC) if m)

BASE_PATTERNS_RU = {
    "pat:rus:years":
    oneOf(RUS_YEARS),
    "pat:rus:weekdays":
    oneOf(RUS_WEEKDAYS),
    "pat:rus:weekdays_lc":
    oneOf(RUS_WEEKDAYS_LC),
    #  months names
    "pat:rus:months":
    oneOf(RUS_MONTHS).setParseAction(lambda t: ru_mname2mon[t[0]]),
    "pat:rus:months:lc":
    oneOf(RUS_MONTHS_LC).setParseAction(lambda t: rulc_mname2mon[t[0]]),
    # Original months names, very rarely in use
    "pat:rus:monthsorig":
    oneOf(RUS_MONTHS_ORIG).setParseAction(lambda t: ru_origmname2mon[t[0]]),
    "pat:rus:monthsorig:lc":
    oneOf(RUS_MONTHS_ORIG_LC).setParseAction(
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month") +
        Optional(",").suppress() + Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 11,
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month") +
        Optional(",").suppress() + Word(nums, exact=4).setResultsName("year") +
        Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {
            "min": 13,
            "max": 20
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
            "min": 14,
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month") +
        Optional(",").suppress() + Word(nums, exact=4).setResultsName("year"),
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(",").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") +
        Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {
            "min": 13,
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
        Word(nums, min=1, max=2) + BASE_PATTERNS_RU["pat:rus:months"] +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {
            "min": 13,
            "max": 20
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
        Word(nums, min=1, max=2) + BASE_PATTERNS_RU["pat:rus:months:lc"] +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).setResultsName("year") +
        BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {
            "min": 13,
            "max": 25
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month") +
        Optional(".").suppress() + Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 11,
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
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(".").suppress() +
        BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month") +
        Literal(".").suppress() + Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 11,
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
        BASE_PATTERNS_RU["pat:rus:monthsorig"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() + Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 13,
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
        BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month") +
        Word(nums, min=1, max=2).setResultsName("day") +
        Literal(",").suppress() + Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 13,
            "max": 22
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]
