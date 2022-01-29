# -*- coding: utf-8 -*-                6
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


EN_NUMERIC_SUFFIXES = ["nd", "rd", "th", "st"]
PAT_EN_DAY_NUMERIC = (
    Word(nums, min=1, max=2).setResultsName("day")
    + oneOf(EN_NUMERIC_SUFFIXES).suppress()
)

BASE_DATE_PATTERNS = {
    "pat:date:d.m": Word(nums, exact=2) + Literal(".").suppress() + Word(nums, exact=2),
    "pat:date:d/m/yyyy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal("/").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("/").suppress()
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:m/d/yy": Word(nums, min=1, max=2).setResultsName("month")
    + Literal("/").suppress()
    + Word(nums, min=1, max=2).setResultsName("day")
    + Literal("/").suppress()
    + Word(nums, exact=2).setResultsName("year"),
    "pat:date:d/m/yy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal("/").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("/").suppress()
    + Word(nums, exact=2).setResultsName("year"),
    "pat:date:d.m.yyyy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal(".").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal(".").suppress()
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:yyyy/m/d": Word(nums, exact=4).setResultsName("year")
    + "/"
    + Word(nums, min=1, max=2).setResultsName("month")
    + "/"
    + Word(nums, min=1, max=2).setResultsName("day"),
    "pat:date:d.m.yy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal(".").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal(".").suppress()
    + Word(nums, exact=2).setResultsName("year"),
    "pat:date:d-m-yy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal("-").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("-").suppress()
    + Word(nums, exact=2).setResultsName("year"),
    "pat:date:d-m-yyyy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal("-").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("-").suppress()
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:yyyy-m-d": Word(nums, exact=4).setResultsName("year")
    + Literal("-").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("-").suppress()
    + Word(nums, min=1, max=2).setResultsName("day"),
    "pat:date:yyyy.m.d": Word(nums, exact=4).setResultsName("year")
    + Literal(".").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal(".").suppress()
    + Word(nums, min=1, max=2).setResultsName("day"),
    "pat:date:ddmmyyyy": Word(nums, exact=2).setResultsName("day")
    + Word(nums, exact=2).setResultsName("month")
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:mmyyyy": Word(nums, exact=2).setResultsName("month")
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:ddmmyyyy": Word(nums, exact=2).setResultsName("day")
    + Word(nums, exact=2).setResultsName("month")
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:mmyyyy": Word(nums, exact=2).setResultsName("month")
    + Word(nums, exact=4).setResultsName("year"),
    "pat:date:yyyymmdd": Word(nums, exact=4).setResultsName("year")
    + Word(nums, exact=2).setResultsName("month")
    + Word(nums, exact=2).setResultsName("day"),
    "pat:date:mm/dd/yyyy": Word(nums, min=1, max=2).setResultsName("month")
    + Literal("/").suppress()
    + Word(nums, min=1, max=2).setResultsName("day")
    + Literal("/").suppress()
    + Word(nums, exact=4).setResultsName("year"),
    # Rare patterns
    "pat:date:d/m yy": Word(nums, min=1, max=2).setResultsName("day")
    + Literal("/").suppress()
    + Word(nums, min=1, max=2).setResultsName("month")
    + Literal("‘").suppress()
    + Word(nums, exact=2).setResultsName("year"),
}

BASE_TIME_PATTERNS = {
    "pat:time:minutes": Word(nums, exact=2).setResultsName("hour")
    + Literal(":").suppress()
    + Word(nums, exact=2).setResultsName("minute"),
    "pat:time:full": Word(nums, exact=2).setResultsName("hour")
    + Literal(":").suppress()
    + Word(nums, exact=2).setResultsName("minute")
    + Literal(":").suppress()
    + Word(nums, exact=2).setResultsName("second") + Optional(Literal('+').suppress() + Word(nums, min=3, max=4).setResultsName('timezone')),
}


ENG_MONTHS = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
ENG_MONTHS_LC = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "jule",
    "august",
    "september",
    "october",
    "november",
    "december",
]
ENG_MONTHS_SHORT = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]
ENG_WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Satuday",
    "Sunday",
]
ENG_WEEKDAYS_SHORT = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


