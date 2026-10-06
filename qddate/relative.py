"""Opt-in relative-date grammar for ``DateParser.parse_relative()``.

Supports a small, well-tested subset of English and Russian relative-date
phrases. The grammar is intentionally narrow: "today"/"yesterday"/"tomorrow"
plus digit-form and word-form "N days ago" / "N days from now" style
constructions. Locale-aware fuzzy phrases ("last week", "next month") are
out of scope.

The grammar is a separate pyparsing expression rather than another entry in
``ALL_PATTERNS``: it doesn't carry a year, doesn't fit the
``bidi-data-extract`` shape, and uses a different pipeline (resolve against
a reference time, not against ``_pattern_metadata``).
"""

from __future__ import annotations

import datetime
from typing import Optional
from typing import Optional as TOptional

from pyparsing import (
    CaselessKeyword,
    Regex,
    Suppress,
    Word,
    nums,
)
from pyparsing import (
    Optional as PpOptional,
)

# Pre-compiled digit/word integer grammar shared by English and Russian
# phrasings. ``n`` may be a digit sequence ("42") or a word ("forty-two").
_DIGIT_NUMBER = Word(nums)
# Word-form integers are restricted to known number words (and a small set of
# Russian variants) so we don't accidentally swallow "today" / "in" / etc.
# as part of a number match. The pattern is case-insensitive and matches one
# or more tokens from a small allow-list.
_WORD_NUMBER_LIST = (
    "zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    "twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|and|"
    "ноль|один|два|три|четыре|пять|шесть|семь|восемь|девять|десять"
)
_WORD_NUMBER = Regex(r"(?i)(?:" + _WORD_NUMBER_LIST + r")(?:\s+(?:" + _WORD_NUMBER_LIST + r"))*")


def _to_int(token: str) -> int:
    """Convert either a digit string or a word-form number to ``int``.

    Word-form integers are limited to the small set the grammar supports; for
    anything else, ``int(token)`` is tried (which works for digit strings).
    """
    if token.isdigit():
        return int(token)
    # Word-form: try the lookup; fall back to the digit path (the grammar
    # wouldn't emit a non-digit token otherwise).
    return _WORD_NUMBERS.get(token.lower(), int(token))


# English word-form numbers 0-99 (sufficient for "N days ago" patterns).
_WORD_NUMBERS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14,
    "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
    "nineteen": 19, "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50,
    "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90,
}

# Russian word-form numbers 0-99 (transliterated for easy ASCII matching).
_RU_WORD_NUMBERS = {
    "ноль": 0, "один": 1, "два": 2, "три": 3, "четыре": 4, "пять": 5,
    "шесть": 6, "семь": 7, "восемь": 8, "девять": 9, "десять": 10,
}


def _compound_word_to_int(tokens):
    """Resolve ``["twenty", "three"]`` -> 23 by a small lookup table."""
    if isinstance(tokens, str):
        token = tokens.lower()
        return _WORD_NUMBERS.get(token, _RU_WORD_NUMBERS.get(token, int(tokens)))
    parts = [t.lower() for t in tokens]
    if not parts:
        raise ValueError("empty token list")
    total = 0
    current = 0
    for p in parts:
        if p == "hundred":
            current = (current or 1) * 100
            total += current
            current = 0
        elif p == "and":
            continue
        else:
            v = _WORD_NUMBERS.get(p)
            if v is None:
                raise ValueError(f"unknown word-form number: {p!r}")
            current += v
    return total + current


_WORD_NUMBER.set_parse_action(_compound_word_to_int)


