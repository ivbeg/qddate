#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

import datetime
import re
import time
import warnings
from dataclasses import dataclass
from typing import Any, Iterator, Optional, Union
from typing import Optional as TOptional

from pyparsing import Literal, Regex, Word, lineStart, nums, one_of, restOfLine
from pyparsing import Optional as PpOptional

# Enable packrat parsing for better performance
try:
    from pyparsing import ParserElement
    ParserElement.enable_packrat()
except Exception:
    # Packrat is an optimization; if it is unavailable or fails, fall back to
    # standard parsing rather than crashing on import.
    pass

from .dirty import matchPrefix
from .patterns import (
    _PATTERN_METADATA,
    ALL_PATTERNS,
    BASE_TIME_PATTERNS,
    MONTHS_BY_LANGUAGE,
    _infer_required_chars,
    get_patterns_for_languages,
)
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

# Pre-compiled pyparsing patterns for language detection (compiled once at module level)
# Use Regex within pyparsing for word boundary matching (pyparsing's oneOf doesn't support word boundaries)
# Create regex patterns that match any English/German month with word boundaries
_ENGLISH_MONTH_PATTERN = Regex(r'\b(' + '|'.join(re.escape(m) for m in _ENGLISH_MONTHS) + r')\b')
_GERMAN_MONTH_PATTERN = Regex(r'\b(' + '|'.join(re.escape(m) for m in _GERMAN_MONTHS) + r')\b')

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


