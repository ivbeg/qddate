#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

import datetime
import numbers
import re
import time
import warnings
from dataclasses import dataclass
from typing import Any, Iterator, NamedTuple, Optional, Union
from typing import Optional as TOptional

from pyparsing import (
    And,
    CaselessLiteral,
    Empty,
    Forward,
    LineStart,
    Literal,
    Located,
    MatchFirst,
    OneOrMore,
    Or,
    ParseBaseException,
    ParserElement,
    Regex,
    StringStart,
    TokenConverter,
    Word,
    ZeroOrMore,
    lineStart,
    nums,
    one_of,
)
from pyparsing import Optional as PpOptional

# Enable packrat parsing for better performance
try:
    ParserElement.enable_packrat()
except Exception:
    # Packrat is an optimization; if it is unavailable or fails, fall back to
    # standard parsing rather than crashing on import.
    pass

from .dirty import matchPrefix
from .patterns import (
    _PATTERN_METADATA,
    ALL_PATTERNS,
    ALL_TIME_PREFIXES,
    BASE_TIME_PATTERNS,
    MONTHS_BY_LANGUAGE,
    SUPPORTED_LANGUAGES,
    TIME_PREFIXES_BY_LANGUAGE,
    TIMEZONE_ABBREVIATIONS,
    _infer_required_chars,
    get_patterns_for_languages,
)
from .patterns.base import ENG_WEEKDAYS
from .patterns.cz import CZ_WEEKDAYS
from .patterns.de import DE_WEEKDAYS
from .patterns.es import ES_WEEKDAYS
from .patterns.fr import FR_WEEKDAYS
from .patterns.it import IT_WEEKDAYS
from .patterns.nl import NL_WEEKDAYS
from .patterns.pt import PT_WEEKDAYS
from .patterns.ru import RUS_WEEKDAYS
from .relative import parse_relative as _parse_relative


# Pre-compiled month-name sets for language detection. Built once at import
# time from `MONTHS_BY_LANGUAGE` (the canonical month table) so adding a
# language touches one place.
def _lang_month_names(code: str) -> frozenset:
    """Return the month names (in their original casing) for ``code`` that
    the language-detection heuristic should use.

    Includes only the language-specific full names plus genitive forms (for
    Russian/Ukrainian/Polish/Czech, where the genitive is grammatically
    required after a numeric day). Does **not** include abbreviations —
    abbreviations like ``Jan``/``Feb`` are shared across languages (English,
    German, French, Portuguese all abbreviate to ``Jan``/``Fev``) and
    including them causes false-positive language detection. The legacy
    code excluded abbreviations for the same reason.

    Names listed in ``detect_excludes`` are removed (Romanian ``mai``/``august``
    are excluded because they collide with Portuguese/English/Dutch/German).
    """
    data = MONTHS_BY_LANGUAGE.get(code)
    if data is None:
        return frozenset()
    out = set(data.full) | set(data.full_lc)
    if data.genitive:
        out |= set(data.genitive)
    if data.genitive_lc:
        out |= set(data.genitive_lc)
    if data.detect_excludes:
        out -= set(data.detect_excludes)
    return frozenset(out)


_RUSSIAN_MONTHS = _lang_month_names("ru")
_FRENCH_MONTHS = _lang_month_names("fr")
_SPANISH_MONTHS = _lang_month_names("es")
_ITALIAN_MONTHS = _lang_month_names("it")
_PORTUGUESE_MONTHS = _lang_month_names("pt")
_ROMANIAN_MONTHS = _lang_month_names("ro")
_UKRAINIAN_MONTHS = _lang_month_names("uk")
_CZECH_MONTHS = _lang_month_names("cz")
_POLISH_MONTHS = _lang_month_names("pl")
_ENGLISH_MONTHS = _lang_month_names("en")
_GERMAN_MONTHS = _lang_month_names("de")
_DUTCH_MONTHS = _lang_month_names("nl")
_TURKISH_MONTHS = _lang_month_names("tr")
_BULGARIAN_MONTHS = _lang_month_names("bg")

# Word tokenizer shared by language detection: letters only, so "28." and
# "Segunda-feira" split into words the same way the month/weekday sets do.
_WORD_RE = re.compile(r"[^\W\d_]+")

# Month sets that claim a language, in precedence order. Several full month
# names are shared (German/Dutch "Juni", German/French "Mai", Russian/Bulgarian
# "Август"; every shared name maps to the same month number, see
# tests/test_regressions_2026_10.py). ``_detect_language`` narrows to the first
# claiming language; when its patterns find nothing, ``_iter_matches`` tries
# the patterns of every language.
_CYRILLIC_DETECTION: tuple[tuple[str, frozenset[str]], ...] = (
    ("uk", _UKRAINIAN_MONTHS),
    ("ru", _RUSSIAN_MONTHS),
    ("bg", _BULGARIAN_MONTHS),
)
# Romanian stays after the other Romance languages so an unrestricted parser
# does not relabel ambiguous "mai"; Dutch is listed before German as before.
_LATIN_DETECTION: tuple[tuple[str, frozenset[str]], ...] = (
    ("fr", _FRENCH_MONTHS),
    ("es", _SPANISH_MONTHS),
    ("it", _ITALIAN_MONTHS),
    ("pt", _PORTUGUESE_MONTHS),
    ("cz", _CZECH_MONTHS),
    ("pl", _POLISH_MONTHS),
    ("ro", _ROMANIAN_MONTHS),
    ("en", _ENGLISH_MONTHS),
    ("nl", _DUTCH_MONTHS),
    ("de", _GERMAN_MONTHS),
    ("tr", _TURKISH_MONTHS),
)


def _lang_weekday_words(*names_lists) -> frozenset:
    """Lower-cased word tokens of the given weekday names."""
    return frozenset(
        word
        for names in names_lists
        for name in names
        for word in _WORD_RE.findall(name.lower())
    )


# Full weekday names of the languages that have weekday patterns. A weekday
# breaks the tie when the month name is shared ("Montag, 18 Juni 1953" is
# German, not Dutch).
_WEEKDAYS_BY_LANGUAGE = {
    "en": _lang_weekday_words(ENG_WEEKDAYS),
    "de": _lang_weekday_words(DE_WEEKDAYS),
    "nl": _lang_weekday_words(NL_WEEKDAYS),
    "fr": _lang_weekday_words(FR_WEEKDAYS),
    "es": _lang_weekday_words(ES_WEEKDAYS),
    "it": _lang_weekday_words(IT_WEEKDAYS),
    "pt": _lang_weekday_words(PT_WEEKDAYS),
    "cz": _lang_weekday_words(CZ_WEEKDAYS),
    "ru": _lang_weekday_words(RUS_WEEKDAYS),
}


def _resolve_month_claims(claims: list, words: frozenset) -> list:
    """Pick the language among those whose month names occur in the text.

    A single claim is returned as is. With a shared month name, a weekday
    name of exactly one claiming language decides; otherwise every claiming
    language is returned, so the filters do not narrow to one of them.
    """
    if len(claims) <= 1:
        return claims
    by_weekday = [
        lang for lang in claims
        if not words.isdisjoint(_WEEKDAYS_BY_LANGUAGE.get(lang, ()))
    ]
    if len(by_weekday) == 1:
        return by_weekday
    return claims

# Pre-compiled pyparsing patterns for year format detection (compiled once at module level)
# 4-digit year: 4 consecutive digits (Word naturally handles word boundaries)
_YEAR_4DIGIT_PATTERN = Word(nums, exact=4)
# 2-digit year: separator + 2 digits + boundary (use Regex for complex pattern within pyparsing)
_YEAR_2DIGIT_PATTERN = Regex(r'[/.\-,\s]\d{2}(?=\s|$|[^\d])')

# Character set constants for pattern filtering
CHAR_SET_DIGITS = 'digits'
CHAR_SET_LATIN = 'latin'
CHAR_SET_CYRILLIC = 'cyrillic'
CHAR_SET_ACCENTED = 'accented'
CHAR_SET_SEPARATORS = 'separators'

# Language to character set mapping
LANGUAGE_CHAR_SETS = {
    'ru': {CHAR_SET_DIGITS, CHAR_SET_CYRILLIC},
    'bg': {CHAR_SET_DIGITS, CHAR_SET_CYRILLIC},
    'fr': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'cz': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'pl': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'es': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'it': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'pt': {CHAR_SET_DIGITS, CHAR_SET_ACCENTED},
    'ro': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
    'uk': {CHAR_SET_DIGITS, CHAR_SET_CYRILLIC},
    'de': {CHAR_SET_DIGITS, CHAR_SET_LATIN},  # may have umlauts but treated as latin
    'tr': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
    'en': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
    'nl': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
}


# Priority tiers keyed by exact basekey. These replace the former substring
# checks ("date_1" in basekey also matched "date_10"); each set preserves the
# exact scoring the substring version produced.
_PRIORITY_TIER_COMMON = frozenset({
    "dt:date:date_1", "dt:date:date_2", "dt:date:date_10",
})
_PRIORITY_TIER_ISO = frozenset({
    "dt:date:date_iso8601", "dt:date:date_iso8601_short",
})
_PRIORITY_TIER_9 = frozenset({"dt:date:date_9"})
_PRIORITY_TIER_MID = frozenset({
    # date_4_point matched the legacy "date_4" substring check; kept for parity.
    "dt:date:date_3", "dt:date:date_4", "dt:date:date_5", "dt:date:date_6",
    "dt:date:date_4_point",
})
_PRIORITY_SLASH_BOOST = frozenset({
    "dt:date:date_1", "dt:date:date_8", "dt:date:date_usa",
    "dt:date:date_usa_1", "dt:date:date_10",
})
_PRIORITY_DOT_BOOST = frozenset({
    "dt:date:date_2", "dt:date:date_4", "dt:date:date_10", "dt:date:date_4_point",
})
_PRIORITY_DASH_BOOST = frozenset({
    "dt:date:date_iso8601", "dt:date:date_iso8601_short", "dt:date:date_9",
})


# ``DateMatch.datetime`` hides the module name inside the class body.
_TzInfo = datetime.tzinfo


@dataclass
class DateMatch:
    """Typed result of a successful date match.

    Returned by :meth:`DateParser.match_typed`. ``.to_dict()`` provides a plain
    mapping for callers that need the old-style shape.

    The ``format_date()`` method is the natural inverse of parsing: it formats
    ``self.datetime`` back into the locale-aware string the parser originally
    matched, so the result round-trips through :meth:`DateParser.parse`.

    Fields:

    - ``span``: ``(start, end)`` of the date in ``raw``; ``start`` is always 0
      (a date must start the text) and ``raw[end:]`` is the text after it.
    - ``precision``: the finest unit the text states: ``"day"`` (no time),
      ``"hour"`` ("3 PM"), ``"minute"`` or ``"second"``.
    - ``tzinfo``: the timezone written in the text (``+03:00``, ``MSK``),
      or None. Set whether or not the parser has ``tz_aware=True``; only with
      it is ``datetime`` aware.
    - ``has_year``: False when the year was not in the text and was taken from
      the reference (patterns with the ``noyear`` flag).
    """

    datetime: datetime.datetime
    pattern_key: str
    language: TOptional[str]
    format: str
    raw: str
    span: tuple[int, int] = (0, 0)
    precision: str = "day"
    tzinfo: TOptional[_TzInfo] = None
    has_year: bool = True

    def to_dict(self) -> dict:
        return {
            "datetime": self.datetime,
            "pattern_key": self.pattern_key,
            "language": self.language,
            "format": self.format,
            "raw": self.raw,
            "span": self.span,
            "precision": self.precision,
            "tzinfo": self.tzinfo,
            "has_year": self.has_year,
        }

    def format_date(self) -> str:
        """Format ``self.datetime`` using the pattern's ``format`` string.

        Round-trips through :meth:`DateParser.parse` for the same pattern —
        ``parser.parse(match.format_date())`` returns the same datetime (modulo
        the year-folding behaviour of two-digit-year patterns).
        """
        if not self.format:
            return self.datetime.isoformat()
        return self.datetime.strftime(self.format)


