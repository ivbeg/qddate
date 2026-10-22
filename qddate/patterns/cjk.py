# -*- coding: utf-8 -*-
"""Chinese, Japanese and Korean numeric dates.

``2022年5月5日`` (Chinese, Japanese) and ``2022년 5월 5일`` (Korean) write the
year, month and day as numbers, each followed by its unit. The patterns
belong to no language, like the other numeric patterns: every ``languages=``
hint tries them, and ``DateMatch.language`` is None.

A weekday may follow the day (``2022年5月5日(木)``, ``2022年5月5日 星期四``,
``2022년 5월 5일 (목)``), then a time written with units (``14時30分``,
``14时30分``, ``14시 30분``) or after a morning or afternoon marker
(``午後2時``, ``下午2:30``, ``오후 2:30``). ``2022年5月5日 14:30`` is read by
the generated time variants, like any date. Full-width digits
(``２０２２年５月５日``) are accepted.
"""

from pyparsing import (
    Literal,
    Optional,
    ParseException,
    Word,
    one_of,
)

# ASCII and full-width digits; ``int()`` reads both.
_DIGITS = "0123456789" + "０１２３４５６７８９"


def _number(name, exact=None):
    """A number of ``exact`` digits, or of one or two, named ``name``."""
    if exact is not None:
        return Word(_DIGITS, exact=exact).set_results_name(name)
    return Word(_DIGITS, min=1, max=2).set_results_name(name)


_ZH_WEEKDAYS = ["星期" + c for c in "一二三四五六日天"] + ["周" + c for c in "一二三四五六日天"]
_JA_WEEKDAYS = [c + suffix for c in "月火水木金土日" for suffix in ("", "曜", "曜日")]
_KO_WEEKDAYS = [c + suffix for c in "월화수목금토일" for suffix in ("", "요일")]
# In brackets ("(木)", "（星期四）", "(목)") or written out ("星期四", "木曜日",
# "목요일"); a bare "木" or "목" is not taken for a weekday. One list, so the
# grammar stays a single alternation.
_WEEKDAY = one_of(
    [opening + name + closing
     for name in _ZH_WEEKDAYS + _JA_WEEKDAYS + _KO_WEEKDAYS
     for opening, closing in (("(", ")"), ("（", "）"))] +
    _ZH_WEEKDAYS +
    [name for name in _JA_WEEKDAYS + _KO_WEEKDAYS if name.endswith(("曜日", "요일"))]
).suppress()

_AFTERNOON = ("午後", "下午", "오후")


def _cjk_to_24_hour(text, loc, tokens):
    """Parse action of a time after a morning or afternoon marker: turn
    ``hour`` into a 24-hour value and drop the marker, as ``_to_24_hour``
    does for AM/PM."""
    if "ampm" not in tokens:
        return
    hour = int(tokens["hour"])
    if hour > 12:
        raise ParseException(text, loc, "12-hour clock hour above 12")
    tokens["hour"] = "%02d" % (hour % 12 + (12 if tokens["ampm"] in _AFTERNOON else 0))
    del tokens["ampm"]


# "14時30分", "14时30分15秒", "14시 30분", "14時".
_CLOCK_UNITS = (_number("hour") + one_of(["時", "时", "시"]).suppress() +
                Optional(_number("minute") + one_of(["分", "분"]).suppress() +
                         Optional(_number("second") + one_of(["秒", "초"]).suppress())))
_CLOCK_COLON = (_number("hour") + Literal(":").suppress() +
                Word(_DIGITS, exact=2).set_results_name("minute") +
                Optional(Literal(":").suppress() + Word(_DIGITS, exact=2).set_results_name("second")))
_MORNING_OR_AFTERNOON = one_of(["午前", "上午", "오전"] + list(_AFTERNOON)).set_results_name("ampm")
_TIME = ((_MORNING_OR_AFTERNOON + (_CLOCK_COLON | _CLOCK_UNITS)) |
         _CLOCK_UNITS).set_parse_action(_cjk_to_24_hour)

_DAY_UNIT = one_of(["日", "号"])

_YMD = (_number("year", 4) + Literal("年").suppress() +
        _number("month") + Literal("月").suppress() +
        _number("day") + _DAY_UNIT.suppress())
_MD = (_number("month") + Literal("月").suppress() +
       _number("day") + _DAY_UNIT.suppress())
_YMD_KO = (_number("year", 4) + Literal("년").suppress() +
           _number("month") + Literal("월").suppress() +
           _number("day") + Literal("일").suppress())
_MD_KO = (_number("month") + Literal("월").suppress() +
          _number("day") + Literal("일").suppress())

PATTERNS_CJK = [
    {
        "key": "dt:date:date_cjk",
        "name": "Chinese or Japanese date with year, month and day units",
        "pattern": _YMD + Optional(_WEEKDAY) + Optional(_TIME),
        "length": {
            "min": 8,
            "max": 44
        },
        "format": "%Y年%m月%d日",
    },
    {
        "key": "dt:date:date_cjk_ko",
        "name": "Korean date with year, month and day units",
        "pattern": _YMD_KO + Optional(_WEEKDAY) + Optional(_TIME),
        "length": {
            "min": 8,
            "max": 44
        },
        "format": "%Y년 %m월 %d일",
    },
    # Without a year ("5月5日", "5월 5일"): the year comes from ``reference=``.
    {
        "key": "dt:date:date_cjk_noyear",
        "name": "Chinese or Japanese date with month and day units, without year",
        "pattern": _MD + Optional(_WEEKDAY) + Optional(_TIME),
        "length": {
            "min": 4,
            "max": 38
        },
        "format": "%m月%d日",
        "noyear": True,
    },
    {
        "key": "dt:date:date_cjk_ko_noyear",
        "name": "Korean date with month and day units, without year",
        "pattern": _MD_KO + Optional(_WEEKDAY) + Optional(_TIME),
        "length": {
            "min": 4,
            "max": 38
        },
        "format": "%m월 %d일",
        "noyear": True,
    },
]