@dataclass
class DateMatch:
    """Typed result of a successful date match.

    Returned by :meth:`DateParser.match_typed`. ``.to_dict()`` provides a plain
    mapping for callers that need the old-style shape.

    The ``format_date()`` method is the natural inverse of parsing: it formats
    ``self.datetime`` back into the locale-aware string the parser originally
    matched, so the result round-trips through :meth:`DateParser.parse`.
    """

    datetime: datetime.datetime
    pattern_key: str
    language: TOptional[str]
    format: str
    raw: str

    def to_dict(self) -> dict:
        return {
            "datetime": self.datetime,
            "pattern_key": self.pattern_key,
            "language": self.language,
            "format": self.format,
            "raw": self.raw,
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


class DateParser:
    """Class to use pyparsing-based patterns to parse dates"""

    def __init__(self, generate: bool = True, patterns: list[dict] = ALL_PATTERNS,
                 base_only: bool = False, languages: Union[str, list[str], None] = None,
                 pivot_year: int | None = None, tz_aware: bool = False,
                 use_fingerprint: bool = True) -> None:
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
                          If None (default), 2-digit years are passed through unchanged.
        :type pivot_year: int|None
        :param tz_aware: If True, a parsed ``+HHMM`` timezone offset is attached to the returned datetime
                         (making it timezone-aware). Default False keeps returning naive datetimes.
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
        """
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
        self.ind: list[Any] = []
        # When ``True``, ``match()``/``match_all()``/``parse()`` route through the
        # single-walk fingerprint-based filter (``_filter_patterns_fingerprint``)
        # instead of the 6-level filter (``_filter_patterns_hierarchical``).
        # Default ``False`` preserves the legacy behaviour bit-for-bit; a future
        # round flips the default after parity is locked on the full corpus.
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

    def end_session(self) -> None:
        self.cachedpats = None

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

            data = {**pat}
            data["basekey"] = data["key"]
            data["key"] += ":time_1"
            data["right"] = True
            data["pattern"] = (data["pattern"] +
                               PpOptional(Literal(",")).suppress() +
                               BASE_TIME_PATTERNS["pat:time:minutes"])
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 5,
                "max": data["length"]["max"] + 8,
            }
            # Preserve character set metadata
            if "required_chars" in pat:
                data["required_chars"] = pat["required_chars"]
            base.append(data)

            data = {**pat}
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_2"
            data["pattern"] = (data["pattern"] +
                               PpOptional(one_of([",", "|", "T"])).suppress() +
                               BASE_TIME_PATTERNS["pat:time:full"])
            data["time_format"] = "%H:%M:%S"
            data["length"] = {
                "min": data["length"]["min"] + 9,
                # HH:MM:SS adds 9 chars; the optional "+HHMM" offset adds 5 more.
                # Without the +5, offset-carrying timestamps never fit this
                # variant and silently fell back to HH:MM (seconds dropped).
                "max": data["length"]["max"] + 14,
            }
            # Preserve character set metadata
            if "required_chars" in pat:
                data["required_chars"] = pat["required_chars"]
            base.append(data)

            data = {**pat}
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_3"
            data["pattern"] = (data["pattern"] +
                               PpOptional(Literal("[")).suppress() +
                               BASE_TIME_PATTERNS["pat:time:minutes"] +
                               PpOptional(Literal("]")).suppress())
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 7,
                "max": data["length"]["max"] + 10,
            }
            # Preserve character set metadata
            if "required_chars" in pat:
                data["required_chars"] = pat["required_chars"]
            base.append(data)

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
                # Right
                data = {**pat}
                data["key"] += ":t_right"
                data["pattern"] = (
                    lineStart + data["pattern"] +
                    PpOptional(one_of([",", "|", ":", ")"])).suppress() +
                    restOfLine.suppress())
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

        from .patterns.fingerprint import (
            compute_pattern_fingerprint,
        )

        index: dict = {}
        for p in self.patterns:
            fp = compute_pattern_fingerprint(p)
            index.setdefault(fp, []).append(p)
        self._pattern_fingerprints = index

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
        # Use pyparsing scanString for consistency with codebase
        if next(_YEAR_4DIGIT_PATTERN.scanString(text), None) is not None:
            return '4digit'

        # Look for 2-digit year patterns using pyparsing
        if next(_YEAR_2DIGIT_PATTERN.scanString(text), None) is not None:
            return '2digit'

        return 'unknown'

    def _detect_language(self, text):
        """Detect language from text using character sets and month name detection.

        Optimized version: uses simple 'in' operator instead of regex for faster matching.

        :param text: Input string to analyze
        :type text: str
        :return: List of possible language codes, or None if unknown
        :rtype: list|None
        """
        if not text:
            return None

        char_sets = scan_char_sets(text)
        text_lower = text.lower()
        detected_languages = []

        # Check for Cyrillic languages
        if CHAR_SET_CYRILLIC in char_sets:
            # Use simple 'in' operator - faster than regex for date strings
            if any(month in text_lower for month in _UKRAINIAN_MONTHS):
                detected_languages.append('uk')
                return detected_languages
            if any(month in text_lower for month in _RUSSIAN_MONTHS):
                detected_languages.append('ru')
                # Early exit: high confidence match
                return detected_languages
            else:
                # Could be Russian or Bulgarian
                detected_languages.extend(['ru', 'bg'])
                return detected_languages

        # Check for accented languages with month name detection
        if CHAR_SET_ACCENTED in char_sets or CHAR_SET_LATIN in char_sets:
            # Use simple 'in' operator instead of regex - sufficient for date strings
            # French month names
            if any(month in text_lower for month in _FRENCH_MONTHS):
                detected_languages.append('fr')
                return detected_languages  # Early exit: high confidence

            # Spanish month names
            if any(month in text_lower for month in _SPANISH_MONTHS):
                detected_languages.append('es')
                return detected_languages  # Early exit: high confidence

            # Italian month names
            if any(month in text_lower for month in _ITALIAN_MONTHS):
                detected_languages.append('it')
                return detected_languages  # Early exit: high confidence

            # Portuguese month names
            if any(month in text_lower for month in _PORTUGUESE_MONTHS):
                detected_languages.append('pt')
                return detected_languages  # Early exit: high confidence

            # Czech month names
            if any(month in text_lower for month in _CZECH_MONTHS):
                detected_languages.append('cz')
                return detected_languages  # Early exit: high confidence

            # Polish month names (including genitive forms)
            if any(month in text_lower for month in _POLISH_MONTHS):
                detected_languages.append('pl')
                return detected_languages  # Early exit: high confidence

            # Romanian month names. Keep this after the existing Romance-language
            # checks so an unrestricted parser does not relabel ambiguous "mai".
            if any(month in text_lower for month in _ROMANIAN_MONTHS):
                detected_languages.append('ro')
                return detected_languages  # Early exit: high confidence

        # Check for Latin-based languages (English, German, Dutch, Turkish)
        # Only check if no accented languages were detected (to avoid false matches)
        if CHAR_SET_LATIN in char_sets and not detected_languages:
            # English month names (use pyparsing for consistency with codebase)
            # pyparsing's oneOf with scanString naturally handles word boundaries
            if next(_ENGLISH_MONTH_PATTERN.scanString(text_lower, maxMatches=1), None) is not None:
                detected_languages.append('en')
                return detected_languages  # Early exit: high confidence

            # Dutch month names (check before German since they share month names like "juli")
            if any(month in text_lower for month in _DUTCH_MONTHS):
                detected_languages.append('nl')
                return detected_languages  # Early exit: high confidence

            # German month names (use pyparsing for consistency)
            if next(_GERMAN_MONTH_PATTERN.scanString(text_lower, maxMatches=1), None) is not None:
                detected_languages.append('de')
                return detected_languages  # Early exit: high confidence

            # Turkish month names
            if any(month in text_lower for month in _TURKISH_MONTHS):
                detected_languages.append('tr')
                return detected_languages  # Early exit: high confidence

        # If no specific language detected but we have character sets, return None
        # (let other filters handle it)
        return detected_languages if detected_languages else None

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
                                       noyearformatfilter=False, nolanguagefilter=False):
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
        :return: Filtered list of patterns, or None if no patterns remain
        :rtype: list|None
        """
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
            if self._language_allowlist is not None and detected_languages:
                detected_languages = [
                    lang for lang in detected_languages if lang in self._language_allowlist
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
                                     noyearformatfilter=False, nolanguagefilter=False):
        """Single-walk fingerprint-based candidate selection.

        Mirrors ``_filter_patterns_hierarchical`` (length → charset → separator →
        language → year_format → prefix) but collapses the first five levels into
        one intersection over the precomputed ``qddate.patterns.fingerprint.
        _PATTERN_FINGERPRINTS`` index via :func:`candidate_keys_for`. The prefix
        filter (``__matchPrefix``) is kept as the final gate because it depends
        on the candidate set and the prefix index, not on text-fingerprint
        dimensions.

        The result is a **superset-or-equal** of the legacy 6-level pipeline's
        candidate set on every probe string (``tests/test_fingerprint_parity.py``
        locks this property). The legacy pipeline remains the default
        (``use_fingerprint=False``) until parity is fully locked.

        :param text: Input text to match.
        :type text: str
        :param n: Length of text (``len(text)``).
        :type n: int
        :param noprefix: If True, skip the prefix filter.
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

        text_char_sets = scan_char_sets(text) if not nocharsetfilter else frozenset()
        separators = self._detect_separators(text) if not noseparatorfilter else {"mixed"}
        if nolanguagefilter:
            detected_languages: list[str] = []
        else:
            detected_languages = self._detect_language(text)
            if self._language_allowlist is not None and detected_languages:
                # Intersection with the caller's allow-list (German "Juli"
                # regression fix): when the caller forced a specific
                # language, detection must not narrow below it.
                detected_languages = [
                    lang for lang in detected_languages
                    if lang in self._language_allowlist
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
            if self._language_allowlist is not None and fp_lang in self._language_allowlist:
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

        # Single-walk intersection over the per-instance fingerprint index.
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
        pats: list[dict] = []
        for fp, bucket in self._pattern_fingerprints.items():
            if fp.length_min > n or fp.length_max < n:
                continue
            if not _chars_match(fp.chars):
                continue
            if not _lang_match(fp.language):
                continue
            if not _year_match(fp.year_format):
                continue
            for p in bucket:
                if _sep_match(fp.separator, fp.language):
                    pats.append(p)
                elif _space_compat_basekey(p.get("basekey", p.get("key", ""))):
                    pats.append(p)

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

    def _calculate_pattern_priority(self, pattern, text):
        """Calculate priority score for pattern based on text characteristics.

        Higher scores indicate patterns more likely to match. Patterns are sorted
        by priority (descending) to try most promising patterns first.

        :param pattern: Pattern dictionary
        :type pattern: dict
        :param text: Input text to match
        :type text: str
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

        # Boost if length is exact match (more likely to be correct)
        length_min = pattern.get("length", {}).get("min", 0)
        length_max = pattern.get("length", {}).get("max", 0)
        if length_min <= n <= length_max:
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

        return score

    def _iter_matches(self, text, noprefix=False, allow_no_year=True, nocharsetfilter=False,
                      noseparatorfilter=False, noyearformatfilter=False,
                      nolanguagefilter=False):
        """Yield ``(priority, end, result)`` for every candidate pattern matching
        ``text`` at position 0, highest priority first.

        Shared engine behind :meth:`match` and :meth:`match_all`. Components are
        sanity-checked (month/day/hour/minute/second ranges) before yielding.
        """
        n = len(text)

        # Route to the fingerprint-based filter when the constructor flag is set,
        # otherwise fall through to the existing 6-level pipeline. Both paths
        # share the same candidate-set semantics (level 6 prefix + score +
        # component-range validation); the fingerprint path is parity-locked
        # to be a superset-or-equal of the legacy path on every probe string.
        if self.use_fingerprint:
            pats = self._filter_patterns_fingerprint(text, n, noprefix=noprefix, allow_no_year=allow_no_year,
                                                     nocharsetfilter=nocharsetfilter,
                                                     noseparatorfilter=noseparatorfilter,
                                                     noyearformatfilter=noyearformatfilter,
                                                     nolanguagefilter=nolanguagefilter)
        else:
            pats = self._filter_patterns_hierarchical(text, n, noprefix=noprefix, allow_no_year=allow_no_year,
                                                      nocharsetfilter=nocharsetfilter,
                                                      noseparatorfilter=noseparatorfilter,
                                                      noyearformatfilter=noyearformatfilter,
                                                      nolanguagefilter=nolanguagefilter)
        if not pats:
            return

        # Sort patterns by priority (try most likely patterns first)
        scored = sorted(
            ((self._calculate_pattern_priority(p, text), p) for p in pats),
            key=lambda item: item[0], reverse=True)

        for _score, p in scored:
            # Cache dictionary lookups
            length_min = p["length"]["min"]
            length_max = p["length"]["max"]
            if n < length_min or n > length_max:
                continue
            if not allow_no_year:
                if p.get("noyear", False):
                    continue
            match_data = next(p["pattern"].scanString(text, maxMatches=1), None)
            if match_data is None:
                continue
            r, start, end = match_data
            if start != 0:
                continue
            if not _values_in_range(r.asDict()):
                continue
            yield _score, end, {"values": r, "pattern": p}

    def match(self, text: str, noprefix: bool = False, allow_no_year: bool = True, nocharsetfilter: bool = False,
             noseparatorfilter: bool = False, noyearformatfilter: bool = False,
             nolanguagefilter: bool = False, *, noyear: TOptional[bool] = None) -> Union[dict, None]:  # noqa: E501
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


        :return: Returns dicts with `values` as array of representing parsed date and 'pattern'
            with info about matched pattern if successful, else returns None
        :rtype: :class:`dict`."""
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            allow_no_year = noyear
        # Among equally-prioritized matches prefer the one consuming the most
        # input (e.g. HH:MM:SS over HH:MM). Iteration is priority-sorted, so we
        # stop as soon as the priority drops below the current best.
        best = None
        for score, end, result in self._iter_matches(
                text, noprefix=noprefix, allow_no_year=allow_no_year,
                nocharsetfilter=nocharsetfilter, noseparatorfilter=noseparatorfilter,
                noyearformatfilter=noyearformatfilter, nolanguagefilter=nolanguagefilter):
            if best is None or (score == best[0] and end > best[1]):
                best = (score, end, result)
            else:
                break
        return best[2] if best else None

    def match_all(self, text: str, noprefix: bool = False, allow_no_year: bool = True,
                  nocharsetfilter: bool = False, noseparatorfilter: bool = False,
                  noyearformatfilter: bool = False,
                  nolanguagefilter: bool = False, *,
                  noyear: TOptional[bool] = None) -> list[dict]:
        """Return every distinct match for ``text``, best first.

        Unlike :meth:`match` (which returns a single winner), this surfaces
        ambiguity: ``01/02/2020`` is valid as both D/M/Y and M/D/Y, and scraping
        callers often need to know that instead of silently getting one
        interpretation. Results are deduplicated by base pattern, keeping the
        longest-consuming variant of each.

        Accepts the same filter flags as :meth:`match`. ``noyear=`` is the
        deprecated alias for ``allow_no_year=``.

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
        results: list[tuple[int, dict]] = []
        index_by_basekey: dict[str, int] = {}
        for _score, end, result in self._iter_matches(
                text, noprefix=noprefix, allow_no_year=allow_no_year,
                nocharsetfilter=nocharsetfilter, noseparatorfilter=noseparatorfilter,
                noyearformatfilter=noyearformatfilter, nolanguagefilter=nolanguagefilter):
            p = result["pattern"]
            basekey = p.get("basekey", p.get("key", ""))
            if basekey in index_by_basekey:
                idx = index_by_basekey[basekey]
                if end > results[idx][0]:
                    results[idx] = (end, result)
                continue
            index_by_basekey[basekey] = len(results)
            results.append((end, result))
        return [result for _end, result in results]

    def parse(self, text: str, noprefix: bool = False, nocharsetfilter: bool = False,
              noseparatorfilter: bool = False, noyearformatfilter: bool = False,
              nolanguagefilter: bool = False, allow_no_year: bool = True,
              *, noyear: TOptional[bool] = None) -> Union[datetime.datetime, None]:
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
            If True (default) patterns without a year are allowed and the current
            year is substituted (e.g. "05.12"); if False such patterns are skipped.
        :type allow_no_year: bool
        :param noyear:
            **Deprecated.** Use ``allow_no_year=`` instead.
        :type noyear: bool


        :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
        :rtype: :class:`datetime <datetime.datetime>`."""
        if noyear is not None:
            warnings.warn(
                "noyear= is deprecated; use allow_no_year= instead.",
                DeprecationWarning, stacklevel=2,
            )
            allow_no_year = noyear
        res = self.match(text, noprefix=noprefix, allow_no_year=allow_no_year,
                         nocharsetfilter=nocharsetfilter,
                         noseparatorfilter=noseparatorfilter,
                         noyearformatfilter=noyearformatfilter,
                         nolanguagefilter=nolanguagefilter)
        if res:
            return self._build_datetime(res)
        return None

    def _build_datetime(self, res):
        """Convert a ``match()`` result into a :class:`datetime.datetime`.

        Applies the parser's ``pivot_year`` (2-digit years) and ``tz_aware``
        (parsed ``+HHMM`` offset) options. Returns None for out-of-range values
        or unexpected result keys instead of raising.
        """
        r = res["values"]
        p = res["pattern"]
        d = {"month": 0, "day": 0, "year": 0}
        if p.get("noyear", False):
            d["year"] = self._get_cached_year()
        tz_offset = None
        for k, v in r.items():
            if k == "timezone":
                # "+HHMM" offset captured by pat:time:full; not a datetime kwarg.
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
        if tz_offset is not None and self._tz_aware:
            tz_txt = str(tz_offset).zfill(4)
            hours, minutes = int(tz_txt[:2]), int(tz_txt[2:])
            if hours <= 23 and minutes <= 59:
                dt = dt.replace(tzinfo=datetime.timezone(
                    datetime.timedelta(hours=hours, minutes=minutes)))
        return dt

    def match_typed(self, text: str, **kwargs: Any) -> Union[DateMatch, None]:
        """Like :meth:`match`, but returns a typed :class:`DateMatch` (or None).

        The datetime is already constructed (honoring ``pivot_year``/``tz_aware``),
        and the result carries ``pattern_key``, ``language``, ``format`` and the
        original ``raw`` text. Accepts the same filter flags as :meth:`match`.
        """
        res = self.match(text, **kwargs)
        if res is None:
            return None
        dt = self._build_datetime(res)
        if dt is None:
            return None
        p = res["pattern"]
        return DateMatch(
            datetime=dt,
            pattern_key=p["key"],
            language=_pattern_language(p),
            format=p.get("format", ""),
            raw=text,
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