def format_date(dt: datetime.datetime, pattern_key: str) -> str:
    """Format ``dt`` using the ``format`` string of the given pattern.

    ``pattern_key`` may be a base pattern key (e.g.
    ``"dt:date:date_eng1_short"``) or a generated key (e.g.
    ``"dt:date:date_rus2:t_right"``). The lookup searches ``ALL_PATTERNS``
    by base key / basekey; if a generated key doesn't match, the caller can
    pass ``DateParser.patterns`` to a parser instance and the format string
    is read from the matching generated pattern.

    Args:
        dt: the value to format.
        pattern_key: the pattern key (base or generated) whose ``format`` strftime
            string to apply.

    Raises:
        ValueError: if ``pattern_key`` does not resolve to any base pattern.
    """
    for pat in ALL_PATTERNS:
        if pat["key"] == pattern_key or pat.get("basekey") == pattern_key:
            fmt = pat.get("format", "")
            if not fmt:
                return dt.isoformat()
            return dt.strftime(fmt)
    # Fall back: the caller might have passed a generated key. We can't
    # resolve it without a parser instance, so the legacy string-based
    # format lookup stops here. For callers that need round-tripping
    # against a generated key, use ``DateParser.format_date(dt, key)``
    # which can look up the parser's own pattern list.
    raise ValueError(
        f"Unknown pattern_key {pattern_key!r}; expected a base key from "
        f"qddate.patterns.ALL_PATTERNS, or a generated key for a parser "
        f"instance — in the latter case use ``DateParser.format_date``. "
        f"For the matching pattern, use ``DateMatch.pattern_key`` directly."
    )


def _append(expr, extra):
    """Return ``expr + extra``, or ``expr`` unchanged when ``extra`` is None."""
    return expr if extra is None else expr + extra


def _values_in_range(d):
    """Sanity-check matched date/time components.

    ``match()`` historically validated only month/day, which let impossible times
    (e.g. ``25:70``) surface as valid matches while ``parse()`` rejected them.
    """
    month_val = d.get("month")
    if month_val is not None and not 1 <= int(month_val) <= 12:
        return False
    day_val = d.get("day")
    if day_val is not None and not 1 <= int(day_val) <= 31:
        return False
    hour_val = d.get("hour")
    if hour_val is not None and int(hour_val) > 23:
        return False
    minute_val = d.get("minute")
    if minute_val is not None and int(minute_val) > 59:
        return False
    second_val = d.get("second")
    if second_val is not None and int(second_val) > 59:
        return False
    return True


def parse_timezone(text: TOptional[str]) -> TOptional[datetime.timezone]:
    """Return the fixed-offset timezone written as ``text``, or None.

    ``text`` is the ``timezone`` value of a match: a numeric offset
    (``+0300``, ``+03:00``, ``-0500``, the legacy three digits ``+300``),
    ``Z``, ``GMT``/``UTC`` alone or with an offset (``GMT+3``, ``UTC-05:30``)
    or an abbreviation from ``qddate.patterns.TIMEZONE_ABBREVIATIONS``
    (``MSK``, ``МСК``, ``CEST``, ``PDT``). An abbreviation's timezone carries
    its name. Offsets of 24 hours or more, or with minutes above 59, give None.
    """
    if not text:
        return None
    text = str(text)
    if text == "Z":
        return datetime.timezone.utc
    offset = text
    after_utc = text[:3] in ("GMT", "UTC")
    if after_utc:
        offset = text[3:]
        if not offset:
            return datetime.timezone.utc
    else:
        minutes = TIMEZONE_ABBREVIATIONS.get(text)
        if minutes is not None:
            return datetime.timezone(datetime.timedelta(minutes=minutes), text)
    if offset[:1] not in ("+", "-") or len(offset) < 2:
        return None
    sign = -1 if offset[0] == "-" else 1
    digits = offset[1:]
    if ":" in digits:
        hours_text, minutes_text = digits.split(":", 1)
    elif after_utc and len(digits) <= 2:
        # "GMT+3": hours only.
        hours_text, minutes_text = digits, "0"
    else:
        digits = digits.zfill(4)
        hours_text, minutes_text = digits[:-2], digits[-2:]
    if not (hours_text.isdigit() and minutes_text.isdigit()):
        return None
    hours, minutes = int(hours_text), int(minutes_text)
    if hours > 23 or minutes > 59:
        return None
    return datetime.timezone(sign * datetime.timedelta(hours=hours, minutes=minutes))


def _precision(values) -> str:
    """The finest unit a match states: ``"second"``, ``"minute"``, ``"hour"``
    (a 12-hour time without minutes, "3 PM") or ``"day"``."""
    for unit in ("second", "minute", "hour"):
        if unit in values:
            return unit
    return "day"


def _original_index(text: str, end: int) -> int:
    """Map ``end``, an index into ``text.expandtabs()``, back to ``text``."""
    if "\t" not in text:
        return end
    pos = column = 0
    for i, char in enumerate(text):
        if pos >= end:
            return i
        if char == "\t":
            step = 8 - column % 8
        else:
            step = 1
        pos += step
        column = 0 if char in "\r\n" else column + step
    return len(text)


# Numeric patterns by the order they read day, month and year in. With
# ``date_order=`` the patterns of that order win when several read the same
# text ("05/06/2022": ``date_1`` day first, ``date_usa`` month first).
# Dotted and dashed dates have no month-first pattern, so "MDY" leaves them
# day first; four-digit-year-first dates ("2022-05-06") are not ambiguous.
_DATE_ORDER_BASEKEYS = {
    "DMY": frozenset({
        "dt:date:date_1", "dt:date:date_2", "dt:date:date_4", "dt:date:date_4_point",
        "dt:date:date_5", "dt:date:date_8", "dt:date:date_iso8601",
        "dt:date:date_iso8601_short", "dt:date:weekday_eng_iso",
        "dt:date:weekday_short_eng_iso",
    }),
    "MDY": frozenset({"dt:date:date_usa", "dt:date:date_usa_1"}),
    "YMD": frozenset({
        "dt:date:date_3", "dt:date:date_6", "dt:date:date_9", "dt:date:date_10",
    }),
}
# Larger than any priority difference, so the order decides between patterns
# that consume the same text; a longer match still wins.
_DATE_ORDER_BONUS = 1000

#: A date without a year is moved to the previous year (``prefer="past"``) only
#: when it lies more than this after the reference, and to the next year
#: (``prefer="future"``) only when it lies more than this before it; the slack
#: absorbs timezone differences between the page and the reference.
NOYEAR_ROLLOVER_GRACE = datetime.timedelta(days=2)

_PREFER_VALUES = (None, "past", "future")


def _check_prefer(prefer: TOptional[str]) -> None:
    """Validate ``prefer=``: None, "past" or "future"."""
    if prefer not in _PREFER_VALUES:
        raise ValueError(f"prefer must be 'past', 'future' or None; got {prefer!r}")


def _roll_year(dt: datetime.datetime, reference: datetime.datetime,
               prefer: str) -> TOptional[datetime.datetime]:
    """Move ``dt``, a date without a written year, to the year ``prefer``
    asks for relative to ``reference``; None when the day does not exist in
    that year (29 February). Compares wall-clock times."""
    ref = reference.replace(tzinfo=None)
    year = dt.year
    if prefer == "past" and dt > ref + NOYEAR_ROLLOVER_GRACE:
        year -= 1
    elif prefer == "future" and dt < ref - NOYEAR_ROLLOVER_GRACE:
        year += 1
    if year == dt.year:
        return dt
    try:
        return dt.replace(year=year)
    except ValueError:
        return None


def _check_date_order(date_order: TOptional[str]) -> TOptional[str]:
    """Validate ``date_order=``: None or "DMY"/"MDY"/"YMD" (any case)."""
    if date_order is None:
        return None
    if isinstance(date_order, str) and date_order.upper() in _DATE_ORDER_BASEKEYS:
        return date_order.upper()
    raise ValueError(
        f"date_order must be 'DMY', 'MDY', 'YMD' or None; got {date_order!r}")


def _check_languages(languages: Union[str, list[str], tuple[str, ...], set[str], frozenset[str], None]
                     ) -> TOptional[frozenset]:
    """Validate a ``languages=`` hint; None or empty means no hint."""
    if languages is None:
        return None
    if isinstance(languages, str):
        languages = [languages]
    elif not isinstance(languages, (list, tuple, set, frozenset)):
        raise TypeError("languages must be a string, list of strings, or None")
    codes = frozenset(languages)
    invalid = sorted(codes - set(SUPPORTED_LANGUAGES))
    if invalid:
        raise ValueError(
            f"Unsupported language(s): {invalid}. "
            f"Supported languages: {SUPPORTED_LANGUAGES}")
    return codes or None


# Entries kept in ``DateParser._walk_cache`` before it is emptied.
_WALK_CACHE_SIZE = 4096


# Digits, separators and spaces: what the numeric parts of a date are made of.
# A grammar element that matches nowhere in this string needs a letter.
_NON_LETTER_PROBE = "0123456789 .,/-:+'‘’()[]|"


class _GrammarNeeds(NamedTuple):
    """What a text must contain for a grammar to match it at position 0.

    ``words`` holds one set of regexes per required element that needs a
    letter (a month or weekday name list); from each set, one regex must be
    found in the text. ``first`` is the set of characters such a match can
    start with when the text does not start with whitespace, or ``None`` when
    it is not known.
    """
    words: frozenset
    first: TOptional[frozenset]


_NO_NEEDS = _GrammarNeeds(frozenset(), None)


