# -*- coding: utf-8 -*-                6
from pyparsing import (
    Literal,
    Optional,
    White,
    Word,
    nums,
    one_of,
)

EN_NUMERIC_SUFFIXES = ["nd", "rd", "th", "st"]
PAT_EN_DAY_NUMERIC = (Word(nums, min=1, max=2).set_results_name("day") +
                      one_of(EN_NUMERIC_SUFFIXES).suppress())

BASE_DATE_PATTERNS = {
    "pat:date:d.m":
    Word(nums, exact=2).set_results_name("day") + Literal(".").suppress() +
    Word(nums, exact=2).set_results_name("month"),
    "pat:date:d/m/yyyy":
    (Word(nums, min=1, max=2).set_results_name("day") + Literal("/").suppress() +
     Word(nums, min=1, max=2).set_results_name("month") +
     Literal("/").suppress() + Word(nums, exact=4).set_results_name("year")) |
    (Word(nums, min=1, max=2).set_results_name("day") + White(" ").suppress() +
     Word(nums, min=1, max=2).set_results_name("month") +
     White(" ").suppress() + Word(nums, exact=4).set_results_name("year")),
    "pat:date:m/d/yy":
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("/").suppress() + Word(nums, min=1, max=2).set_results_name("day") +
    Literal("/").suppress() + Word(nums, exact=2).set_results_name("year"),
    "pat:date:d/m/yy":
    (Word(nums, min=1, max=2).set_results_name("day") + Literal("/").suppress() +
     Word(nums, min=1, max=2).set_results_name("month") +
     Literal("/").suppress() + Word(nums, exact=2).set_results_name("year")) |
    (Word(nums, min=1, max=2).set_results_name("day") + White(" ").suppress() +
     Word(nums, min=1, max=2).set_results_name("month") +
     White(" ").suppress() + Word(nums, exact=2).set_results_name("year")),
    "pat:date:d.m.yyyy":
    Word(nums, min=1, max=2).set_results_name("day") + Literal(".").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal(".").suppress() + Word(nums, exact=4).set_results_name("year"),
    "pat:date:yyyy/m/d":
    (Word(nums, exact=4).set_results_name("year") + "/" +
     Word(nums, min=1, max=2).set_results_name("month") + "/" +
     Word(nums, min=1, max=2).set_results_name("day")) |
    (Word(nums, exact=4).set_results_name("year") + White(" ").suppress() +
     Word(nums, min=1, max=2).set_results_name("month") + White(" ").suppress() +
     Word(nums, min=1, max=2).set_results_name("day")),
    "pat:date:d.m.yy":
    Word(nums, min=1, max=2).set_results_name("day") + Literal(".").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal(".").suppress() + Word(nums, exact=2).set_results_name("year"),
    "pat:date:d-m-yy":
    Word(nums, min=1, max=2).set_results_name("day") + Literal("-").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("-").suppress() + Word(nums, exact=2).set_results_name("year"),
    "pat:date:d-m-yyyy":
    Word(nums, min=1, max=2).set_results_name("day") + Literal("-").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("-").suppress() + Word(nums, exact=4).set_results_name("year"),
    "pat:date:yyyy-m-d":
    Word(nums, exact=4).set_results_name("year") + Literal("-").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("-").suppress() + Word(nums, min=1, max=2).set_results_name("day"),
    "pat:date:yyyy.m.d":
    Word(nums, exact=4).set_results_name("year") + Literal(".").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal(".").suppress() + Word(nums, min=1, max=2).set_results_name("day"),
    "pat:date:ddmmyyyy":
    Word(nums, exact=2).set_results_name("day") +
    Word(nums, exact=2).set_results_name("month") +
    Word(nums, exact=4).set_results_name("year"),
    "pat:date:mmyyyy":
    Word(nums, exact=2).set_results_name("month") +
    Word(nums, exact=4).set_results_name("year"),
    "pat:date:yyyymmdd":
    Word(nums, exact=4).set_results_name("year") +
    Word(nums, exact=2).set_results_name("month") +
    Word(nums, exact=2).set_results_name("day"),
    "pat:date:mm/dd/yyyy":
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("/").suppress() + Word(nums, min=1, max=2).set_results_name("day") +
    Literal("/").suppress() + Word(nums, exact=4).set_results_name("year"),
    # Rare patterns
    "pat:date:d/m yy":
    Word(nums, min=1, max=2).set_results_name("day") + Literal("/").suppress() +
    Word(nums, min=1, max=2).set_results_name("month") +
    Literal("‘").suppress() + Word(nums, exact=2).set_results_name("year"),
}