class RelativeMatch:
    """Result of resolving a relative phrase against a reference time.

    ``delta`` is the integer offset to apply to the reference (positive =
    future, negative = past) and ``unit`` is one of ``"day"``, ``"week"``,
    ``"month"``, ``"year"``, or ``None`` for "today"/"yesterday"/"tomorrow".
    """

    def __init__(self, days: int = 0, weeks: int = 0, months: int = 0, years: int = 0,
                 anchor: TOptional[str] = None):
        self.days = days
        self.weeks = weeks
        self.months = months
        self.years = years
        # ``anchor`` is one of "today", "yesterday", "tomorrow" (None when the
        # match has a non-zero N-units offset).
        self.anchor = anchor

    def resolve(self, reference: datetime.datetime) -> datetime.datetime:
        """Apply the relative offset to ``reference`` and return a datetime."""
        anchor_date = reference.date()
        if self.anchor == "yesterday":
            anchor_date = anchor_date - datetime.timedelta(days=1)
        elif self.anchor == "tomorrow":
            anchor_date = anchor_date + datetime.timedelta(days=1)
        # Apply the offsets
        total_days = self.days + 7 * self.weeks
        # Use dateutil-style add for months/years (approx via 30 days when
        # dateutil isn't available; for "1 month ago" we use a 30-day window
        # which is good enough for scraping).
        if self.months or self.years:
            try:
                from dateutil.relativedelta import relativedelta  # type: ignore
                anchor_date = anchor_date + relativedelta(months=self.months, years=self.years)
            except ImportError:
                # Fallback: 30 days per month, 365 days per year.
                anchor_date = anchor_date + datetime.timedelta(days=30 * self.months + 365 * self.years)
        if total_days:
            anchor_date = anchor_date + datetime.timedelta(days=total_days)
        return datetime.datetime.combine(anchor_date, reference.time())

    def __repr__(self):
        return (f"RelativeMatch(days={self.days}, weeks={self.weeks}, "
                f"months={self.months}, years={self.years}, anchor={self.anchor!r})")


# English patterns
_EN_TODAY = CaselessKeyword("today").set_parse_action(lambda: RelativeMatch(anchor="today"))
_EN_YESTERDAY = CaselessKeyword("yesterday").set_parse_action(lambda: RelativeMatch(anchor="yesterday"))
_EN_TOMORROW = CaselessKeyword("tomorrow").set_parse_action(lambda: RelativeMatch(anchor="tomorrow"))


def _make_en_offset(unit_keyword: str, unit: str, future_prep: str = "in"):
    """Build ``N <unit>(s) ago`` and ``<future_prep> N <unit>(s)`` patterns."""
    # Match "day" or "days" (and same for week/month/year).
    unit_re = Regex(r"(?i)" + unit_keyword + r"s?")
    # Wrap the number in its own Group; this ensures the parse action sees
    # just the count, not the unit/prep tokens.
    n = (_DIGIT_NUMBER | _WORD_NUMBER)("n")

    ago = (
        n
        + unit_re
        + CaselessKeyword("ago")
    ).set_parse_action(lambda t: RelativeMatch(**{unit + "s": -int(t.n)}))  # type: ignore[arg-type]

    # Build future as either "<prep> N <unit>" or just "N <unit>". The
    # ``Suppress`` drops the prep from the token stream so the parse action
    # only sees the number.
    in_fut = (
        PpOptional(Suppress(CaselessKeyword(future_prep)))
        + n
        + unit_re
    ).set_parse_action(lambda t: RelativeMatch(**{unit + "s": int(t.n)}))  # type: ignore[arg-type]

    return ago, in_fut


def _make_en_nounit(unit_keyword: str, unit: str):
    """Build plain ``N <unit>(s)`` (positive direction, no prep)."""
    unit_re = Regex(r"(?i)" + unit_keyword + r"s?")
    n = (_DIGIT_NUMBER | _WORD_NUMBER)("n")
    return (
        n
        + unit_re
    ).set_parse_action(lambda t: RelativeMatch(**{unit + "s": int(t.n)}))  # type: ignore[arg-type]


# Combine each unit's positive offset into "N <unit>" (handles "5 days" alone).
_EN_DAYS_PLAIN = _make_en_nounit("day", "day")
_EN_WEEKS_PLAIN = _make_en_nounit("week", "week")
_EN_MONTHS_PLAIN = _make_en_nounit("month", "month")
_EN_YEARS_PLAIN = _make_en_nounit("year", "year")


_EN_DAYS_AGO, _EN_DAYS_IN = _make_en_offset("day", "day")
_EN_WEEKS_AGO, _EN_WEEKS_IN = _make_en_offset("week", "week")
_EN_MONTHS_AGO, _EN_MONTHS_IN = _make_en_offset("month", "month")
_EN_YEARS_AGO, _EN_YEARS_IN = _make_en_offset("year", "year")

# Russian patterns (lowercase Cyrillic; case-insensitive match).
_RU_TODAY = Regex(r"(?i)\bсегодня\b").set_parse_action(lambda: RelativeMatch(anchor="today"))
_RU_YESTERDAY = Regex(r"(?i)\bвчера\b").set_parse_action(lambda: RelativeMatch(anchor="yesterday"))
_RU_TOMORROW = Regex(r"(?i)\bзавтра\b").set_parse_action(lambda: RelativeMatch(anchor="tomorrow"))


