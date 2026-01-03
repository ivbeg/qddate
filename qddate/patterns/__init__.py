# -*- coding: utf-8 -*-
__version__ = "0.1.1"
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

from .base import PATTERNS_EN, BASE_TIME_PATTERNS, INTEGER_LIKE_PATTERNS
from .bg import PATTERNS_BG
from .cz import PATTERNS_CZ
from .de import PATTERNS_DE
from .es import PATTERNS_ES
from .fr import PATTERNS_FR
from .it import PATTERNS_IT
from .nl import PATTERNS_NL
from .pl import PATTERNS_PL
from .pt import PATTERNS_PT
from .ru import PATTERNS_RU
from .tr import PATTERNS_TR

ALL_PATTERNS = (PATTERNS_EN + INTEGER_LIKE_PATTERNS + PATTERNS_BG +
                PATTERNS_CZ + PATTERNS_DE + PATTERNS_ES + PATTERNS_FR +
                PATTERNS_IT + PATTERNS_NL + PATTERNS_PL + PATTERNS_PT +
                PATTERNS_RU + PATTERNS_TR)

SUPPORTED_LANGUAGES = [
    "bg",
    "cz",
    "de",
    "en",
    "es",
    "fr",
    "it",
    "nl",
    "pl",
    "pt",
    "ru",
    "tr",
]

# Mapping of language codes to their pattern lists
PATTERNS_BY_LANGUAGE = {
    "en": PATTERNS_EN + INTEGER_LIKE_PATTERNS,
    "bg": PATTERNS_BG,
    "cz": PATTERNS_CZ,
    "de": PATTERNS_DE,
    "es": PATTERNS_ES,
    "fr": PATTERNS_FR,
    "it": PATTERNS_IT,
    "nl": PATTERNS_NL,
    "pl": PATTERNS_PL,
    "pt": PATTERNS_PT,
    "ru": PATTERNS_RU,
    "tr": PATTERNS_TR,
}


def get_patterns_for_languages(languages):
    """Get patterns for specified languages.
    
    :param languages: Language code (str) or list of language codes (list of str).
                     If None or empty, returns all patterns.
    :type languages: str|list|None
    :return: Combined list of patterns for specified languages
    :rtype: list
    :raises ValueError: If any language code is not in SUPPORTED_LANGUAGES
    """
    if languages is None:
        return ALL_PATTERNS
    
    # Normalize to list
    if isinstance(languages, str):
        languages = [languages]
    elif not isinstance(languages, (list, tuple)):
        raise TypeError("languages must be a string, list of strings, or None")
    
    if len(languages) == 0:
        return ALL_PATTERNS
    
    # Validate all language codes
    invalid_languages = [lang for lang in languages if lang not in SUPPORTED_LANGUAGES]
    if invalid_languages:
        raise ValueError(
            f"Unsupported language(s): {invalid_languages}. "
            f"Supported languages: {SUPPORTED_LANGUAGES}"
        )
    
    # Combine patterns for specified languages
    patterns = []
    for lang in languages:
        patterns.extend(PATTERNS_BY_LANGUAGE[lang])
    
    return patterns