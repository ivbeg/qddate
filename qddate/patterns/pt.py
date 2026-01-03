# -*- coding: utf-8 -*-
from pyparsing import (
    Word,
    nums,
    oneOf,
    CaselessLiteral,
    Optional,
    Literal,
)

PT_MONTHS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
PT_MONTHS_LC = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]

PT_MONTHS_SHORT = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]
PT_MONTHS_SHORT_LC = [
    "jan",
    "fev",
    "mar",
    "abr",
    "mai",
    "jun",
    "jul",
    "ago",
    "set",
    "out",
    "nov",
    "dez",
]

PT_WEEKDAYS = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]
PT_WEEKDAYS_LC = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]
PT_WEEKDAYS_SHORT = [
    "Seg",
    "Ter",
    "Qua",
    "Qui",
    "Sex",
    "Sáb",
    "Dom",
]
PT_WEEKDAYS_SHORT_LC = [
    "seg",
    "ter",
    "qua",
    "qui",
    "sex",
    "sáb",
    "dom",
]

# Portugal months map
pt_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS) if m)
ptlc_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS_LC) if m)
ptshort_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS_SHORT) if m)
ptshortlc_mname2mon = dict((m, i + 1) for i, m in enumerate(PT_MONTHS_SHORT_LC) if m)

BASE_PATTERNS_PT = {
    "pat:pt:months":
    oneOf(PT_MONTHS).setParseAction(lambda t: pt_mname2mon[t[0]]),
    "pat:pt:months_lc":
    oneOf(PT_MONTHS_LC).setParseAction(lambda t: ptlc_mname2mon[t[0]]),
    "pat:pt:months_short":
    oneOf(PT_MONTHS_SHORT, caseless=True).setParseAction(lambda t: ptshort_mname2mon[t[0].capitalize()]),
    "pat:pt:months_short_lc":
    oneOf(PT_MONTHS_SHORT_LC).setParseAction(lambda t: ptshortlc_mname2mon[t[0]]),
    "pat:pt:weekdays":
    oneOf(PT_WEEKDAYS),
    "pat:pt:weekdays_lc":
    oneOf(PT_WEEKDAYS_LC),
    "pat:pt:weekdays_short":
    oneOf(PT_WEEKDAYS_SHORT, caseless=True),
    "pat:pt:weekdays_short_lc":
    oneOf(PT_WEEKDAYS_SHORT_LC),
}

PATTERNS_PT = [
    # Portugal patterns
    {
        "key":
        "dt:date:pt_base",
        "name":
        "Base portugal date with month name not article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month") +
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
        "dt:date:pt_base_lc",
        "name":
        "Base portugal date with month name and lowcase, no article",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month") +
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
        "dt:date:pt_base_article",
        "name":
        "Base portugal date with month name and articles",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 11,
            "max": 26
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pt_base_lc_article",
        "name":
        "Base portugal date with month name and articles and lowcase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        CaselessLiteral("de").suppress() +
        BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month") +
        CaselessLiteral("de").suppress() +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 11,
            "max": 26
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # Abbreviated month patterns
    {
        "key":
        "dt:date:pt_short",
        "name":
        "Portuguese date with abbreviated month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months_short"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 9,
            "max": 13
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pt_short_lc",
        "name":
        "Portuguese date with abbreviated month lowercase",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months_short_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 9,
            "max": 13
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pt_short_monthfirst",
        "name":
        "Portuguese date with abbreviated month (month first)",
        "pattern":
        (BASE_PATTERNS_PT["pat:pt:months_short"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")) |
        (BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month") +
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
        "dt:date:pt_short_lc_monthfirst",
        "name":
        "Portuguese date with abbreviated month lowercase (month first)",
        "pattern":
        (BASE_PATTERNS_PT["pat:pt:months_short_lc"].setResultsName("month") +
         Word(nums, min=1, max=2).setResultsName("day") +
         Literal(",").suppress() +
         Word(nums, exact=4).setResultsName("year")) |
        (BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month") +
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
        "dt:date:pt_weekday",
        "name":
        "Portuguese date with weekday",
        "pattern":
        BASE_PATTERNS_PT["pat:pt:weekdays"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 20,
            "max": 40
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pt_weekday_lc",
        "name":
        "Portuguese date with weekday lowercase",
        "pattern":
        BASE_PATTERNS_PT["pat:pt:weekdays_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 20,
            "max": 40
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:pt_weekday_short",
        "name":
        "Portuguese date with short weekday",
        "pattern":
        BASE_PATTERNS_PT["pat:pt:weekdays_short"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
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
        "dt:date:pt_weekday_short_lc",
        "name":
        "Portuguese date with short weekday lowercase",
        "pattern":
        BASE_PATTERNS_PT["pat:pt:weekdays_short_lc"].suppress() +
        Optional(Literal(",")).suppress() +
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_PT["pat:pt:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year"),
        "length": {
            "min": 13,
            "max": 20
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]