# English months map
en_mname2mon = dict((m, i + 1) for i, m in enumerate(ENG_MONTHS) if m)
ensh_mname2mon = dict((m, i + 1) for i, m in enumerate(ENG_MONTHS_SHORT) if m)
enlc_mname2mon = dict((m, i + 1) for i, m in enumerate(ENG_MONTHS_LC) if m)
ensh_wday2weekday = dict((m, i + 1) for i, m in enumerate(ENG_WEEKDAYS_SHORT) if m)

BASE_PATTERNS_EN = {
    "pat:eng:months": oneOf(ENG_MONTHS).setParseAction(lambda t: en_mname2mon[t[0]]),
    "pat:eng:months:lc": oneOf(ENG_MONTHS_LC).setParseAction(
        lambda t: enlc_mname2mon[t[0]]
    ),
    "pat:eng:months:short": oneOf(ENG_MONTHS_SHORT, caseless=True).setParseAction(
        lambda t: ensh_mname2mon[t[0].lower()]
    ),
    "pat:eng:weekdays": oneOf(ENG_WEEKDAYS),
    "pat:eng:weekdays:short": oneOf(ENG_WEEKDAYS_SHORT, caseless=True).setParseAction(
        lambda t: ensh_wday2weekday[t[0].lower()]
    ),
}