def _grammar_needs(expr: ParserElement, cache: dict[int, tuple[Any, _GrammarNeeds]]) -> _GrammarNeeds:
    """Return the :class:`_GrammarNeeds` of the pyparsing grammar ``expr``.

    Both are necessary conditions: a text that lacks one cannot match, so
    ``_match_candidates`` skips the grammar without running it. Elements this
    function does not know contribute nothing, which only weakens the check.

    ``cache`` maps ``id(element)`` to ``(element, needs)``, so a base grammar
    shared by its generated variants is analysed once.
    """
    entry = cache.get(id(expr))
    if entry is not None and entry[0] is expr:
        return entry[1]
    # Placeholder for a grammar that refers to itself through a ``Forward``.
    cache[id(expr)] = (expr, _NO_NEEDS)
    needs = _NO_NEEDS
    if isinstance(expr, Regex):
        # ``one_of`` compiles a month or weekday list to one regex, which is
        # what the element matches with, so searching with it is exact.
        if expr.re.search(_NON_LETTER_PROBE) is None:
            needs = _GrammarNeeds(frozenset({frozenset({expr.re})}), None)
    elif isinstance(expr, Word):
        needs = _GrammarNeeds(frozenset(), frozenset(expr.initChars))
    elif isinstance(expr, Literal) and not isinstance(expr, CaselessLiteral):
        if expr.match:
            needs = _GrammarNeeds(frozenset(), frozenset(expr.match[0]))
    elif isinstance(expr, (LineStart, StringStart, Empty)):
        # Match without consuming a character.
        needs = _GrammarNeeds(frozenset(), frozenset())
    elif isinstance(expr, And):
        parts = [_grammar_needs(part, cache) for part in expr.exprs]
        # Every part is required, so are their words. The text starts with
        # the first part that cannot match empty, or with an empty-matching
        # part before it.
        starts: set = set()
        start_known = False
        for part, part_needs in zip(expr.exprs, parts):
            if part_needs.first is None:
                break
            starts |= part_needs.first
            if not part.mayReturnEmpty:
                start_known = True
                break
        needs = _GrammarNeeds(
            frozenset().union(*(p.words for p in parts)),
            frozenset(starts) if start_known else None)
    elif isinstance(expr, (MatchFirst, Or)):
        alternatives = [_grammar_needs(alt, cache) for alt in expr.exprs]
        # Any alternative may match. Each one that needs words finds one of
        # its regexes, so one regex of all of them must be found, provided
        # every alternative needs words.
        words: frozenset = frozenset()
        if alternatives and all(alt.words for alt in alternatives):
            words = frozenset({frozenset(
                rx for alt in alternatives for regexes in alt.words for rx in regexes)})
        firsts = [alt.first for alt in alternatives if alt.first is not None]
        needs = _GrammarNeeds(
            words,
            frozenset().union(*firsts)
            if alternatives and len(firsts) == len(alternatives) else None)
    elif isinstance(expr, (PpOptional, ZeroOrMore)):
        # Not required, but when present the match starts with it.
        if expr.expr is not None:
            needs = _GrammarNeeds(frozenset(), _grammar_needs(expr.expr, cache).first)
    elif isinstance(expr, (TokenConverter, OneOrMore, Located, Forward)):
        # Wrappers that require their element (``Suppress``, ``Combine``, …).
        if expr.expr is not None:
            needs = _grammar_needs(expr.expr, cache)
    cache[id(expr)] = (expr, needs)
    return needs


def _may_match(grammar: ParserElement, text: str,
               cache: dict[int, tuple[Any, _GrammarNeeds]], found: dict) -> bool:
    """Return False when ``grammar`` cannot match ``text`` at position 0.

    ``text`` is the text with tabs expanded, as pyparsing reads it. ``cache``
    is the ``_grammar_needs`` cache; ``found`` caches, for this text, whether
    a set of regexes is found in it.
    """
    needs = _grammar_needs(grammar, cache)
    # An element after the first one skips whitespace before it, so a text
    # starting with whitespace may start a match with a different character.
    first_char = text[:1]
    if (needs.first is not None and first_char not in needs.first
            and not first_char.isspace() and not grammar.mayReturnEmpty):
        return False
    for regexes in needs.words:
        hit = found.get(regexes)
        if hit is None:
            hit = found[regexes] = any(rx.search(text) for rx in regexes)
        if not hit:
            return False
    return True


def _pattern_language(pattern):
    """Return a pattern's language, resolving generated variants via ``basekey``.

    Reads the explicit ``language`` field stamped from ``_PATTERN_METADATA``. For
    patterns produced by ``DateParser.__generate`` (whose ``key`` is suffixed, e.g.
    ``dt:date:de_base:time_1``), the field is inherited from the base pattern at
    copy time; the ``basekey`` lookup is a fallback for safety.
    """
    lang = pattern.get("language")
    if lang is not None:
        return lang
    basekey = pattern.get("basekey", pattern.get("key", ""))
    entry = _PATTERN_METADATA.get(basekey)
    return entry[0] if entry else None


def _pattern_separator(pattern):
    """Return a pattern's separator, resolving generated variants via ``basekey``."""
    sep = pattern.get("separator")
    if sep is not None:
        return sep
    basekey = pattern.get("basekey", pattern.get("key", ""))
    entry = _PATTERN_METADATA.get(basekey)
    return entry[1] if entry else "mixed"


def _index_by_fingerprint(patterns):
    """Group pattern dicts by fingerprint: ``{FingerprintKey: [pattern, ...]}``.

    Buckets keep the order of ``patterns``.
    """
    # Local import: ``qddate.patterns.fingerprint`` imports from
    # ``qddate.patterns``, which this module imports at load time.
    from .patterns.fingerprint import compute_pattern_fingerprint

    index: dict = {}
    for p in patterns:
        index.setdefault(compute_pattern_fingerprint(p), []).append(p)
    return index


def scan_char_sets(text):
    """Single-pass scanner returning set of character categories present in text.

    Optimized version: limits scanning to first 100 characters and uses early exit.

    :param text: Input string to scan
    :type text: str
    :return: Set of character set constants present in the text
    :rtype: set
    """
    if not text:
        return set()

    char_sets = set()
    # Accented characters for various languages
    # French: éàèùâêîôûçÉÀÈÙÂÊÎÔÛÇ
    # Spanish: áíóúñÁÍÓÚÑ
    # German: äöüÄÖÜ
    # Czech/Polish: řžýčšďťňŘŽÝČŠĎŤŇ
    accented_chars = 'éàèùâêîôûçÉÀÈÙÂÊÎÔÛÇáíóúñÁÍÓÚÑäöüÄÖÜřžýčšďťňŘŽÝČŠĎŤŇ'

    # Limit scanning to first 100 characters (dates are rarely longer)
    scan_len = min(100, len(text))

    # Scan for character sets with early exit optimization
    for i in range(scan_len):
        char = text[i]
        if char.isdigit():
            char_sets.add(CHAR_SET_DIGITS)
        elif 'а' <= char.lower() <= 'я' or char in 'ёЁ':
            char_sets.add(CHAR_SET_CYRILLIC)
        elif char.isalpha() and ord(char) < 128:
            char_sets.add(CHAR_SET_LATIN)
        elif char in accented_chars:
            char_sets.add(CHAR_SET_ACCENTED)
        elif char in './-, ':
            char_sets.add(CHAR_SET_SEPARATORS)

        # Early exit optimization: once we've found all possible sets, we can stop
        # Maximum possible sets: digits, cyrillic, latin, accented, separators (5)
        if len(char_sets) >= 5:
            break

    return char_sets


def _month_claims(text: str, char_sets) -> list:
    """Languages whose month names occur in ``text`` as whole words.

    ``char_sets`` is ``scan_char_sets(text)``; it selects the Cyrillic or the
    Latin-script table. See :meth:`DateParser._language_claims`.
    """
    if CHAR_SET_CYRILLIC in char_sets:
        table = _CYRILLIC_DETECTION
    elif CHAR_SET_ACCENTED in char_sets or CHAR_SET_LATIN in char_sets:
        table = _LATIN_DETECTION
    else:
        return []
    # Whole words only: a substring check lets French "mai" claim
    # Portuguese "maio", which then filters out the Portuguese patterns.
    words = frozenset(_WORD_RE.findall(text.lower()))
    claims = [lang for lang, months in table if not words.isdisjoint(months)]
    return _resolve_month_claims(claims, words)


