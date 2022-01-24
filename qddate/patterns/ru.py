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
from .base import BASE_DATE_PATTERNS

RUS_MONTHS_ORIG = [
    u"Январь",
    u"Февраль",
    u"Март",
    u"Апрель",
    u"Май",
    u"Июнь",
    u"Июль",
    u"Август",
    u"Сентябрь",
    u"Октябрь",
    u"Ноябрь",
    u"Декабрь",
]
RUS_MONTHS_ORIG_LC = [
    u"январь",
    u"февраль",
    u"март",
    u"апрель",
    u"май",
    u"июнь",
    u"июль",
    u"август",
    u"сентябрь",
    u"октябрь",
    u"ноябрь",
    u"декабрь",
]
RUS_MONTHS = [
    u"Января",
    u"Февраля",
    u"Марта",
    u"Апреля",
    u"Мая",
    u"Июня",
    u"Июля",
    u"Августа",
    u"Сентября",
    u"Октября",
    u"Ноября",
    u"Декабря",
]
RUS_MONTHS_LC = [
    u"января",
    u"февраля",
    u"марта",
    u"апреля",
    u"мая",
    u"июня",
    u"июля",
    u"августа",
    u"сентября",
    u"октября",
    u"ноября",
    u"декабря",
]
RUS_WEEKDAYS = [
    u"Понедельник",
    u"Вторник",
    u"Среда",
    u"Четверг",
    u"Пятница",
    u"Суббота",
    u"Воскресение",
]
RUS_WEEKDAYS_LC = [
    u"понедельник",
    u"вторник",
    u"среда",
    u"четверг",
    u"пятница",
    u"суббота",
    u"воскресение",
]
RUS_YEARS = [u"г.", u"года"]


# Russian months map
ru_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS) if m)
rulc_mname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_LC) if m)
ru_origmname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG) if m)
rulc_origmname2mon = dict((m, i + 1) for i, m in enumerate(RUS_MONTHS_ORIG_LC) if m)

BASE_PATTERNS_RU = {
    "pat:rus:years": oneOf(RUS_YEARS),
    "pat:rus:weekdays": oneOf(RUS_WEEKDAYS),
    "pat:rus:weekdays_lc": oneOf(RUS_WEEKDAYS_LC),
    #  months names
    "pat:rus:months": oneOf(RUS_MONTHS).setParseAction(lambda t: ru_mname2mon[t[0]]),
    "pat:rus:months:lc": oneOf(RUS_MONTHS_LC).setParseAction(
        lambda t: rulc_mname2mon[t[0]]
    ),
    # Original months names, very rarely in use
    "pat:rus:monthsorig": oneOf(RUS_MONTHS_ORIG).setParseAction(
        lambda t: ru_origmname2mon[t[0]]
    ),
    "pat:rus:monthsorig:lc": oneOf(RUS_MONTHS_ORIG_LC).setParseAction(
        lambda t: rulc_origmname2mon[t[0]]
    ),
}

PATTERNS_RU = [
    # Russian patterns
    {
        "key": "dt:date:date_rus",
        "name": "Date with russian month",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 20},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:date_rus2",
        "name": "Date with russian month and year word",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year")
        + Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {"min": 13, "max": 20},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:date_rus3",
        "name": "Date with russian year",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yyyy"]
        + BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {"min": 14, "max": 20},
        "format": "%d.%m.%Y",
    },
    {
        "key": "dt:date:date_rus_lc1",
        "name": "Date with russian month",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:date_rus_lc2",
        "name": "Date with russian month with year word",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year")
        + Optional(BASE_PATTERNS_RU["pat:rus:years"]).suppress(),
        "length": {"min": 13, "max": 25},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_rus",
        "name": "Date with russian month and weekday",
        "pattern": BASE_PATTERNS_RU["pat:rus:weekdays"]
        + Optional(",")
        + Word(nums, min=1, max=2)
        + BASE_PATTERNS_RU["pat:rus:months"]
        + Optional(Literal(",")).suppress()
        + Word(nums, exact=4).setResultsName("year")
        + BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {"min": 13, "max": 20},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_rus_lc1",
        "name": "Date with russian month and weekday",
        "pattern": BASE_PATTERNS_RU["pat:rus:weekdays"]
        + Optional(",")
        + Word(nums, min=1, max=2)
        + BASE_PATTERNS_RU["pat:rus:months:lc"]
        + Optional(Literal(",")).suppress()
        + Word(nums, exact=4).setResultsName("year")
        + BASE_PATTERNS_RU["pat:rus:years"].suppress(),
        "length": {"min": 13, "max": 25},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:rus_rare_2",
        "name": "Date with russian month with dots as divider",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_RU["pat:rus:months"].setResultsName("month")
        + Optional(".").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 20},
        "format": "%d.%m.%Y",
        "filter": 1,
    },
    {
        "key": "dt:date:rus_rare_3",
        "name": "Date with russian month with dots as divider with low case months",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Literal(".").suppress()
        + BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month")
        + Literal(".").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 11, "max": 20},
        "format": "%d.%m.%Y",
        "filter": 1,
    },
    # KHMB Bank http://www.kbhmb.ru/news/
    {
        "key": "dt:date:rus_rare_5",
        "name": "Russian date stars with month name",
        "pattern": BASE_PATTERNS_RU["pat:rus:monthsorig"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 13, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
    # Bank Rus format http://www.bankrus.ru/about/info/g1/news
    {
        "key": "dt:date:rus_rare_6",
        "name": "Russian date stars with weekday and follows with month name",
        "pattern": BASE_PATTERNS_RU["pat:rus:weekdays_lc"].suppress()
        + Literal(",").suppress()
        + BASE_PATTERNS_RU["pat:rus:months:lc"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Literal(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 13, "max": 22},
        "format": "%d %m %Y",
        "filter": 1,
    },
]