PATTERNS_EN = [
    # Universal patterns
    {
        "key": "dt:date:date_1",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {"min": 8, "max": 10},
        "format": "%d/%m/%Y",
    },
    {
        "key": "dt:date:date_2",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yyyy"],
        "length": {"min": 8, "max": 10},
        "format": "%d.%m.%Y",
    },
    {
        "key": "dt:date:date_3",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy/m/d"],
        "length": {"min": 8, "max": 10},
        "format": "%Y/%m/%d",
    },
    {
        "key": "dt:date:date_4",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yy"],
        "length": {"min": 6, "max": 8},
        "format": "%d.%m.%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_iso8601",
        "name": "ISO 8601 date",
        "pattern": BASE_DATE_PATTERNS["pat:date:d-m-yyyy"],
        "length": {"min": 8, "max": 10},
        "format": "%d-%m-%Y",
    },
    {
        "key": "dt:date:date_iso8601_short",
        "name": "ISO 8601 date shorted",
        "pattern": BASE_DATE_PATTERNS["pat:date:d-m-yy"],
        "length": {"min": 6, "max": 8},
        "format": "%d-%m-%Y",
        "yearshort": True,
    },
# Commented since it's very rare and generates too many false positives
#    {
#        "key": "dt:date:date_7",
#        "name": "Year-month string",
#        "pattern": BASE_DATE_PATTERNS["pat:date:mmyyyy"],
#        "length": {"min": 6, "max": 6},
#        "format": "%m.%Y",
#    },
    {
        "key": "dt:date:date_8",
        "name": "Date with 2-digits year",
        "pattern": BASE_DATE_PATTERNS["pat:date:d/m/yy"],
        "length": {"min": 6, "max": 8},
        "format": "%d/%m/%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_9",
        "name": "Date as ISO",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy-m-d"],
        "length": {"min": 6, "max": 10},
        "format": "%Y-%m-%d",
    },
    {
        "key": "dt:date:date_10",
        "name": "Date as yyyy.mm.dd",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy.m.d"],
        "length": {"min": 6, "max": 10},
        "format": "%Y.%m.%d",
    },
    # USA patterns
    {
        "key": "dt:date:date_usa_1",
        "name": "Date with 2-digits year",
        "pattern": BASE_DATE_PATTERNS["pat:date:m/d/yy"],
        "length": {"min": 6, "max": 8},
        "format": "%m/%d/%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_usa",
        "name": "USA mm/dd/yyyy string",
        "pattern": BASE_DATE_PATTERNS["pat:date:mm/dd/yyyy"],
        "length": {"min": 8, "max": 10},
        "format": "%m/%d/%Y",
    },
    # English patterns
    {
        "key": "dt:date:date_eng1",
        "name": "Date with english month and possible dots",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_EN["pat:eng:months"].setResultsName("month")
        + Optional(".").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%d.%b.%Y",
    },
    {
        "key": "dt:date:date_eng1x",
        "name": "Date with english month and , ",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_EN["pat:eng:months"].setResultsName("month")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%d.%b.%Y",
    },
    {
        "key": "dt:date:date_eng1_lc",
        "name": "Date with english month lowcase",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_EN["pat:eng:months:lc"].setResultsName("month")
        + Optional(".").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%d.%b.%Y",
    },
    {
        "key": "dt:date:date_eng1_short",
        "name": "Date with english month short",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional(".").suppress()
        + BASE_PATTERNS_EN["pat:eng:months:short"].setResultsName("month")
        + Optional(".").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 10},
        "format": "%d.%b.%Y",
    },
    {
        "key": "dt:date:date_eng2",
        "name": "Date with english month 2",
        "pattern": BASE_PATTERNS_EN["pat:eng:months"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%b %d, %Y",
    },
    {
        "key": "dt:date:date_eng2_lc",
        "name": "Date with english month 2 lowcase",
        "pattern": BASE_PATTERNS_EN["pat:eng:months:lc"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%b %d, %Y",
    },
    {
        "key": "dt:date:date_eng2_short",
        "name": "Date with english month 2 short",
        "pattern": BASE_PATTERNS_EN["pat:eng:months:short"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 10},
        "format": "%b %d, %Y",
    },
    {
        "key": "dt:date:date_eng3",
        "name": "Date with english month full",
        "pattern": BASE_PATTERNS_EN["pat:eng:months:lc"].setResultsName("month")
        + Word(nums, min=1, max=2).setResultsName("day")
        + Optional(",").suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 10, "max": 20},
        "format": "%b %d, %Y",
        "filter": 2,
    },
    {
        "key": "dt:date:date_eng4_short",
        "name": "Date with english month short with dash",
        "pattern": Word(nums, min=1, max=2).setResultsName("day")
        + Optional("-").suppress()
        + BASE_PATTERNS_EN["pat:eng:months:short"].setResultsName("month")
        + Optional("-").suppress()
        + Word(nums, exact=2).setResultsName("year"),
        "length": {"min": 10, "max": 10},
        "format": "%d-%b-%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:noyear_1",
        "name": "Datetime string without year",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m"],
        "length": {"min": 5, "max": 5},
        "format": "%d.%m",
        "noyear": True,
    },
    {
        "key": "dt:date:date_4_point",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yy"] + Literal(".").suppress(),
        "length": {"min": 6, "max": 9},
        "format": "%d.%m.%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:weekday_eng",
        "name": "Date with english month and weekday",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays"].suppress()
        + Optional(",").suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_EN["pat:eng:months"].setResultsName("month")
        + Optional(Literal(",")).suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 17, "max": 27},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_eng_lc",
        "name": "Date with english month and weekday",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays"].suppress()
        + Optional(",").suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_EN["pat:eng:months:lc"].setResultsName("month")
        + Optional(Literal(",")).suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 17, "max": 27},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_eng_wshort",
        "name": "Date with english month and weekday",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress()
        + Optional(",").suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_EN["pat:eng:months"].setResultsName("month")
        + Optional(Literal(",")).suppress()
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 16, "max": 27},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_eng_mshort_wshort",
        "name": "Date with short english month and short weekday",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress()
        + Word(nums, min=1, max=2).setResultsName("day")
        + BASE_PATTERNS_EN["pat:eng:months:short"].setResultsName("month")
        + Word(nums, exact=4).setResultsName("year"),
        "length": {"min": 15, "max": 15},
        "format": "%d %m %Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_eng_iso",
        "name": "Date with english weekday and iso date",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays"].suppress()
        + Optional(",").suppress()
        + BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {"min": 13, "max": 25},
        "format": "%d/%m/%Y",
        "filter": 1,
    },
    {
        "key": "dt:date:weekday_short_eng_iso",
        "name": "Date with english short weekday and iso date",
        "pattern": BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress()
        + Optional(",").suppress()
        + BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {"min": 13, "max": 18},
        "format": "%d/%m/%Y",
        "filter": 1,
    },
]

INTEGER_LIKE_PATTERNS = [
    {
        "key": "dt:date:date_5",
        "name": "Datetime string as ddmmyyyy",
        "pattern": BASE_DATE_PATTERNS["pat:date:ddmmyyyy"],
        "length": {"min": 8, "max": 8},
        "format": "%d%m%Y",
    },
    {
        "key": "dt:date:date_6",
        "name": "Datetime string as yyyymmdd",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyymmdd"],
        "length": {"min": 8, "max": 8},
        "format": "%Y%m%d",
    },
]