BASE_TIME_PATTERNS = {
    "pat:time:minutes":
    Word(nums, exact=2).set_results_name("hour") + Literal(":").suppress() +
    Word(nums, exact=2).set_results_name("minute"),
    "pat:time:full":
    Word(nums, exact=2).set_results_name("hour") + Literal(":").suppress() +
    Word(nums, exact=2).set_results_name("minute") + Literal(":").suppress() +
    Word(nums, exact=2).set_results_name("second") + Optional(
        Literal("+").suppress() +
        Word(nums, min=3, max=4).set_results_name("timezone")),
}

# English month data is sourced from the canonical `MONTHS_BY_LANGUAGE` table
# (`qddate.patterns.months`). The names are re-exported here as back-compat
# constants so the pyparsing grammar and downstream tests can keep using the
# familiar ``ENG_MONTHS``/``en_mname2mon`` symbols.
from .months import MONTHS_BY_LANGUAGE  # noqa: E402

_EN_DATA = MONTHS_BY_LANGUAGE["en"]
ENG_MONTHS = list(_EN_DATA.full)
ENG_MONTHS_LC = list(_EN_DATA.full_lc)
ENG_MONTHS_ABBREV = list(_EN_DATA.abbrev)
# English always populates ``short_lc`` (the 3-letter lowercase abbreviations).
# The dataclass declares the field as ``Optional`` for languages that don't,
# hence the explicit ``or abbrev_lc`` fall-back to keep mypy happy.
_EN_SHORT_LC = _EN_DATA.short_lc if _EN_DATA.short_lc is not None else _EN_DATA.abbrev_lc
ENG_MONTHS_SHORT = list(_EN_SHORT_LC)
ENG_WEEKDAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
ENG_WEEKDAYS_SHORT = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# English months map (built from the same table)
en_mname2mon = {m: i for i, m in enumerate(_EN_DATA.full, 1)}
enabbrev_mname2mon = {m: i for i, m in enumerate(_EN_DATA.abbrev, 1)}
enlc_mname2mon = {m: i for i, m in enumerate(_EN_DATA.full_lc, 1)}
ensh_mname2mon = {m: i for i, m in enumerate(_EN_SHORT_LC, 1)}
enabbrev_mname2mon = dict((m, i + 1) for i, m in enumerate(ENG_MONTHS_ABBREV) if m)
ensh_wday2weekday = dict(
    (m, i + 1) for i, m in enumerate(ENG_WEEKDAYS_SHORT) if m)

BASE_PATTERNS_EN = {
    "pat:eng:months":
    one_of(ENG_MONTHS, caseless=True).set_parse_action(lambda t: en_mname2mon[t[0].capitalize()]),
    "pat:eng:months:lc":
    one_of(ENG_MONTHS_LC).set_parse_action(lambda t: enlc_mname2mon[t[0]]),
    "pat:eng:months:short":
    one_of(
        ENG_MONTHS_SHORT,
        caseless=True).set_parse_action(lambda t: ensh_mname2mon[t[0].lower()]),
    "pat:eng:months:abbrev":
    one_of(ENG_MONTHS_ABBREV, caseless=True).set_parse_action(lambda t: enabbrev_mname2mon[t[0].capitalize()]),
    "pat:eng:day_postfix":
    PAT_EN_DAY_NUMERIC,
    "pat:eng:weekdays":
    one_of(ENG_WEEKDAYS),
    "pat:eng:weekdays:short":
    one_of(ENG_WEEKDAYS_SHORT, caseless=True).set_parse_action(
        lambda t: ensh_wday2weekday[t[0].lower()]),
}

