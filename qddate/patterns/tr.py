# -*- coding: utf-8 -*-
from pyparsing import Word, nums, oneOf, Optional

TR_MONTHS = [
    "Ocak",
    "Şubat",
    "Mart",
    "Nisan",
    "Mayıs",
    "Haziran",
    "Temmuz",
    "Ağustos",
    "Eylül",
    "Ekim",
    "Kasım",
    "Aralık",
]

TR_MONTHS_LC = [
    "ocak",
    "şubat",
    "mart",
    "nisan",
    "mayıs",
    "haziran",
    "temmuz",
    "ağustos",
    "eylül",
    "ekim",
    "kasım",
    "aralık",
]

tr_mname2mon = dict((m, i + 1) for i, m in enumerate(TR_MONTHS) if m)
trlc_mname2mon = dict((m, i + 1) for i, m in enumerate(TR_MONTHS_LC) if m)

BASE_PATTERNS_TR = {
    "pat:tr:months":
    oneOf(TR_MONTHS).setParseAction(lambda t: tr_mname2mon[t[0]]),
    "pat:tr:months_lc":
    oneOf(TR_MONTHS_LC).setParseAction(lambda t: trlc_mname2mon[t[0]]),
}

TURKISH_SUFFIX = Optional(
    oneOf(["tarihinde", "tarihli"], caseless=True)).suppress()

PATTERNS_TR = [
    {
        "key":
        "dt:date:tr_base",
        "name":
        "Base Turkish date with capitalized month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_TR["pat:tr:months"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") + TURKISH_SUFFIX,
        "length": {
            "min": 11,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
    {
        "key":
        "dt:date:tr_base_lc",
        "name":
        "Base Turkish date with lowercase month",
        "pattern":
        Word(nums, min=1, max=2).setResultsName("day") +
        BASE_PATTERNS_TR["pat:tr:months_lc"].setResultsName("month") +
        Word(nums, exact=4).setResultsName("year") + TURKISH_SUFFIX,
        "length": {
            "min": 11,
            "max": 32
        },
        "format":
        "%d %m %Y",
        "filter":
        1,
    },
]

