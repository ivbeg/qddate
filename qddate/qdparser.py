#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

import datetime
import os
import time
import re

from pyparsing import Optional, lineStart, oneOf, Literal, restOfLine, Word, nums, Regex

try:
   import dill
   DILL_ENABLED = True
except:
   DILL_ENABLED = False

# Enable packrat parsing for better performance
try:
    from pyparsing import ParserElement
    ParserElement.enable_packrat()
except:
    pass

from .dirty import matchPrefix
from .patterns import ALL_PATTERNS, BASE_TIME_PATTERNS, get_patterns_for_languages, SUPPORTED_LANGUAGES

# Pre-compiled month name sets for language detection (lowercase for fast matching)
_RUSSIAN_MONTHS = frozenset(['января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
                             'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
                             'январь', 'февраль', 'март', 'апрель', 'июнь', 'июль',
                             'август', 'сентябрь', 'октябрь', 'ноябрь', 'декабрь'])
_FRENCH_MONTHS = frozenset(['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'])
_SPANISH_MONTHS = frozenset(['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                            'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'])
_ITALIAN_MONTHS = frozenset(['gennaio', 'febbraio', 'marzo', 'aprile', 'maggio', 'giugno',
                            'luglio', 'agosto', 'settembre', 'ottobre', 'novembre', 'dicembre'])
_PORTUGUESE_MONTHS = frozenset(['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                               'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'])
_CZECH_MONTHS = frozenset(['leden', 'únor', 'březen', 'duben', 'květen', 'červen',
                           'červenec', 'srpen', 'září', 'říjen', 'listopad', 'prosinec'])
_POLISH_MONTHS = frozenset(['styczeń', 'stycznia', 'luty', 'lutego', 'marzec', 'marca', 
                            'kwiecień', 'kwietnia', 'maj', 'maja', 'czerwiec', 'czerwca',
                            'lipiec', 'lipca', 'sierpień', 'sierpnia', 'wrzesień', 'września',
                            'październik', 'października', 'listopad', 'listopada', 
                            'grudzień', 'grudnia'])
_ENGLISH_MONTHS = frozenset(['january', 'february', 'march', 'april', 'may', 'june',
                            'july', 'august', 'september', 'october', 'november', 'december',
                            'jan', 'feb', 'mar', 'apr', 'may', 'jun',
                            'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])
_GERMAN_MONTHS = frozenset(['januar', 'februar', 'märz', 'april', 'mai', 'juni',
                           'juli', 'august', 'september', 'oktober', 'november', 'dezember'])
_DUTCH_MONTHS = frozenset(['januari', 'februari', 'maart', 'april', 'mei', 'juni',
                          'juli', 'augustus', 'september', 'oktober', 'november', 'december'])
_TURKISH_MONTHS = frozenset(['ocak', 'şubat', 'mart', 'nisan', 'mayıs', 'haziran',
                            'temmuz', 'ağustos', 'eylül', 'ekim', 'kasım', 'aralık'])

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
    'de': {CHAR_SET_DIGITS, CHAR_SET_LATIN},  # may have umlauts but treated as latin
    'tr': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
    'en': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
    'nl': {CHAR_SET_DIGITS, CHAR_SET_LATIN},
}


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

    def __init__(self, generate=True, patterns=ALL_PATTERNS, base_only=False, languages=None):
        """Inits class DataParser
        :param generate: Boolean value, if true, than automatically generate all patterns from base list self.patterns
        :param patterns: list of patterns to be used. Default ALL_PATTERNS. See qddate.patterns for more info
        :param base_only: Use only base patterns during generation of final list. Filters all patterns with text after datetime.
        :param languages: Language code (str) or list of language codes (list of str) to filter patterns by.
                         If None, uses all patterns. If specified, filters patterns to only include those for the specified languages.
                         Examples: languages="ru", languages=["en", "de"], languages=None (default)
        :type languages: str|list|None
        """
        # Filter patterns by language if languages parameter is provided
        if languages is not None:
            patterns = get_patterns_for_languages(languages)
        
        self.patterns = patterns
        self._current_year = datetime.datetime.now().year
        self._year_refresh_interval = 3600  # seconds
        self._next_year_refresh = time.monotonic() + self._year_refresh_interval
        if generate:
            self.__generate(base_only)
        self._build_length_index()
        self._build_separator_index()
        self._build_year_format_index()
        self._build_language_index()
        self.cachedpats = None
        self.ind = []

    def __matchPrefix(self, text):
        """
        Wrapper for matchPrefix function that filters patterns based on text prefix.
        Accuracy-first implementation - returns comprehensive pattern sets to avoid
        missing valid dates due to overly restrictive filtering.
        :param text: text with date to match (typically first 6 characters)
        :return: list of pattern basekeys to run against
        """
        return matchPrefix(text)

    def startSession(self, cached_p):
        cached_set = set(cached_p) if not isinstance(cached_p, set) else cached_p
        self.cachedpats = [x for x in self.patterns if x["key"] in cached_set]

    def endSession(self):
        self.cachedpats = None

    def __generate(self, base_only=False):
        """Generates dates patterns"""
        base = []
        texted = []
        for pat in self.patterns:
            # Assign character set metadata to base pattern
            if "required_chars" not in pat:
                pat["required_chars"] = self._infer_char_sets(pat)
            
            data = {**pat}
            data["basekey"] = data["key"]
            data["key"] += ":time_1"
            data["right"] = True
            data["pattern"] = (data["pattern"] +
                               Optional(Literal(",")).suppress() +
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
                               Optional(oneOf([",", "|", "T"])).suppress() +
                               BASE_TIME_PATTERNS["pat:time:full"])
            data["time_format"] = "%H:%M:%S"
            data["length"] = {
                "min": data["length"]["min"] + 9,
                "max": data["length"]["max"] + 9,
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
                               Optional(Literal("[")).suppress() +
                               BASE_TIME_PATTERNS["pat:time:minutes"] +
                               Optional(Literal("]")).suppress())
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
                    Optional(oneOf([",", "|", ":", ")"])).suppress() +
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
        
        :param pattern: Pattern dictionary
        :type pattern: dict
        :return: Set of required character set constants
        :rtype: set
        """
        key = pattern.get("key", "")
        basekey = pattern.get("basekey", key)
        
        # Extract language from pattern key
        # Pattern keys like "dt:date:date_rus" or "dt:date:date_eng1"
        lang = None
        if "_rus" in basekey or "rus_" in basekey:
            lang = 'ru'
        elif "_bg" in basekey or "bg_" in basekey:
            lang = 'bg'
        elif "_fr" in basekey or "fr_" in basekey:
            lang = 'fr'
        elif "_cz" in basekey or "cz_" in basekey:
            lang = 'cz'
        elif "_pl" in basekey or "pl_" in basekey:
            lang = 'pl'
        elif "_es" in basekey or "es_" in basekey:
            lang = 'es'
        elif "_it" in basekey or "it_" in basekey:
            lang = 'it'
        elif "_pt" in basekey or "pt_" in basekey:
            lang = 'pt'
        elif "_de" in basekey or "de_" in basekey:
            lang = 'de'
        elif "_tr" in basekey or "tr_" in basekey:
            lang = 'tr'
        elif "_nl" in basekey or "nl_" in basekey:
            lang = 'nl'
        elif "_eng" in basekey or "eng" in basekey or "date_usa" in basekey:
            lang = 'en'
        
        # Check if pattern has month names (non-numeric patterns)
        # Numeric-only patterns (like date_1, date_2, date_iso8601) only need digits
        has_month_names = (
            "eng" in basekey or
            "rus" in basekey or
            "fr" in basekey or
            "es" in basekey or
            "it" in basekey or
            "pt" in basekey or
            "de" in basekey or
            "bg" in basekey or
            "cz" in basekey or
            "pl" in basekey or
            "tr" in basekey or
            "nl" in basekey or
            "weekday" in basekey
        )
        
        # If we found a language and it has month names, use language-specific sets
        if lang and has_month_names:
            return LANGUAGE_CHAR_SETS.get(lang, {CHAR_SET_DIGITS, CHAR_SET_LATIN})
        
        # Numeric-only patterns (like date_1, date_2, date_5, date_6, date_iso8601, date_usa)
        # These patterns only contain digits and separators
        if any(x in basekey for x in ["date_1", "date_2", "date_3", "date_4", "date_5", 
                                      "date_6", "date_7", "date_8", "date_9", "date_10",
                                      "date_iso8601", "date_iso8601_short", "date_usa", 
                                      "date_usa_1", "noyear_1"]):
            return {CHAR_SET_DIGITS}
        
        # Default: assume digits and latin (for English patterns without explicit markers)
        return {CHAR_SET_DIGITS, CHAR_SET_LATIN}

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
            key = p.get("key", "")
            basekey = p.get("basekey", key)
            
            # Infer separator from pattern key or format
            # Note: Check more specific patterns first (e.g., date_10 before date_1) to avoid substring matching issues
            if any(x in basekey for x in ["date_10", "date_4_point", "date_rus3", "date_usa_1"]):
                # More specific patterns first to avoid substring matching (e.g., date_1 matching date_10)
                if "date_10" in basekey or "date_4_point" in basekey or "date_rus3" in basekey:
                    self._patterns_by_separator['dot'].append(p)
                elif "date_usa_1" in basekey:
                    self._patterns_by_separator['slash'].append(p)
            elif any(x in basekey for x in ["date_2", "date_4", "noyear_1", "rare_2", "rare_3", "rus_rare_2", "rus_rare_3", "date_eng1", "date_eng1_lc", "date_eng1_short"]):
                self._patterns_by_separator['dot'].append(p)
            elif any(x in basekey for x in ["date_1", "date_8", "date_usa", "rare_1"]):
                self._patterns_by_separator['slash'].append(p)
            elif any(x in basekey for x in ["date_3"]):
                # date_3 (yyyy/m/d) can accept both / and space, index under slash for now
                # The separator filter will handle space detection
                self._patterns_by_separator['slash'].append(p)
            elif any(x in basekey for x in ["date_iso8601", "date_iso8601_short", "date_9"]):
                self._patterns_by_separator['dash'].append(p)
            elif any(x in basekey for x in ["date_5", "date_6", "date_7"]):
                self._patterns_by_separator['none'].append(p)
            elif any(x in basekey for x in ["eng", "rus", "fr", "de", "es", "it", "pt", "bg", "cz", 
                                             "pl", "tr", "nl", "weekday"]):
                self._patterns_by_separator['space'].append(p)
            else:
                self._patterns_by_separator['mixed'].append(p)

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
        """Pre-index patterns by language for faster filtering"""
        self._patterns_by_language = {}
        
        for p in self.patterns:
            key = p.get("key", "")
            basekey = p.get("basekey", key)
            
            # Extract language from pattern basekey
            lang = None
            if "_rus" in basekey or "rus_" in basekey:
                lang = 'ru'
            elif "_bg" in basekey or "bg_" in basekey:
                lang = 'bg'
            elif "_fr" in basekey or "fr_" in basekey:
                lang = 'fr'
            elif "_cz" in basekey or "cz_" in basekey:
                lang = 'cz'
            elif "_pl" in basekey or "pl_" in basekey:
                lang = 'pl'
            elif "_es" in basekey or "es_" in basekey:
                lang = 'es'
            elif "_it" in basekey or "it_" in basekey:
                lang = 'it'
            elif "_pt" in basekey or "pt_" in basekey:
                lang = 'pt'
            elif "_de" in basekey or "de_" in basekey:
                lang = 'de'
            elif "_tr" in basekey or "tr_" in basekey:
                lang = 'tr'
            elif "_nl" in basekey or "nl_" in basekey:
                lang = 'nl'
            elif "_eng" in basekey or "eng" in basekey or "date_usa" in basekey:
                lang = 'en'
            
            if lang:
                if lang not in self._patterns_by_language:
                    self._patterns_by_language[lang] = []
                self._patterns_by_language[lang].append(p)

    def _filter_patterns_hierarchical(self, text, n, noprefix=False, noyear=True, 
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
        :param noyear: If True, use patterns with noyear flag
        :type noyear: bool
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
                
                # Patterns that accept multiple separator types (e.g., date_1, date_8, date_3 now accept both / and space)
                # Include slash and mixed patterns when space is detected (since patterns now accept both)
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
                        elif has_text and any(x in basekey for x in ["eng", "rus", "fr", "de", "es", "it", 
                                                                      "pt", "bg", "cz", "pl", "tr", "nl", 
                                                                      "weekday", "rare"]):
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
                for p in self._patterns_by_year_format.get(year_format, []):
                    pat_key = p.get("key")
                    if pat_key not in year_pat_keys:
                        year_pats.append(p)
                        year_pat_keys.add(pat_key)
                # Also include 'any' patterns
                for p in self._patterns_by_year_format.get('any', []):
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
        
        # Higher priority for common patterns
        if "date_1" in basekey or "date_2" in basekey:
            score += 100
        elif "date_iso8601" in basekey:
            score += 80
        elif "date_9" in basekey:
            score += 75
        elif any(x in basekey for x in ["date_3", "date_4", "date_5", "date_6"]):
            score += 70
        elif any(x in basekey for x in ["eng", "rus", "fr", "de", "es", "it", "pt"]):
            score += 60
        
        # Boost if separator matches (optimized: check separator first, then pattern types)
        if '/' in text:
            if "date_1" in basekey or "date_8" in basekey or "date_usa" in basekey:
                score += 20
        elif '.' in text:
            if "date_2" in basekey or "date_4" in basekey or "date_10" in basekey:
                score += 20
        elif '-' in text:
            if "date_iso8601" in basekey or "date_9" in basekey:
                score += 20
        elif ' ' in text:
            # Use 'in' checks directly instead of any() for common patterns
            if ("eng" in basekey or "rus" in basekey or "fr" in basekey or "de" in basekey or 
                "es" in basekey or "it" in basekey or "pt" in basekey or "bg" in basekey or 
                "cz" in basekey or "pl" in basekey or "tr" in basekey or "nl" in basekey or 
                "weekday" in basekey):
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

    def match(self, text, noprefix=False, noyear=True, nocharsetfilter=False, noseparatorfilter=False, noyearformatfilter=False, nolanguagefilter=False):
        """Matches date/datetime string against date patterns and returns pattern and parsed date if matched.
        It's not indeded for common usage, since if successful it returns date as array of numbers and pattern
        that matched this date

        :param text:
            Any human readable string
        :type date_string: str|unicode
        :param noprefix:
            If set True than doesn't use prefix based date patterns filtering settings
        :type noprefix: bool
        :param noyear:
            If set True than does use patterns with noyear flag (does a lot of false positives) if set False doesn't use patterns with noyear flag
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


        :return: Returns dicts with `values` as array of representing parsed date and 'pattern' with info about matched pattern if successful, else returns None
        :rtype: :class:`dict`."""
        n = len(text)
        
        # Use hierarchical filtering to get candidate patterns
        pats = self._filter_patterns_hierarchical(text, n, noprefix=noprefix, noyear=noyear,
                                                   nocharsetfilter=nocharsetfilter, 
                                                   noseparatorfilter=noseparatorfilter,
                                                   noyearformatfilter=noyearformatfilter,
                                                   nolanguagefilter=nolanguagefilter)
        if pats is None:
            return None
        
        # Sort patterns by priority (try most likely patterns first)
        pats = sorted(pats, key=lambda p: self._calculate_pattern_priority(p, text), reverse=True)
        
        # Note: basekey filtering is already done in _filter_patterns_hierarchical (Level 6),
        # so we don't need to duplicate it here. The patterns returned already have prefix filtering applied.
        for p in pats:
            # Cache dictionary lookups
            length_min = p["length"]["min"]
            length_max = p["length"]["max"]
            if n < length_min or n > length_max:
                continue
            if not noyear:
                p_noyear = p.get("noyear", False)
                if p_noyear:
                    continue
            match_data = next(p["pattern"].scanString(text, maxMatches=1), None)
            if match_data is None:
                continue
            r, start, _ = match_data
            if start != 0:
                continue
            # Do sanity check - cache dict lookup and use dict.get() for efficiency
            d = r.asDict()
            month_val = d.get("month")
            if month_val is not None:
                val = int(month_val)
                if val > 12 or val < 1:
                    continue
            day_val = d.get("day")
            if day_val is not None:
                val = int(day_val)
                if val > 31 or val < 1:
                    continue
            return {"values": r, "pattern": p}
        return None

    def parse(self, text, noprefix=False, nocharsetfilter=False, noseparatorfilter=False, noyearformatfilter=False, nolanguagefilter=False):
        """Parse date and time from given date string.

        :param text:
            Any human readable string
        :type date_string: str|unicode
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


        :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
        :rtype: :class:`datetime <datetime.datetime>`."""

        res = self.match(text, noprefix=noprefix, nocharsetfilter=nocharsetfilter, 
                        noseparatorfilter=noseparatorfilter, noyearformatfilter=noyearformatfilter,
                        nolanguagefilter=nolanguagefilter)
        if res:
            r = res["values"]
            p = res["pattern"]
            d = {"month": 0, "day": 0, "year": 0}
            if p.get("noyear", False):
                d["year"] = self._get_cached_year()
            for k, v in r.items():
                d[k] = int(v)
            try:
                dt = datetime.datetime(**d)
                return dt
            except ValueError:
                # Invalid date values (e.g., year 0) - return None
                return None
        return None

    def _get_cached_year(self):
        """Return cached current year, refreshing periodically."""
        now = time.monotonic()
        if now >= self._next_year_refresh:
            self._current_year = datetime.datetime.now().year
            self._next_year_refresh = now + self._year_refresh_interval
        return self._current_year


if __name__ == "__main__":

    tests = [
        "01.12.2009",
        "2013-01-12",
        "31.05.2001",
        "7/12/2009",
        "6 Jan 2009",
        "Jan 8, 1098",
        "JAN 1, 2001",
        "3 Января 2003 года",
        "05 Января 2003",
        "12.03.1999 Hello people",
        "15 февраля 2007 года",
        "5 August 2001",
        "3 jun 2009",
        "16 May 2009 14:10",
        "01 february 2009",
        "01.03.2009 14:53",
        "01.03.2009 14:53:12",
        "22.12.2009 17:56",
        "05/16/99",
        "11/29/1991",
        "Thursday 4 April 2019",
        "July 01, 2015",
        "Fri, 3 July 2015",
        "2 Июня 2015",
        "9 июля 2015 г.",
        "26 / 06 ‘15",
        "09.июля.2015",
        "14th April 2015:",
        "23 Jul 2015, 09:00 BST",
        "пятница, июля 17, 2015",
        "Июль 16, 2015",
        "Le 8 juillet 2015",
        "8 juillet 2015",
        "Fri 24 Jul 2015",
        "26 de julho de 2015",
        "17 de Junio de 2015",
        "28. Juli 2015",
        "21 Фeвpyapи 2015",
        "1 нoeмвpи 2013",
        "23 июня 2015",
        "3 Июля, 2015",
        "7 August, 2015",
        "Wednesday 22 Apr 2015",
        "12-08-2015 - 09:00",
        "08 Jul, 2015",
        "August 10th, 2015",
        "junio 9, 2015",
        "Авг 11, 2015",
        "Вторник, 18 Август 2015 18:51",
        "Июль 16th, 2012 | 11:08 пп",
        "19 август в 16:03",
        "7 August, 2015",
        "9 Июля 2015 [11:23]",
    ]

    #    print list(calendar.month_abbr)[1:]
    ind = DateParser(generate=True)
    #    for i in ind.patterns:
    #        print i
    print(len(ind.patterns))
    for text in tests:
        res = ind.match(text)
        print(r)
        if r:
            r = res["values"]
            p = res["pattern"]
            d = {"month": 0, "day": 0, "year": 0}
            if "noyear" in p and p["noyear"] == True:
                d["year"] = datetime.datetime.now().year
            for k, v in list(r.items()):
                d[k] = int(v)
            dt = datetime.datetime(**d)
        else:
            pass

    #    for p in ind.patterns:
    #        pprint(p)

    for text in tests:
        pass
        # print(dateparser.parse(text))
#    ind.patterns = DATE_DATA_TYPES_RAW