PATTERNS_EN = [
    # Universal patterns
    {
        "key": "dt:date:date_1",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {
            "min": 8,
            "max": 10
        },
        "format": "%d/%m/%Y",
    },
    {
        "key": "dt:date:date_2",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yyyy"],
        "length": {
            "min": 8,
            "max": 10
        },
        "format": "%d.%m.%Y",
    },
    {
        "key": "dt:date:date_3",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy/m/d"],
        "length": {
            "min": 8,
            "max": 10
        },
        "format": "%Y/%m/%d",
    },
    {
        "key": "dt:date:date_4",
        "name": "Datetime string",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m.yy"],
        "length": {
            "min": 6,
            "max": 8
        },
        "format": "%d.%m.%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_iso8601",
        "name": "ISO 8601 date",
        "pattern": BASE_DATE_PATTERNS["pat:date:d-m-yyyy"],
        "length": {
            "min": 8,
            "max": 10
        },
        "format": "%d-%m-%Y",
    },
    {
        "key": "dt:date:date_iso8601_short",
        "name": "ISO 8601 date shorted",
        "pattern": BASE_DATE_PATTERNS["pat:date:d-m-yy"],
        "length": {
            "min": 6,
            "max": 8
        },
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
        "length": {
            "min": 6,
            "max": 8
        },
        "format": "%d/%m/%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_9",
        "name": "Date as ISO",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy-m-d"],
        "length": {
            "min": 6,
            "max": 10
        },
        "format": "%Y-%m-%d",
    },
    {
        "key": "dt:date:date_10",
        "name": "Date as yyyy.mm.dd",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyy.m.d"],
        "length": {
            "min": 6,
            "max": 10
        },
        "format": "%Y.%m.%d",
    },
    # USA patterns
    {
        "key": "dt:date:date_usa_1",
        "name": "Date with 2-digits year",
        "pattern": BASE_DATE_PATTERNS["pat:date:m/d/yy"],
        "length": {
            "min": 6,
            "max": 8
        },
        "format": "%m/%d/%y",
        "yearshort": True,
    },
    {
        "key": "dt:date:date_usa",
        "name": "USA mm/dd/yyyy string",
        "pattern": BASE_DATE_PATTERNS["pat:date:mm/dd/yyyy"],
        "length": {
            "min": 8,
            "max": 10
        },
        "format": "%m/%d/%Y",
    },
    # English patterns
    {
        "key":
        "dt:date:date_eng1",
        "name":
        "Date with english month and possible dots",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
        Optional(one_of([".", ","])).suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d.%b.%Y",
    },
    {
        "key":
        "dt:date:date_eng1x",
        "name":
        "Date with english month and , ",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d.%b.%Y",
    },
    {
        "key":
        "dt:date:date_eng1_lc",
        "name":
        "Date with english month lowcase",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_EN["pat:eng:months:lc"].set_results_name("month") +
        Optional(".").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%d.%b.%Y",
    },
    {
        "key":
        "dt:date:date_eng1_short",
        "name":
        "Date with english month short",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(".").suppress() +
        BASE_PATTERNS_EN["pat:eng:months:short"].set_results_name("month") +
        Optional(".").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 11
        },
        "format":
        "%d.%b.%Y",
    },
    {
        "key":
        "dt:date:date_eng2",
        "name":
        "Date with english month 2",
        "pattern":
        (BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
         PAT_EN_DAY_NUMERIC +
         Optional(",").suppress() + Word(nums, exact=4).set_results_name("year")) |
        (PAT_EN_DAY_NUMERIC +
         BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
         Word(nums, exact=4).set_results_name("year")),
        "length": {
            "min": 10,
            "max": 22
        },
        "format":
        "%b %d, %Y",
    },
    {
        "key":
        "dt:date:date_eng2_lc",
        "name":
        "Date with english month 2 lowcase",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:months:lc"].set_results_name("month") +
        PAT_EN_DAY_NUMERIC +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 22
        },
        "format":
        "%b %d, %Y",
    },
    {
        "key":
        "dt:date:date_eng2_short",
        "name":
        "Date with english month 2 short",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:months:short"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 10
        },
        "format":
        "%b %d, %Y",
    },
    {
        "key":
        "dt:date:date_eng3",
        "name":
        "Date with english month full lowcase",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:months:lc"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%b %d, %Y",
        "filter":
        2,
    },
    {
        "key":
        "dt:date:date_eng3_nolc",
        "name":
        "Date with english month full",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional(",").suppress() + Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 10,
            "max": 20
        },
        "format":
        "%b %d, %Y",
        "filter":
        2,
    },
    {
        "key":
        "dt:date:date_eng4_short",
        "name":
        "Date with english month short with dash",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        Optional("-").suppress() +
        BASE_PATTERNS_EN["pat:eng:months:short"].set_results_name("month") +
        Optional("-").suppress() + Word(nums, exact=2).set_results_name("year"),
        # Day 1-2 + optional dashes + 3-letter month + 2-digit year = 6..9 chars
        # (was {10, 10}, which no possible match can ever have).
        "length": {
            "min": 6,
            "max": 9
        },
        "format":
        "%d-%b-%y",
        "yearshort":
        True,
    },
    {
        "key": "dt:date:noyear_1",
        "name": "Datetime string without year",
        "pattern": BASE_DATE_PATTERNS["pat:date:d.m"],
        "length": {
            "min": 5,
            "max": 5
        },
        "format": "%d.%m",
        "noyear": True,
    },
    {
        "key": "dt:date:date_4_point",
        "name": "Datetime string",
        "pattern":
        BASE_DATE_PATTERNS["pat:date:d.m.yy"] + Literal(".").suppress(),
        "length": {
            "min": 6,
            "max": 9
        },
        "format": "%d.%m.%y",
        "yearshort": True,
    },
    {
        "key":
        "dt:date:weekday_eng",
        "name":
        "Date with english month and weekday",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays"].suppress() +
        Optional(",").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 17,
            "max": 27
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_lc",
        "name":
        "Date with english month and weekday",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays"].suppress() +
        Optional(",").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:lc"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 17,
            "max": 27
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_wshort",
        "name":
        "Date with english month and weekday",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress() +
        Optional(",").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 16,
            "max": 27
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_mshort_wshort",
        "name":
        "Date with short english month and short weekday",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:short"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 15,
            "max": 15
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_iso",
        "name":
        "Date with english weekday and iso date",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays"].suppress() +
        Optional(",").suppress() + BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {
            "min": 13,
            "max": 25
        },
        "format":
        "%d/%m/%Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_short_eng_iso",
        "name":
        "Date with english short weekday and iso date",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress() +
        Optional(",").suppress() + BASE_DATE_PATTERNS["pat:date:d/m/yyyy"],
        "length": {
            "min": 13,
            "max": 18
        },
        "format":
        "%d/%m/%Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_mixed",
        "name":
        "Date with english full weekday and short month",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays"].suppress() +
        Optional(",").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:short"].set_results_name("month") +
        Optional(Literal(",")).suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 13,
            "max": 27
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    # English abbreviated month patterns
    {
        "key":
        "dt:date:date_eng_abbrev1",
        "name":
        "Date with abbreviated English month (day first)",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 13
        },
        "format":
        "%d %b %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_eng_abbrev2",
        "name":
        "Date with abbreviated English month (month first)",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%b %d, %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_eng_abbrev3",
        "name":
        "Date with abbreviated English month and comma (day first)",
        "pattern":
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 9,
            "max": 15
        },
        "format":
        "%d %b, %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_abbrev1",
        "name":
        "Date with abbreviated English month and short weekday",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 13,
            "max": 17
        },
        "format":
        "%d %b %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_abbrev2",
        "name":
        "Date with abbreviated English month, short weekday, and comma",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays:short"].suppress() +
        Literal(",").suppress() +
        Word(nums, min=1, max=2).set_results_name("day") +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 13,
            "max": 18
        },
        "format":
        "%d %b %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:weekday_eng_abbrev3",
        "name":
        "Date with full english weekday and abbreviated month (month first)",
        "pattern":
        BASE_PATTERNS_EN["pat:eng:weekdays"].suppress() +
        Optional(",").suppress() +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, min=1, max=2).set_results_name("day") +
        Literal(",").suppress() +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 18,
            "max": 32
        },
        "format":
        "%b %d, %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:date_eng_abbrev_postfix",
        "name":
        "Date with abbreviated English month and day with ordinal suffix",
        "pattern":
        PAT_EN_DAY_NUMERIC +
        BASE_PATTERNS_EN["pat:eng:months:abbrev"].set_results_name("month") +
        Word(nums, exact=4).set_results_name("year"),
        "length": {
            "min": 11,
            "max": 16
        },
        "format":
        "%d %b %Y",
        "filter":
        1,
    },
]

INTEGER_LIKE_PATTERNS = [
    {
        "key": "dt:date:date_5",
        "name": "Datetime string as ddmmyyyy",
        "pattern": BASE_DATE_PATTERNS["pat:date:ddmmyyyy"],
        "length": {
            "min": 8,
            "max": 8
        },
        "format": "%d%m%Y",
    },
    {
        "key": "dt:date:date_6",
        "name": "Datetime string as yyyymmdd",
        "pattern": BASE_DATE_PATTERNS["pat:date:yyyymmdd"],
        "length": {
            "min": 8,
            "max": 8
        },
        "format": "%Y%m%d",
    },
]