class DateParser:
    """Class to use pyparsing-based patterns to parse dates"""

    def __init__(self, generate: bool = True, patterns: list[dict] = ALL_PATTERNS,
                 base_only: bool = False, languages: Union[str, list[str], None] = None,
                 pivot_year: int | None = None, tz_aware: bool = False,
                 use_fingerprint: bool = True, date_order: str | None = None) -> None:
        """Inits class DataParser
        :param generate: Boolean value, if true, than automatically generate all patterns from base list
        :param patterns: list of patterns to be used. Default ALL_PATTERNS. See qddate.patterns for more info
        :param base_only: Use only base patterns during generation of final list.
                          Filters all patterns with text after datetime.
        :param languages: Language code (str) or list of language codes (list of str) to filter patterns by.
                          If None, uses all patterns. If specified, filters patterns to only include those
                          for the specified languages. Examples: languages="ru", languages=["en", "de"],
                          languages=None (default).
        :type languages: str|list|None
        :param pivot_year: Optional 4-digit pivot year for interpreting 2-digit years (patterns with the
                          ``yearshort`` flag). Years ``00`` to ``(pivot_year % 100) - 1`` map to 20xx, the
                          rest to 19xx. Example: pivot_year=1968 maps 05/16/99 to 1999 and 05/16/20 to 2020.
                          If None (default), 2-digit years are passed through unchanged. A bool or any
                          other non-integer raises ``TypeError``: ``True`` would act as pivot year 1
                          (only ``00`` maps to 2000), so ``pivot_year=True`` is not a way to switch the
                          pivot on.
        :type pivot_year: int|None
        :param tz_aware: If True, a timezone written after the time (``+0300``, ``+03:00``, ``Z``,
                         ``GMT+3``, ``MSK``; see :func:`parse_timezone`) is attached to the returned
                         datetime (making it timezone-aware). Default False keeps returning naive datetimes.
        :type tz_aware: bool
        :param use_fingerprint: When True (the default since ``1.0.14``), route
                                ``match()`` / ``match_all()`` / ``parse()`` through the
                                ``_filter_patterns_fingerprint`` (single-walk intersection over the
                                precomputed ``qddate.patterns.fingerprint._PATTERN_FINGERPRINTS``
                                index). When False, fall through to the legacy 6-level filter
                                (``_filter_patterns_hierarchical``). The two paths are
                                **exactly equivalent** on the extended probe corpus
                                (``tests/test_fingerprint_parity.py``); use ``False`` only when
                                debugging the matcher itself or when chasing a regression in the
                                new path.

                                .. deprecated::
                                    ``use_fingerprint=False`` is deprecated and will be
                                    **removed in v2.0.0**. The legacy 6-level filter is
                                    superseded by the fingerprint-based path; passing ``False``
                                    emits a ``DeprecationWarning``. Omit the parameter (or pass
                                    ``True``) to silence the warning.
        :type use_fingerprint: bool
        :param date_order: How to read a numeric date that several patterns read differently
                           (``05/06/2022``): ``"DMY"`` (day first), ``"MDY"`` (month first) or
                           ``"YMD"``. The patterns of that order win over the others that consume
                           the same text. None (default) keeps the built-in preference (day first).
                           Can be overridden per call.
        :type date_order: str|None
        :raises TypeError: if ``pivot_year`` is a bool or not an integer.
        :raises ValueError: if ``date_order`` is not one of the values above.
        """
        # ``bool`` is an ``int`` subclass, so ``pivot_year=True`` would silently
        # mean pivot year 1. Reject it along with non-integers.
        if pivot_year is not None and (
                isinstance(pivot_year, bool) or not isinstance(pivot_year, numbers.Integral)):
            raise TypeError(
                "pivot_year must be a 4-digit year such as 1968, or None; "
                f"got {pivot_year!r}")
        # ``use_fingerprint=False`` is deprecated since ``1.0.15`` and will be
        # removed in ``v2.0.0``. Emit a warning when the caller explicitly
        # opts in to the legacy 6-level filter so downstream code has a
        # release cycle to migrate.
        if use_fingerprint is False:
            warnings.warn(
                "use_fingerprint=False is deprecated; the legacy 6-level "
                "filter will be removed in v2.0.0. Omit the parameter (or "
                "pass True) to use the fingerprint-based filter.",
                DeprecationWarning,
                stacklevel=2,
            )
        self._date_order = _check_date_order(date_order)
        # Filter patterns by language if languages parameter is provided
        if languages is not None:
            patterns = get_patterns_for_languages(languages)

        # Copy the pattern dicts so per-instance generation never mutates the
        # shared module-level lists (ALL_PATTERNS / PATTERNS_BY_LANGUAGE entries).
        self.patterns = [dict(p) for p in patterns]
        self._pivot_year = pivot_year
        self._tz_aware = tz_aware
        # Remember the user's language allow-list (normalized to a set) so that
        # automatic language detection in the filter pipeline can never narrow the
        # candidate set below what the caller explicitly requested. Fixes the
        # regression where a shared month name (e.g. German/Dutch "Juli") caused
        # a requested language's patterns to be dropped.
        self._language_allowlist: set[str] | None = None
        if languages is not None:
            if isinstance(languages, str):
                self._language_allowlist = {languages}
            else:
                self._language_allowlist = set(languages)
        self._current_year = datetime.datetime.now().year
        self._year_refresh_interval = 3600  # seconds
        self._next_year_refresh = time.monotonic() + self._year_refresh_interval
        if generate:
            self.__generate(base_only)
        # Generation order; breaks priority ties in ``_match_candidates``.
        self._pattern_rank = {p["key"]: i for i, p in enumerate(self.patterns)}
        # Filled on first use by ``_match_candidates``, keyed by the grammar's
        # ``id``: what each grammar needs from a text (see ``_grammar_needs``)
        # and the grammar wrapped to report where its match starts and ends.
        self._needs_cache: dict[int, tuple[Any, _GrammarNeeds]] = {}
        self._anchored_grammars: dict[int, tuple[Any, Located]] = {}
        # Fingerprint indexes over the patterns of a ``languages=`` hint (and
        # the language-neutral ones), built on first use per set of languages.
        self._language_indexes: dict[frozenset, dict] = {}
        self._language_indexes_source: Union[list[dict], None] = None
        # Results of the fingerprint walk by text fingerprint; see
        # ``_filter_patterns_fingerprint``.
        self._walk_cache: dict[tuple, tuple[dict, tuple]] = {}
        self._build_length_index()
        self._build_separator_index()
        self._build_year_format_index()
        self._build_language_index()
        # Per-instance fingerprint index — keyed by the same tuple as the
        # module-level ``_PATTERN_FINGERPRINTS`` but built from ``self.patterns``
        # so generated variants (suffix :time_N, :t_right, etc.) are included.
        # Built unconditionally so the index is always available; the routing
        # decision in ``_iter_matches`` reads ``self.use_fingerprint`` to pick
        # between the legacy and fingerprint paths.
        self._build_fingerprint_index()
        self.cachedpats: Union[list[dict], None] = None
        # Fingerprint index over ``cachedpats`` and the list it was built from;
        # see ``_session_fingerprint_index``.
        self._session_fingerprints: dict = {}
        self._session_fingerprints_source: Union[list[dict], None] = None
        self.ind: list[Any] = []
        # When ``True``, ``match()``/``match_all()``/``parse()`` route through the
        # single-walk fingerprint-based filter (``_filter_patterns_fingerprint``)
        # instead of the 6-level filter (``_filter_patterns_hierarchical``).
        # Default ``True`` since ``1.0.14``; ``False`` (deprecated) keeps the
        # legacy pipeline reachable for debugging.
        self.use_fingerprint = use_fingerprint

    def __matchPrefix(self, text):
        """
        Wrapper for matchPrefix function that filters patterns based on text prefix.
        Accuracy-first implementation - returns comprehensive pattern sets to avoid
        missing valid dates due to overly restrictive filtering.
        :param text: text with date to match (typically first 6 characters)
        :return: list of pattern basekeys to run against
        """
        return matchPrefix(text)

    def start_session(self, cached_p: Union[list[str], set[str]]) -> None:
        cached_set = set(cached_p) if not isinstance(cached_p, set) else cached_p
        self.cachedpats = [x for x in self.patterns if x["key"] in cached_set]
        # Build the session's fingerprint index now, not on the first parse.
        self._session_fingerprint_index()

    def end_session(self) -> None:
        self.cachedpats = None
        self._session_fingerprints = {}
        self._session_fingerprints_source = None

    def startSession(self, cached_p):
        """Deprecated alias of :meth:`start_session`."""
        warnings.warn(
            "startSession() is deprecated, use start_session() instead",
            DeprecationWarning, stacklevel=2,
        )
        self.start_session(cached_p)

    def endSession(self):
        """Deprecated alias of :meth:`end_session`."""
        warnings.warn(
            "endSession() is deprecated, use end_session() instead",
            DeprecationWarning, stacklevel=2,
        )
        self.end_session()

    def __generate(self, base_only=False):
        """Generates dates patterns"""
        base = []
        texted = []
        for pat in self.patterns:
            # Read-only against the source pattern: ``required_chars`` was
            # already stamped by ``annotate_patterns`` at import time.
            pass

            # A word the pattern's language writes before the time ("в" in
            # "4 Сентября 2020 в 04:06") is accepted in the time variants; it
            # widens their maximum length by the word and its space. A numeric
            # date has no language and accepts the words of every language.
            language = pat.get("language")
            prefixes = (TIME_PREFIXES_BY_LANGUAGE.get(language) if language is not None
                        else ALL_TIME_PREFIXES)
            if prefixes:
                time_prefix = PpOptional(one_of(list(prefixes))).suppress()
                prefix_len = max(len(word) for word in prefixes) + 1
            else:
                time_prefix = None
                prefix_len = 0

            def time_variant(suffix, grammar, min_add, max_add, time_format, pat=pat):
                """Return a copy of ``pat`` matching ``grammar``, whose length
                bounds exceed the date's by ``min_add`` and ``max_add``."""
                data = {**pat}
                data["basekey"] = data["key"]
                data["key"] += suffix
                data["right"] = True
                data["pattern"] = grammar
                data["time_format"] = time_format
                data["length"] = {
                    "min": data["length"]["min"] + min_add,
                    "max": data["length"]["max"] + max_add,
                }
                # Preserve character set metadata
                if "required_chars" in pat:
                    data["required_chars"] = pat["required_chars"]
                return data

            # Lengths after the date: a separator with its spaces (" | ") is up
            # to 3 characters, an optional zone up to 10 (" GMT+03:00").
            # HH:MM or HHhMM ("14h30", "14 h 30" is 7 characters), separated
            # by ",", "|" or the ISO "T".
            base.append(time_variant(
                ":time_1",
                _append(pat["pattern"] + PpOptional(one_of([",", "|", "T"])).suppress(),
                        time_prefix) + BASE_TIME_PATTERNS["pat:time:clock"],
                5, 3 + 7 + 10 + prefix_len, "%H:%M"))
            # HH:MM:SS adds 9 chars (eight and one separating space); the
            # optional zone adds up to 10 more. Without room for it,
            # offset-carrying timestamps never fit this variant and silently
            # fell back to HH:MM (seconds dropped).
            base.append(time_variant(
                ":time_2",
                _append(pat["pattern"] + PpOptional(one_of([",", "|", "T"])).suppress(),
                        time_prefix) + BASE_TIME_PATTERNS["pat:time:full"],
                9, 3 + 8 + 10 + prefix_len, "%H:%M:%S"))
            base.append(time_variant(
                ":time_3",
                _append(pat["pattern"], time_prefix) +
                PpOptional(Literal("[")).suppress() +
                BASE_TIME_PATTERNS["pat:time:minutes"] +
                PpOptional(Literal("]")).suppress(),
                7, 10 + prefix_len, "%H:%M"))
            # 12-hour clock: "3 PM", " 12:45:00 p.m." is up to 13 characters.
            base.append(time_variant(
                ":time_4",
                _append(pat["pattern"] + PpOptional(one_of([",", "|"])).suppress(),
                        time_prefix) + BASE_TIME_PATTERNS["pat:time:clock_ampm"],
                4, 3 + 13 + 10 + prefix_len, "%I:%M %p"))
            # The time before the date: "12:30, 5 мая 2022", "14:30 | 5 May 2022".
            base.append(time_variant(
                ":time_left",
                BASE_TIME_PATTERNS["pat:time:any"] +
                PpOptional(one_of([",", "|", "-"])).suppress() + pat["pattern"],
                4, 13 + 10 + 3, "%H:%M"))

            data = {**pat}
            data["pattern"] = data["pattern"]
            data["right"] = True
            data["basekey"] = data["key"]
            # Preserve character set metadata
            if "required_chars" in pat:
                data["required_chars"] = pat["required_chars"]
            base.append(data)

        if not base_only:
            for pat in base:
                # Right: the date followed by any text. The trailing text is
                # left unconsumed (parse_string accepts a prefix match), so the
                # match end marks where the date stops and match() can compare
                # it with the other candidates'.
                data = {**pat}
                data["key"] += ":t_right"
                data["pattern"] = (
                    lineStart + data["pattern"] +
                    PpOptional(one_of([",", "|", ":", ")"])).suppress())
                data["length"] = {
                    "min": data["length"]["min"] + 1,
                    "max": data["length"]["max"] + 90,
                }
                # Preserve character set metadata
                if "required_chars" in pat:
                    data["required_chars"] = pat["required_chars"]
                texted.append(data)

            base.extend(texted)
        self.patterns = base

    def _infer_char_sets(self, pattern):
        """Infer required character sets from pattern metadata.

        Thin wrapper around ``qddate.patterns._infer_required_chars`` kept for
        back-compat with callers who read this method directly.
        """
        return set(_infer_required_chars(pattern))

    def _build_length_index(self):
        """Pre-index patterns by length ranges for faster filtering"""
        self._patterns_by_length = {}
        for p in self.patterns:
            min_len = p["length"]["min"]
            max_len = p["length"]["max"]
            for length in range(min_len, max_len + 1):
                if length not in self._patterns_by_length:
                    self._patterns_by_length[length] = []
                self._patterns_by_length[length].append(p)

    def _build_separator_index(self):
        """Pre-index patterns by separator types for faster filtering"""
        self._patterns_by_separator = {
            'slash': [],      # Patterns using /
            'dot': [],        # Patterns using .
            'dash': [],       # Patterns using -
            'space': [],      # Patterns using spaces
            'none': [],       # Patterns with no separators (like yyyymmdd)
            'mixed': []       # Patterns with multiple separator types
        }

        for p in self.patterns:
            # Read the authoritative separator (stamped from _PATTERN_METADATA);
            # resolves generated variants via basekey. The old substring ladder is
            # gone — adding/renaming a pattern no longer risks mis-bucketing it.
            sep = _pattern_separator(p)
            self._patterns_by_separator[sep].append(p)

    def _detect_separators(self, text):
        """Quickly detect separator types in text.

        :param text: Input string to scan
        :type text: str
        :return: Set of detected separator types
        :rtype: set
        """
        if not text:
            return set()

        separators = set()
        # Check first 20 chars for efficiency
        scan_len = min(20, len(text))
        for i in range(scan_len):
            char = text[i]
            if char == '/':
                separators.add('slash')
            elif char == '.':
                separators.add('dot')
            elif char == '-':
                separators.add('dash')
            elif char == ' ':
                separators.add('space')

        # If no separators found and text is mostly digits, it might be 'none'
        if not separators and text and text[0].isdigit():
            # Check if it's a compact format like yyyymmdd or ddmmyyyy
            if len(text) >= 8 and all(c.isdigit() for c in text[:8]):
                separators.add('none')
            else:
                # Default to mixed if we can't determine
                separators.add('mixed')
        elif not separators:
            separators.add('mixed')

        return separators

    def _build_fingerprint_index(self) -> None:
        """Pre-index patterns by their (length, chars, separator, language, year_format) fingerprint.

        Built per-instance so generated variants (suffix ``:time_N``,
        ``:t_right`` etc.) are included — the module-level
        ``qddate.patterns.fingerprint._PATTERN_FINGERPRINTS`` only carries
        the 134 base patterns and would miss them. The result is a dict
        from ``FingerprintKey`` to a list of pattern dicts; ``_filter_patterns_fingerprint``
        uses ``set`` arithmetic on the keys to compute intersections.
        """
        self._pattern_fingerprints = _index_by_fingerprint(self.patterns)

    def _session_fingerprint_index(self) -> dict:
        """Return the fingerprint index the fingerprint filter walks.

        Outside a session this is the full per-instance index. Inside one it
        is an index over ``self.cachedpats`` only, so the fingerprint path
        honours ``start_session()`` the way the legacy filter does (session
        patterns are its level-1 set). The session index is rebuilt whenever
        ``cachedpats`` is a different list from the one it was built from,
        which also covers callers that assign ``cachedpats`` directly.
        """
        cached = self.cachedpats
        if cached is None:
            return self._pattern_fingerprints
        if self._session_fingerprints_source is not cached:
            self._session_fingerprints = _index_by_fingerprint(cached)
            self._session_fingerprints_source = cached
        return self._session_fingerprints

    def _build_year_format_index(self):
        """Pre-index patterns by year format requirements for faster filtering"""
        self._patterns_by_year_format = {
            '4digit': [],   # Patterns requiring 4-digit year
            '2digit': [],   # Patterns requiring 2-digit year
            'noyear': [],   # Patterns without year
            'any': []       # Patterns that accept any year format
        }

        for p in self.patterns:
            key = p.get("key", "")
            basekey = p.get("basekey", key)

            if p.get("noyear", False):
                self._patterns_by_year_format['noyear'].append(p)
            elif p.get("yearshort", False):
                self._patterns_by_year_format['2digit'].append(p)
            elif any(x in basekey for x in ["date_iso8601", "date_9", "date_10"]):
                # ISO formats typically use 4-digit years
                self._patterns_by_year_format['4digit'].append(p)
            else:
                # Most patterns can handle both, but default to 4-digit preference
                self._patterns_by_year_format['any'].append(p)

    def _detect_year_format(self, text):
        """Detect if text likely has 2-digit or 4-digit year.

        Optimized version: uses pre-compiled pyparsing patterns.

        :param text: Input string to scan
        :type text: str
        :return: '4digit', '2digit', or 'unknown'
        :rtype: str
        """
        if not text:
            return 'unknown'

        # Look for 4-digit year patterns (more specific, check first)
        # Use pyparsing scan_string for consistency with codebase
        if next(_YEAR_4DIGIT_PATTERN.scan_string(text), None) is not None:
            return '4digit'

        # Look for 2-digit year patterns using pyparsing
        if next(_YEAR_2DIGIT_PATTERN.scan_string(text), None) is not None:
            return '2digit'

        return 'unknown'

    def _language_claims(self, text):
        """Return every language whose month names occur in ``text``.

        Languages come in detection precedence order. When a month name is
        shared (German/Dutch "Juni", German/French "Mai", Russian/Bulgarian
        "Август") and a weekday name belongs to exactly one claiming language,
        only that language is returned.

        :param text: Input string to analyze
        :type text: str
        :return: List of language codes (empty when no month name is found)
        :rtype: list
        """
        if not text:
            return []
        return _month_claims(text, scan_char_sets(text))

    def _detect_language(self, text):
        """Detect language from text using character sets and month name detection.

        Returns the first language of :meth:`_language_claims` (``['ru', 'bg']``
        for Cyrillic text without a Russian or Ukrainian month name), so a
        shared month name still narrows the filters to one language;
        ``_iter_matches`` retries without the language filter when that
        language finds nothing.

        :param text: Input string to analyze
        :type text: str
        :return: List of possible language codes, or None if unknown
        :rtype: list|None
        """
        if not text:
            return None

        char_sets = scan_char_sets(text)
        claims = _month_claims(text, char_sets)
        if CHAR_SET_CYRILLIC in char_sets:
            if not claims or claims == ['bg']:
                # Could be Russian or Bulgarian
                return ['ru', 'bg']
            return claims[:1]
        # If no specific language detected, return None
        # (let other filters handle it)
        return claims[:1] or None

    def _build_language_index(self):
        """Pre-index patterns by language for faster filtering.

        Reads the authoritative ``language`` field (stamped from
        ``_PATTERN_METADATA``) rather than re-deriving it from key substrings.
        Generated variants inherit the base pattern's language via ``basekey``.
        """
        self._patterns_by_language = {}

        for p in self.patterns:
            lang = _pattern_language(p)
            if lang:
                self._patterns_by_language.setdefault(lang, []).append(p)

    def _filter_patterns_hierarchical(self, text, n, noprefix=False, allow_no_year=True,
                                       nocharsetfilter=False, noseparatorfilter=False,
                                       noyearformatfilter=False, nolanguagefilter=False,
                                       allowlist=None):
        """Apply multiple filters in optimal order for maximum efficiency.

        Filters are applied in order from cheapest/most selective to more expensive:
        1. Length filter (cheapest, most selective)
        2. Character set filter (cheap, very selective)
        3. Separator filter (cheap, selective)
        4. Year format filter (cheap)
        5. Prefix filter (existing, most selective)

        :param text: Input text to match
        :type text: str
        :param n: Length of text
        :type n: int
        :param noprefix: If True, skip prefix filtering
        :type noprefix: bool
        :param allow_no_year: If True, patterns with the ``noyear`` flag are
                              eligible to match. If False, those patterns are
                              excluded.
        :type allow_no_year: bool
        :param nocharsetfilter: If True, skip character set filtering
        :type nocharsetfilter: bool
        :param noseparatorfilter: If True, skip separator filtering
        :type noseparatorfilter: bool
        :param noyearformatfilter: If True, skip year format filtering
        :type noyearformatfilter: bool
        :param nolanguagefilter: If True, skip language filtering
        :type nolanguagefilter: bool
        :param allowlist: Languages detection may not narrow below; defaults to
                          the constructor's ``languages=``
        :type allowlist: set|None
        :return: Filtered list of patterns, or None if no patterns remain
        :rtype: list|None
        """
        if allowlist is None:
            allowlist = self._language_allowlist
        # Level 1: Length filter (cheapest, most selective)
        if self.cachedpats is not None:
            pats = self.cachedpats
        else:
            if hasattr(self, '_patterns_by_length'):
                pats = self._patterns_by_length.get(n, [])
            else:
                pats = self.patterns

        if not pats:
            return None

        # Level 2: Character set filter (cheap, very selective)
        if n > 5 and not noprefix and not nocharsetfilter:
            text_char_sets = scan_char_sets(text)
            compatible_patterns = []
            for p in pats:
                required_chars = p.get("required_chars")
                if not required_chars:
                    compatible_patterns.append(p)
                    continue

                # Early exit: check if required character sets are present
                required_cyrillic = CHAR_SET_CYRILLIC in required_chars
                if required_cyrillic and CHAR_SET_CYRILLIC not in text_char_sets:
                    continue

                required_accented = CHAR_SET_ACCENTED in required_chars
                has_latin = CHAR_SET_LATIN in text_char_sets
                has_accented = CHAR_SET_ACCENTED in text_char_sets
                if required_accented and not has_accented and not has_latin:
                    continue

                # Use set operations directly instead of copying
                # Check if required chars (with accented->latin substitution) are subset of text chars
                if CHAR_SET_ACCENTED in required_chars and has_latin:
                    # Create adjusted set without copying
                    if required_chars - {CHAR_SET_ACCENTED} | {CHAR_SET_LATIN} <= text_char_sets:
                        compatible_patterns.append(p)
                else:
                    if required_chars <= text_char_sets:
                        compatible_patterns.append(p)

            if compatible_patterns:
                pats = compatible_patterns
            else:
                return None

        # Level 3: Separator filter (cheap, selective)
        if n > 0 and not noseparatorfilter and hasattr(self, '_patterns_by_separator'):
            separators = self._detect_separators(text)
            if separators:
                separator_basekeys = set()
                for sep in separators:
                    for p in self._patterns_by_separator.get(sep, []):
                        basekey = p.get("basekey", p.get("key", ""))
                        separator_basekeys.add(basekey)

                # Patterns that accept multiple separator types (e.g., date_1, date_8, date_3
                # now accept both / and space). Include slash and mixed patterns
                # when space is detected (since patterns now accept both)
                if 'space' in separators:
                    # Combine both checks in one pass for efficiency
                    space_compatible_patterns = []
                    space_compatible_patterns.extend(self._patterns_by_separator.get('slash', []))
                    space_compatible_patterns.extend(self._patterns_by_separator.get('mixed', []))
                    for p in space_compatible_patterns:
                        basekey = p.get("basekey", p.get("key", ""))
                        # Include patterns that can accept spaces (date_1, date_8, date_3)
                        if any(x in basekey for x in ["date_1", "date_8", "date_3"]):
                            separator_basekeys.add(basekey)

                has_text = any(c.isalpha() for c in text)

                if separator_basekeys:
                    filtered_pats = []
                    for p in pats:
                        basekey = p.get("basekey", p.get("key", ""))
                        if basekey in separator_basekeys:
                            filtered_pats.append(p)
                        elif has_text and any(
                            token in basekey
                            for token in [
                                "eng", "rus", "fr", "de", "es", "it", "pt", "bg",
                                "cz", "pl", "tr", "nl", "ro", "weekday", "rare",
                                "uk",
                            ]
                        ):
                            if 'space' in separators or 'mixed' in separators:
                                filtered_pats.append(p)
                    pats = filtered_pats
                else:
                    pats = []

            if not pats:
                return None

        # Level 4: Language filter (after character sets, before separators)
        # Only apply if we have high confidence (single language detected with month names)
        if n > 5 and not nolanguagefilter and hasattr(self, '_patterns_by_language'):
            detected_languages = self._detect_language(text)
            # When the caller supplied a languages= allow-list, intersect the
            # detected set with it so we never drop a language the caller requested.
            # (This is what fixes the German "Juli" -> detected as Dutch -> German
            # patterns dropped regression: Dutch is filtered out by the allow-list,
            # leaving detection with no high-confidence single language, so we skip
            # the narrowing instead of discarding valid candidates.)
            if allowlist is not None and detected_languages:
                detected_languages = [
                    lang for lang in detected_languages if lang in allowlist
                ]
            # Only filter if we detected exactly one language (high confidence)
            # Multiple languages or None means we're not confident, so don't filter
            if detected_languages and len(detected_languages) == 1:
                lang = detected_languages[0]
                language_pats = []
                language_pat_keys = set()
                for p in self._patterns_by_language.get(lang, []):
                    pat_key = p.get("key")
                    if pat_key not in language_pat_keys:
                        language_pats.append(p)
                        language_pat_keys.add(pat_key)

                if language_pat_keys:
                    pats = [p for p in pats if p.get("key") in language_pat_keys]
                else:
                    pats = []

            if not pats:
                return None

        # Level 5: Year format filter (cheap)
        if n > 0 and not noyearformatfilter and hasattr(self, '_patterns_by_year_format'):
            year_format = self._detect_year_format(text)
            if year_format != 'unknown':
                year_pats = []
                year_pat_keys = set()
                # Include patterns matching detected format
                buckets = [year_format, 'any']
                # No-year patterns must stay reachable: a short text like "05.12"
                # is detected as '2digit' (the ".12" tail looks like a short year),
                # so excluding 'noyear' here made them impossible to match. Only a
                # detected 4-digit year rules them out.
                if year_format != '4digit':
                    buckets.append('noyear')
                for bucket in buckets:
                    for p in self._patterns_by_year_format.get(bucket, []):
                        pat_key = p.get("key")
                        if pat_key not in year_pat_keys:
                            year_pats.append(p)
                            year_pat_keys.add(pat_key)

                if year_pat_keys:
                    pats = [p for p in pats if p.get("key") in year_pat_keys]
                else:
                    pats = []

            if not pats:
                return None

        # Level 6: Prefix filter (existing, most selective)
        if n > 5 and not noprefix:
            basekeys_list = self.__matchPrefix(text[:6])
            basekeys = set(basekeys_list) if basekeys_list else set()
            if basekeys:
                pats = [p for p in pats if p.get("basekey") in basekeys or not p.get("right", False)]

        return pats if pats else None

    def _filter_patterns_fingerprint(self, text, n, noprefix=False, allow_no_year=True,
                                     nocharsetfilter=False, noseparatorfilter=False,
                                     noyearformatfilter=False, nolanguagefilter=False,
                                     languages=None):
        """Single-walk fingerprint-based candidate selection.

        Mirrors ``_filter_patterns_hierarchical`` (length → charset → separator →
        language → year_format → prefix) but collapses the first five levels into
        one intersection over the precomputed ``qddate.patterns.fingerprint.
        _PATTERN_FINGERPRINTS`` index via :func:`candidate_keys_for`. The prefix
        filter (``__matchPrefix``) is kept as the final gate because it depends
        on the candidate set and the prefix index, not on text-fingerprint
        dimensions.

        During a session (:meth:`start_session`) only the session's patterns
        are candidates, as on the legacy path.

        This is the default path since ``1.0.14``; the legacy pipeline is only
        reachable through the deprecated ``use_fingerprint=False``. The result
        is a **superset-or-equal** of the legacy pipeline's candidate set under
        every combination of filter toggles, and both paths yield the same
        matches (``tests/test_fingerprint_parity.py`` locks both properties).

        Each ``no*filter`` toggle skips its dimension entirely, exactly as the
        matching legacy level is skipped, so disabling a filter can only widen
        the candidate set.

        :param text: Input text to match.
        :type text: str
        :param n: Length of text (``len(text)``).
        :type n: int
        :param noprefix: If True, skip the prefix filter and, as the legacy
                         pipeline does, the character-set filter.
        :type noprefix: bool
        :param allow_no_year: Currently a no-op for parity; the year-format
                              filter inside ``candidate_keys_for`` already keeps
                              ``noyear`` patterns when the detected format isn't
                              ``"4digit"``.
        :type allow_no_year: bool
        :param nocharsetfilter: If True, skip the character-set filter.
        :type nocharsetfilter: bool
        :param noseparatorfilter: If True, skip the separator filter.
        :type noseparatorfilter: bool
        :param noyearformatfilter: If True, skip the year-format filter.
        :type noyearformatfilter: bool
        :param nolanguagefilter: If True, skip the language filter.
        :type nolanguagefilter: bool
        :param languages: Only patterns of these languages and the
                          language-neutral ones are candidates (a ``languages=``
                          hint), walked through an index cached per set.
        :type languages: frozenset|None
        :return: Filtered list of patterns, or None if no patterns remain.
        :rtype: list|None
        """
        # Local imports to avoid a circular import (qdparser imports patterns
        # at module top, fingerprint re-imports from there). This is also why
        # the helper is referenced via ``from .patterns.fingerprint import ...``
        # lazily inside the method.
        from .patterns.fingerprint import (
            CHAR_SET_ACCENTED,
            CHAR_SET_LATIN,
        )

        # A disabled dimension is skipped, not matched against a placeholder:
        # an empty text charset or a ``{"mixed"}`` separator would *narrow*
        # the candidate set (``fp_chars <= frozenset()`` rejects every pattern
        # that needs a character class). The legacy levels 2 and 4 also skip
        # the charset filter under ``noprefix`` and both filters for texts of
        # five characters or fewer; mirror that, so a short pattern in another
        # script ("5 мая") stays a candidate for "05.12" as it does there.
        allowlist = self._language_allowlist if languages is None else languages
        check_chars = n > 5 and not noprefix and not nocharsetfilter
        check_separator = not noseparatorfilter
        text_char_sets = scan_char_sets(text) if check_chars else frozenset()
        separators = self._detect_separators(text) if check_separator else set()
        if nolanguagefilter or n <= 5:
            detected_languages: list[str] = []
        else:
            detected_languages = self._detect_language(text)
            if allowlist is not None and detected_languages:
                # Intersection with the caller's allow-list (German "Juli"
                # regression fix): when the caller forced a specific
                # language, detection must not narrow below it.
                detected_languages = [
                    lang for lang in detected_languages
                    if lang in allowlist
                ]

        detected_language = (
            detected_languages[0]
            if detected_languages and len(detected_languages) == 1
            else None
        )
        year_format = (
            self._detect_year_format(text)
            if not noyearformatfilter
            else "unknown"
        )

        # ``separators`` is a set (``{'slash', 'dot', ...}``). The legacy
        # pipeline iterates the full set when looking up the separator
        # bucket; a single-separator check would drop patterns whose
        # separator matches a *different* detected separator in the same
        # text (e.g. ``"17 Marca 2018 r."`` has both space and dot).
        detected_separators = frozenset(separators) if separators else frozenset({"mixed"})

        text_has_letters = any(c.isalpha() for c in text)

        # Charset match (mirrors ``candidate_keys_for``'s ``chars_match``).
        def _chars_match(fp_chars) -> bool:
            if not fp_chars:
                return True
            if fp_chars <= text_char_sets:
                return True
            if (
                CHAR_SET_ACCENTED in fp_chars
                and CHAR_SET_LATIN in text_char_sets
                and (fp_chars - {CHAR_SET_ACCENTED}) <= text_char_sets
            ):
                return True
            return False

        # Separator match: pass if ``fp_sep`` is "mixed" (wildcard), or
        # matches any detected separator, OR the legacy "language tokens
        # survive ambiguous separator" rule applies (text has letters
        # AND a space/mixed separator is detected AND the pattern has a
        # language tag).
        def _sep_match(fp_sep: str, fp_lang) -> bool:
            if fp_sep == "mixed" or fp_sep in detected_separators:
                return True
            if (
                text_has_letters
                and fp_lang is not None
                and (detected_separators & {"space", "mixed"})
            ):
                return True
            return False

        # Slash-dominant date basekeys ("date_1", "date_8", "date_3") —
        # when detected is "space", these are admitted regardless of
        # their own separator (the historical "space also accepts
        # slash-style dates" rule).
        _SPACE_COMPATIBLE_BASEKEYS = frozenset({"date_1", "date_8", "date_3"})

        def _space_compat_basekey(basekey: str) -> bool:
            if "space" not in detected_separators:
                return False
            return any(tok in basekey for tok in _SPACE_COMPATIBLE_BASEKEYS)

        # Language match (with allow-list and "no high-confidence detection"
        # wildcard). When ``_detect_language`` returns zero or multiple
        # languages, the legacy pipeline SKIPS the language filter
        # entirely — every language's patterns stay in. Mirror that by
        # returning True for any language when ``detected_language is None``.
        def _lang_match(fp_lang) -> bool:
            if fp_lang is None:
                return True
            if detected_language is None:
                # No high-confidence detection — admit every language.
                return True
            if fp_lang == detected_language:
                return True
            if allowlist is not None and fp_lang in allowlist:
                return True
            return False

        # Year-format match (mirrors ``candidate_keys_for``'s ``year_match``).
        def _year_match(fp_year: str) -> bool:
            if fp_year == "any":
                return True
            if year_format == "unknown":
                return True
            if year_format == "4digit":
                return fp_year == "4digit"
            if year_format == "2digit":
                return fp_year in ("2digit", "noyear")
            if year_format == "noyear":
                return fp_year in ("noyear", "2digit")
            return False

        # Single-walk intersection over the per-instance fingerprint index
        # (restricted to the session's patterns while a session is active).
        # Includes generated variants (suffix :time_N, :t_right) that the
        # module-level ``_PATTERN_FINGERPRINTS`` does not carry.
        #
        # The slash-dominant widening (space-detected + basekey in
        # ``date_1``/``date_8``/``date_3``) is applied **per-pattern** after
        # the bucket-level checks (length, chars, language, year_format)
        # pass: a bucket whose fingerprint's separator doesn't match the
        # detected separator is rejected at the bucket level, but the
        # ``date_1``/``date_8``/``date_3`` patterns are admissible from
        # within any matching bucket whose own separator would have
        # excluded them. Concretely: a fingerprint with ``separator="slash"``
        # is skipped at the bucket level when detected is ``"space"`` —
        # but a pattern whose basekey is ``date_1``/``date_8``/``date_3``
        # gets a free pass via ``_space_compat_basekey``.
        #
        # The walk depends only on what the text's fingerprint says, so its
        # result is kept per fingerprint: text nodes of a page mostly share
        # a few, and the walk grows with the number of generated variants.
        index = self._candidate_index(languages)
        cache_key = (id(index), n, frozenset(text_char_sets), detected_separators,
                     check_separator, detected_language, year_format,
                     text_has_letters, None if allowlist is None else frozenset(allowlist))
        cached = self._walk_cache.get(cache_key)
        if cached is not None and cached[0] is index:
            pats = list(cached[1])
        else:
            pats = []
            for fp, bucket in index.items():
                if fp.length_min > n or fp.length_max < n:
                    continue
                if check_chars and not _chars_match(fp.chars):
                    continue
                if not _lang_match(fp.language):
                    continue
                if not _year_match(fp.year_format):
                    continue
                if not check_separator or _sep_match(fp.separator, fp.language):
                    pats.extend(bucket)
                    continue
                for p in bucket:
                    if _space_compat_basekey(p.get("basekey", p.get("key", ""))):
                        pats.append(p)
            if len(self._walk_cache) >= _WALK_CACHE_SIZE:
                self._walk_cache.clear()
            self._walk_cache[cache_key] = (index, tuple(pats))

        if not pats:
            return None

        # Final gate: prefix filter (level 6). Same logic as the legacy
        # pipeline: when ``n > 5`` and prefix is enabled, keep patterns
        # whose ``basekey`` is in the prefix set, OR patterns without the
        # ``right`` flag (left-aligned only).
        if n > 5 and not noprefix:
            basekeys_list = self.__matchPrefix(text[:6])
            basekeys = set(basekeys_list) if basekeys_list else set()
            if basekeys:
                pats = [
                    p for p in pats
                    if p.get("basekey") in basekeys or not p.get("right", False)
                ]

        return pats if pats else None

    def _calculate_pattern_priority(self, pattern, text, date_order=None):
        """Calculate priority score for pattern based on text characteristics.

        Higher scores indicate patterns more likely to match. Patterns are sorted
        by priority (descending) to try most promising patterns first.

        :param pattern: Pattern dictionary
        :type pattern: dict
        :param text: Input text to match
        :type text: str
        :param date_order: Validated ``date_order`` ("DMY", "MDY", "YMD" or
                           None); the numeric patterns of that order get a
                           bonus larger than any other difference
        :type date_order: str|None
        :return: Integer priority score (higher = more likely)
        :rtype: int
        """
        score = 0
        key = pattern.get("key", "")
        basekey = pattern.get("basekey", key)
        n = len(text)

        # Higher priority for common patterns (exact basekey tiers; the former
        # substring checks let "date_1" silently match "date_10").
        if basekey in _PRIORITY_TIER_COMMON:
            score += 100
        elif basekey in _PRIORITY_TIER_ISO:
            score += 80
        elif basekey in _PRIORITY_TIER_9:
            score += 75
        elif basekey in _PRIORITY_TIER_MID:
            score += 70
        elif _pattern_language(pattern) is not None:
            # Month-name patterns in any language rank just below the numeric cores.
            score += 60

        # Boost if separator matches (exact basekey sets per separator)
        if '/' in text:
            if basekey in _PRIORITY_SLASH_BOOST:
                score += 20
        elif '.' in text:
            if basekey in _PRIORITY_DOT_BOOST:
                score += 20
        elif '-' in text:
            if basekey in _PRIORITY_DASH_BOOST:
                score += 20
        elif ' ' in text:
            # Month-name patterns (any language) are the likely match for spaced text.
            if _pattern_language(pattern) is not None:
                score += 20

        # Boost if length is exact match (more likely to be correct). Not for
        # ":t_right" variants: their bounds include the trailing text, so the
        # input length says nothing about them, and the bonus let them outrank
        # the plain variant that matches the same text.
        length_min = pattern.get("length", {}).get("min", 0)
        length_max = pattern.get("length", {}).get("max", 0)
        if length_min <= n <= length_max and not key.endswith(":t_right"):
            if n == length_min or n == length_max:
                score += 10
            else:
                score += 5

        # Slight penalty for patterns with noyear (less specific)
        if pattern.get("noyear", False):
            score -= 5

        # Slight penalty for rare patterns
        if "rare" in basekey:
            score -= 10

        if date_order is not None and basekey in _DATE_ORDER_BASEKEYS[date_order]:
            score += _DATE_ORDER_BONUS

        return score

    def _iter_matches(self, text, noprefix=False, allow_no_year=True, nocharsetfilter=False,
                      noseparatorfilter=False, noyearformatfilter=False,
                      nolanguagefilter=False, languages=None, date_order=None, tried=None):
        """Yield ``(priority, end, result)`` for every candidate pattern matching
        ``text`` at position 0, highest priority first. ``end`` is where the
        match stops, not counting trailing whitespace, in ``text`` with tabs
        expanded (pyparsing matches against ``text.expandtabs()``).

        Shared engine behind :meth:`match` and :meth:`match_all`. Components are
        sanity-checked (month/day/hour/minute/second ranges) before yielding.
        ``languages`` (a validated hint) restricts the candidates to those
        languages and the language-neutral patterns; ``date_order`` (validated)
        is passed to :meth:`_calculate_pattern_priority`. Keys of the patterns
        run are added to ``tried``, and patterns already in it are skipped.
        """
        filter_flags = {
            "noprefix": noprefix,
            "allow_no_year": allow_no_year,
            "nocharsetfilter": nocharsetfilter,
            "noseparatorfilter": noseparatorfilter,
            "noyearformatfilter": noyearformatfilter,
        }
        if tried is None:
            tried = set()
        found = False
        pats = self._filter_patterns(text, languages=languages,
                                     nolanguagefilter=nolanguagefilter, **filter_flags)
        for item in self._match_candidates(text, pats, allow_no_year, tried, date_order):
            found = True
            yield item
        if found or nolanguagefilter or len(self._language_claims(text)) < 2:
            return
        # The month name is shared by several languages and the language filter
        # kept only the first one ("30. Mai 1953": French before German). It
        # found nothing, so try the patterns of every language.
        pats = self._filter_patterns(text, languages=languages, nolanguagefilter=True,
                                     **filter_flags)
        yield from self._match_candidates(text, pats, allow_no_year, tried, date_order)

    def _iter_passes(self, text, languages=None, date_order=None, first_only=False, **flags):
        """Yield ``(pass, priority, end, result)`` from :meth:`_iter_matches`.

        Without ``languages`` there is one pass, 0, over all candidates. With
        a ``languages=`` hint, pass 0 covers the patterns of those languages
        and the language-neutral ones, and pass 1 the remaining patterns;
        with ``first_only`` pass 1 runs only when pass 0 yields nothing.
        ``date_order`` None means the parser's own ``date_order``.
        """
        hint = _check_languages(languages)
        order = self._date_order if date_order is None else _check_date_order(date_order)
        tried: set[str] = set()
        found = False
        for number, allowed in enumerate([hint, None] if hint else [None]):
            if found and first_only:
                return
            for priority, end, result in self._iter_matches(
                    text, languages=allowed, date_order=order, tried=tried, **flags):
                found = True
                yield number, priority, end, result

    def _filter_patterns(self, text, languages=None, **flags):
        """Return the candidate patterns for ``text`` (or None) from the active filter.

        With ``languages`` (a validated ``languages=`` hint) only the patterns
        of those languages and the language-neutral ones are returned.
        """
        # Route to the fingerprint-based filter when the constructor flag is set,
        # otherwise fall through to the existing 6-level pipeline. Both paths
        # share the same candidate-set semantics (level 6 prefix + score +
        # component-range validation); the fingerprint path is parity-locked
        # to be a superset-or-equal of the legacy path on every probe string.
        if self.use_fingerprint:
            return self._filter_patterns_fingerprint(text, len(text), languages=languages, **flags)
        pats = self._filter_patterns_hierarchical(text, len(text), allowlist=languages, **flags)
        if pats and languages is not None:
            pats = [p for p in pats if _pattern_language(p) in languages
                    or _pattern_language(p) is None]
        return pats or None

    def _candidate_index(self, languages=None):
        """Return the fingerprint index the fingerprint filter walks.

        The session's index during a session (see
        :meth:`_session_fingerprint_index`), otherwise the full index. With
        ``languages`` it is restricted to the patterns of those languages and
        the language-neutral ones; the restricted index is built once per set
        of languages and kept.
        """
        if languages is None:
            return self._session_fingerprint_index()
        source = self.patterns if self.cachedpats is None else self.cachedpats
        if self._language_indexes_source is not source:
            # A new session (or its end): the cached indexes are stale.
            self._language_indexes = {}
            self._language_indexes_source = source
        index = self._language_indexes.get(languages)
        if index is None:
            index = self._language_indexes[languages] = _index_by_fingerprint([
                p for p in source
                if _pattern_language(p) is None or _pattern_language(p) in languages])
        return index

    def _anchored(self, grammar):
        """Return ``grammar`` wrapped in ``Located``, which reports where the
        match starts and ends (``locn_start``/``locn_end``) and the grammar's
        own results as ``value``."""
        entry = self._anchored_grammars.get(id(grammar))
        if entry is None or entry[0] is not grammar:
            entry = (grammar, Located(grammar))
            self._anchored_grammars[id(grammar)] = entry
        return entry[1]

    def _match_candidates(self, text, pats, allow_no_year, tried, date_order=None):
        """Yield ``(priority, end, result)`` for the patterns in ``pats`` that
        match ``text`` at position 0, highest priority first.

        Keys of the patterns run are added to ``tried``; patterns already in it
        are skipped.
        """
        if not pats:
            return
        n = len(text)
        # ``parse_string`` expands tabs before matching; check what a grammar
        # needs against the same string.
        expanded = text.expandtabs()
        found = {}

        # Cheap checks before ranking: the length bounds, then the character
        # the date starts with and the month or weekday names it contains.
        # Most text that is not a date ("Page 2 of 10") fails them before any
        # grammar runs. Only patterns that cannot match are dropped.
        pats = [
            p for p in pats
            if p["length"]["min"] <= n <= p["length"]["max"]
            and (allow_no_year or not p.get("noyear", False))
            and _may_match(p["pattern"], expanded, self._needs_cache, found)
        ]

        # Sort patterns by priority (try most likely patterns first). Ties
        # keep the generation order: the two filters return candidates in
        # different orders, and both must pick the same pattern.
        rank = self._pattern_rank
        scored = sorted(
            ((self._calculate_pattern_priority(p, text, date_order), p) for p in pats),
            key=lambda item: (-item[0], rank.get(item[1]["key"], len(rank))))

        for _score, p in scored:
            if p["key"] in tried:
                continue
            tried.add(p["key"])
            grammar = p["pattern"]
            # ``scan_string`` skipped the grammar's whitespace characters
            # before a match, so a text starting with one never matched at 0.
            # ``Located`` does not skip them for a grammar that starts with
            # ``LineStart`` (the ``:t_right`` variants); keep that rule.
            if expanded[:1] in grammar.whiteChars:
                continue
            # Parse at position 0 only. ``scan_string`` also tried every later
            # position of a text that does not start with a date, only for the
            # match to be discarded.
            try:
                located = self._anchored(grammar).parse_string(text)
            except ParseBaseException:
                continue
            # Leading whitespace is skipped before the match; the date must
            # start the text.
            if located.locn_start != 0:
                continue
            r, end = located.value, located.locn_end
            if not _values_in_range(r.as_dict()):
                continue
            # An optional element that matches nothing still skips the
            # whitespace before it; that whitespace is not part of the date.
            # ``end`` counts in the expanded text: indexing ``text`` with it
            # raised IndexError for "5\tMay 2022".
            while end > 0 and expanded[end - 1].isspace():
                end -= 1
            yield _score, end, {"values": r, "pattern": p}

    def match(self, text: str, noprefix: bool = False, allow_no_year: bool = True, nocharsetfilter: bool = False,
             noseparatorfilter: bool = False, noyearformatfilter: bool = False,
             nolanguagefilter: bool = False, *, noyear: TOptional[bool] = None,
             languages: Union[str, list[str], None] = None,
             date_order: TOptional[str] = None) -> Union[dict, None]:  # noqa: E501
        """Matches date/datetime string against date patterns and returns pattern and parsed date if matched.
        It's not indeded for common usage, since if successful it returns date as array of numbers and pattern
        that matched this date

        :param text:
            Any human readable string
        :type text: str|unicode
        :param noprefix:
            If set True than doesn't use prefix based date patterns filtering settings
        :type noprefix: bool
        :param allow_no_year:
            If True, includes patterns with the ``noyear`` flag (these cause many
            false positives on bare numbers like ``05.12``). If False, those
            patterns are skipped. Default: True.
        :type allow_no_year: bool
        :param noyear:
            **Deprecated.** Use ``allow_no_year=`` instead.
        :type noyear: bool
        :param nocharsetfilter:
            If set True than doesn't use character set based pattern filtering
        :type nocharsetfilter: bool
        :param noseparatorfilter:
            If set True than doesn't use separator based pattern filtering
        :type noseparatorfilter: bool
        :param noyearformatfilter:
            If set True than doesn't use year format based pattern filtering
        :type noyearformatfilter: bool
        :param nolanguagefilter:
            If set True than doesn't use language based pattern filtering
        :type nolanguagefilter: bool
        :param languages:
            Language code or list of codes to try first (the page language,
            say). The patterns of these languages and the language-neutral
            numeric ones are tried first; only when none of them matches are
            the other patterns of the parser tried. Unlike the constructor's
            ``languages=``, the hint never excludes a pattern. Unknown codes
            raise ``ValueError``.
        :type languages: str|list|None
        :param date_order:
            ``"DMY"``, ``"MDY"`` or ``"YMD"`` for this call; None (default) uses
            the parser's ``date_order``. See :class:`DateParser`.
        :type date_order: str|None


        :return: Returns dicts with `values` as array of representing parsed date and 'pattern'
            with info about matched pattern if successful, else returns None
        :rtype: :class:`dict`."""
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            allow_no_year = noyear
        found = self._match_end(
            text, noprefix=noprefix, allow_no_year=allow_no_year,
            nocharsetfilter=nocharsetfilter, noseparatorfilter=noseparatorfilter,
            noyearformatfilter=noyearformatfilter, nolanguagefilter=nolanguagefilter,
            languages=languages, date_order=date_order)
        return found[1] if found else None

    def _match_end(self, text, **flags):
        """Return ``(end, result)`` of the best match for ``text``, or None.

        ``result`` is what :meth:`match` returns; ``end`` is where the date
        stops in ``text.expandtabs()``, not counting trailing whitespace.
        ``flags`` are the keyword arguments of :meth:`match` except ``noyear``.
        """
        # The match consuming the most input wins (a date with its time over
        # the bare date, HH:MM:SS over HH:MM); priority only breaks ties.
        # Patterns are not anchored at the end, so without this a partial
        # match with a length bonus beat a complete one. Candidates come in
        # priority order: keep the first of each length and stop once one
        # covers the whole text. ``end`` counts in the tab-expanded text.
        # With a ``languages=`` hint, a match from the first pass (the hinted
        # languages) wins over any from the second.
        n = len(text.expandtabs().rstrip())
        best = None
        for _number, _score, end, result in self._iter_passes(text, first_only=True, **flags):
            if best is None or end > best[0]:
                best = (end, result)
                if end >= n:
                    break
        return best

    def match_all(self, text: str, noprefix: bool = False, allow_no_year: bool = True,
                  nocharsetfilter: bool = False, noseparatorfilter: bool = False,
                  noyearformatfilter: bool = False,
                  nolanguagefilter: bool = False, *,
                  noyear: TOptional[bool] = None,
                  languages: Union[str, list[str], None] = None,
                  date_order: TOptional[str] = None) -> list[dict]:
        """Return every distinct match for ``text``, best first.

        Unlike :meth:`match` (which returns a single winner), this surfaces
        ambiguity: ``01/02/2020`` is valid as both D/M/Y and M/D/Y, and scraping
        callers often need to know that instead of silently getting one
        interpretation. Results are deduplicated by base pattern, keeping the
        longest-consuming variant of each, and ordered the way :meth:`match`
        picks: most input consumed first, then priority. With a ``languages=``
        hint, the matches of the hinted languages (and the language-neutral
        patterns) come before all others.

        Accepts the same filter flags as :meth:`match`, and ``languages=`` and
        ``date_order=``. ``noyear=`` is the deprecated alias for
        ``allow_no_year=``.

        :return: list of match dicts (same shape as :meth:`match` results),
                 empty when nothing matches
        :rtype: list
        """
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            allow_no_year = noyear
        # basekey -> (pass, end, position in priority order, result)
        best: dict[str, tuple[int, int, int, dict]] = {}
        for order, (number, _score, end, result) in enumerate(self._iter_passes(
                text, noprefix=noprefix, allow_no_year=allow_no_year,
                nocharsetfilter=nocharsetfilter, noseparatorfilter=noseparatorfilter,
                noyearformatfilter=noyearformatfilter, nolanguagefilter=nolanguagefilter,
                languages=languages, date_order=date_order)):
            p = result["pattern"]
            basekey = p.get("basekey", p.get("key", ""))
            if basekey not in best or end > best[basekey][1]:
                best[basekey] = (number, end, order, result)
        ranked = sorted(best.values(), key=lambda item: (item[0], -item[1], item[2]))
        return [result for _number, _end, _order, result in ranked]

    def parse(self, text: str, noprefix: bool = False, nocharsetfilter: bool = False,
              noseparatorfilter: bool = False, noyearformatfilter: bool = False,
              nolanguagefilter: bool = False, allow_no_year: bool = True,
              *, noyear: TOptional[bool] = None,
              languages: Union[str, list[str], None] = None,
              date_order: TOptional[str] = None,
              reference: TOptional[datetime.datetime] = None,
              prefer: TOptional[str] = None) -> Union[datetime.datetime, None]:
        """Parse date and time from given date string.

        :param text:
            Any human readable string
        :type text: str|unicode
        :param noprefix:
            If set True than doesn't use prefix based date patterns filtering settings
        :type noprefix: bool
        :param nocharsetfilter:
            If set True than doesn't use character set based pattern filtering
        :type nocharsetfilter: bool
        :param noseparatorfilter:
            If set True than doesn't use separator based pattern filtering
        :type noseparatorfilter: bool
        :param noyearformatfilter:
            If set True than doesn't use year format based pattern filtering
        :type noyearformatfilter: bool
        :param nolanguagefilter:
            If set True than doesn't use language based pattern filtering
        :type nolanguagefilter: bool
        :param allow_no_year:
            If True (default) patterns without a year are allowed and the year
            of ``reference`` (the current year by default) is substituted
            (e.g. "05.12"); if False such patterns are skipped.
        :type allow_no_year: bool
        :param noyear:
            **Deprecated.** Use ``allow_no_year=`` instead.
        :type noyear: bool
        :param languages:
            Languages to try first; see :meth:`match`.
        :type languages: str|list|None
        :param date_order:
            ``"DMY"``, ``"MDY"`` or ``"YMD"`` for this call; see :meth:`match`.
        :type date_order: str|None
        :param reference:
            The moment that counts as "now" for a date without a year: its
            year is used. Default: the current time.
        :type reference: datetime.datetime|None
        :param prefer:
            For a date without a year: ``"past"`` moves it to the previous year
            when it would lie more than :data:`NOYEAR_ROLLOVER_GRACE` after
            ``reference`` ("31.12" read on 2 January), ``"future"`` to the next
            year when it would lie more than that before it. None (default)
            keeps the year of ``reference``.
        :type prefer: str|None


        :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
        :rtype: :class:`datetime <datetime.datetime>`."""
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            allow_no_year = noyear
        _check_prefer(prefer)
        res = self.match(text, noprefix=noprefix, allow_no_year=allow_no_year,
                         nocharsetfilter=nocharsetfilter,
                         noseparatorfilter=noseparatorfilter,
                         noyearformatfilter=noyearformatfilter,
                         nolanguagefilter=nolanguagefilter,
                         languages=languages, date_order=date_order)
        if res:
            return self._build_datetime(res, reference=reference, prefer=prefer)
        return None

    def _build_datetime(self, res, reference=None, prefer=None):
        """Convert a ``match()`` result into a :class:`datetime.datetime`.

        Applies the parser's ``pivot_year`` (2-digit years) and ``tz_aware``
        (the parsed timezone, see :func:`parse_timezone`) options, and for a
        date without a year the year of ``reference`` and the ``prefer``
        policy (see :meth:`parse`). Returns None for out-of-range values or
        unexpected result keys instead of raising.
        """
        r = res["values"]
        p = res["pattern"]
        d = {"month": 0, "day": 0, "year": 0}
        no_year = p.get("noyear", False)
        if no_year:
            d["year"] = reference.year if reference is not None else self._get_cached_year()
        tz_offset = None
        for k, v in r.items():
            if k == "timezone":
                # Zone written after the time; not a datetime kwarg.
                tz_offset = v
                continue
            d[k] = int(v)
        # 2-digit-year pivot (opt-in via constructor pivot_year=)
        if self._pivot_year is not None and p.get("yearshort", False) and 0 <= d["year"] <= 99:
            pivot_2digit = self._pivot_year % 100
            d["year"] = 2000 + d["year"] if d["year"] < pivot_2digit else 1900 + d["year"]
        try:
            dt = datetime.datetime(**d)
        except (ValueError, TypeError):
            # Invalid date values (e.g., year 0) or unexpected keys - return None
            return None
        if no_year and prefer is not None:
            dt = _roll_year(dt, reference or datetime.datetime.now(), prefer)
            if dt is None:
                return None
        if tz_offset is not None and self._tz_aware:
            tz = parse_timezone(tz_offset)
            if tz is not None:
                dt = dt.replace(tzinfo=tz)
        return dt

    def match_typed(self, text: str, *, reference: TOptional[datetime.datetime] = None,
                    prefer: TOptional[str] = None, **kwargs: Any) -> Union[DateMatch, None]:
        """Like :meth:`match`, but returns a typed :class:`DateMatch` (or None).

        The datetime is already constructed (honoring ``pivot_year``/``tz_aware``
        and ``reference``/``prefer`` as in :meth:`parse`), and the result
        carries ``pattern_key``, ``language``, ``format``, the original ``raw``
        text, the ``span`` of the date in it, its ``precision``, the written
        ``tzinfo`` and ``has_year``. Accepts the same keyword arguments as
        :meth:`match` (filter flags, ``languages=``, ``date_order=``).
        """
        _check_prefer(prefer)
        noyear = kwargs.pop("noyear", None)
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            kwargs["allow_no_year"] = noyear
        found = self._match_end(text, **kwargs)
        if found is None:
            return None
        end, res = found
        dt = self._build_datetime(res, reference=reference, prefer=prefer)
        if dt is None:
            return None
        p = res["pattern"]
        values = res["values"]
        return DateMatch(
            datetime=dt,
            pattern_key=p["key"],
            language=_pattern_language(p),
            format=p.get("format", ""),
            raw=text,
            span=(0, _original_index(text, end)),
            precision=_precision(values),
            tzinfo=parse_timezone(values.get("timezone")),
            has_year=not p.get("noyear", False),
        )

    def parse_many(self, texts: list[str], **kwargs: Any) -> Iterator[Union[datetime.datetime, None]]:
        """Lazily parse an iterable of date strings.

        Yields one :class:`datetime.datetime` (or None) per input item, reusing the
        indexes built at construction time. Keyword arguments are passed through
        to :meth:`parse`.
        """
        for text in texts:
            yield self.parse(text, **kwargs)

    def format_date(self, dt: datetime.datetime, pattern_key: str) -> str:
        """Format ``dt`` with the format string attached to ``pattern_key``.

        Convenience wrapper around the module-level :func:`format_date` for
        callers that already hold a parser instance. See :meth:`DateMatch.format_date`
        for the inverse direction (re-format a parsed ``DateMatch``).
        """
        return format_date(dt, pattern_key)

    def parse_relative(self, text: str, reference: Optional[datetime.datetime] = None) -> Optional[datetime.datetime]:
        """Resolve ``text`` as a relative-date phrase against ``reference``.

        Supported phrases (English): ``today``, ``yesterday``, ``tomorrow``,
        ``N day(s) ago``, ``(in) N day(s)`` (and the same for weeks/months/years).
        Both digit-form ("3 days ago") and word-form ("three days ago") numbers
        are accepted.

        Supported phrases (Russian): ``сегодня``, ``вчера``, ``завтра``, ``N
        <unit> назад``, ``через N <unit>``.

        Args:
            text: the input string to interpret.
            reference: the anchor time; defaults to ``datetime.now()``. Pass an
                explicit value for deterministic tests or for scraping historic
                content where "today" should mean the article's publish date.

        Returns:
            The resolved ``datetime`` (with the time of ``reference``) or
            ``None`` if ``text`` is not a recognised relative phrase.
        """
        if reference is None:
            reference = datetime.datetime.now()
        return _parse_relative(text, reference)

    def _get_cached_year(self):
        """Return cached current year, refreshing periodically."""
        now = time.monotonic()
        if now >= self._next_year_refresh:
            self._current_year = datetime.datetime.now().year
            self._next_year_refresh = now + self._year_refresh_interval
        return self._current_year


if __name__ == "__main__":
    # Minimal smoke demo. The canonical test runner is `pytest tests/`; this block
    # exists only for a quick `python -m qddate.qdparser` sanity check. It must never
    # reference `r` before assignment or import optional deps unguarded.
    samples = [
        "01.12.2009",
        "2013-01-12",
        "6 Jan 2009",
        "3 Января 2003 года",
        "28. Juli 2015",
        "Thursday, Jun 25, 2026",
        "03 de Julio, 2026",
    ]
    parser = DateParser(generate=True)
    print("Generated patterns:", len(parser.patterns))
    for text in samples:
        print(f"{text!r:32} -> {parser.parse(text)}")