def _make_ru_ago(unit_word: str, unit: str):
    """Build ``N <unit> назад`` (Russian: N unit ago)."""
    n = (_DIGIT_NUMBER | _WORD_NUMBER)("n")
    pat = (
        n
        + CaselessKeyword(unit_word)
        + CaselessKeyword("назад")
    ).set_parse_action(lambda t: RelativeMatch(**{unit + "s": -int(t.n)}))  # type: ignore[arg-type]
    return pat


def _make_ru_through(unit_word: str, unit: str):
    """Build ``через N <unit>`` (Russian: in N unit)."""
    n = (_DIGIT_NUMBER | _WORD_NUMBER)("n")
    pat = (
        Suppress(CaselessKeyword("через"))
        + n
        + CaselessKeyword(unit_word)
    ).set_parse_action(lambda t: RelativeMatch(**{unit + "s": int(t.n)}))  # type: ignore[arg-type]
    return pat


_RU_DAYS_AGO = (_make_ru_ago("дней", "day")
                  | _make_ru_ago("дня", "day")
                  | _make_ru_ago("день", "day"))
_RU_WEEKS_AGO = (_make_ru_ago("недель", "week")
                | _make_ru_ago("недели", "week")
                | _make_ru_ago("неделю", "week"))
_RU_MONTHS_AGO = (_make_ru_ago("месяцев", "month")
                 | _make_ru_ago("месяца", "month")
                 | _make_ru_ago("месяц", "month"))
_RU_YEARS_AGO = (_make_ru_ago("лет", "year")
                | _make_ru_ago("года", "year")
                | _make_ru_ago("год", "year"))

_RU_DAYS_THROUGH = (_make_ru_through("дней", "day")
                   | _make_ru_through("дня", "day")
                   | _make_ru_through("день", "day"))
_RU_WEEKS_THROUGH = (_make_ru_through("недель", "week")
                     | _make_ru_through("недели", "week")
                     | _make_ru_through("неделю", "week"))
_RU_MONTHS_THROUGH = (_make_ru_through("месяцев", "month")
                      | _make_ru_through("месяца", "month")
                      | _make_ru_through("месяц", "month"))
_RU_YEARS_THROUGH = (_make_ru_through("лет", "year")
                     | _make_ru_through("года", "year")
                     | _make_ru_through("год", "year"))


# Top-level English/Russian expressions
_EN_RELATIVE = (
    _EN_TODAY | _EN_YESTERDAY | _EN_TOMORROW
    | _EN_DAYS_AGO | _EN_DAYS_IN | _EN_DAYS_PLAIN
    | _EN_WEEKS_AGO | _EN_WEEKS_IN | _EN_WEEKS_PLAIN
    | _EN_MONTHS_AGO | _EN_MONTHS_IN | _EN_MONTHS_PLAIN
    | _EN_YEARS_AGO | _EN_YEARS_IN | _EN_YEARS_PLAIN
)
_RU_RELATIVE = (
    _RU_TODAY | _RU_YESTERDAY | _RU_TOMORROW
    | _RU_DAYS_AGO | _RU_DAYS_THROUGH
    | _RU_WEEKS_AGO | _RU_WEEKS_THROUGH
    | _RU_MONTHS_AGO | _RU_MONTHS_THROUGH
    | _RU_YEARS_AGO | _RU_YEARS_THROUGH
)

_RELATIVE_GRAMMAR = _EN_RELATIVE | _RU_RELATIVE


def parse_relative(text: str, reference: datetime.datetime) -> Optional[datetime.datetime]:
    """Try to resolve ``text`` as a relative-date phrase against ``reference``.

    Returns a ``datetime`` (with the time of ``reference``) on success;
    ``None`` if no relative phrase matches.

    Supported phrases (English): ``today``, ``yesterday``, ``tomorrow``,
    ``N day(s) ago``, ``(in) N day(s)`` (and the same for weeks/months/years).

    Supported phrases (Russian): ``сегодня``, ``вчера``, ``завтра``, ``N
    <unit> назад``, ``через N <unit>``.
    """
    text = (text or "").strip()
    if not text:
        return None
    # Require the match to consume the whole input (no trailing text).
    try:
        tokens = _RELATIVE_GRAMMAR.parseString(text, parseAll=True)
    except Exception:
        return None
    if not tokens:
        return None
    match_obj = tokens[0]
    if not isinstance(match_obj, RelativeMatch):
        return None
    return match_obj.resolve(reference)
