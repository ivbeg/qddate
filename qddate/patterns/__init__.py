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
from .pl import PATTERNS_PL
from .pt import PATTERNS_PT
from .ru import PATTERNS_RU
from .tr import PATTERNS_TR

ALL_PATTERNS = (PATTERNS_EN + INTEGER_LIKE_PATTERNS + PATTERNS_BG +
                PATTERNS_CZ + PATTERNS_DE + PATTERNS_ES + PATTERNS_FR +
                PATTERNS_IT + PATTERNS_PL + PATTERNS_PT + PATTERNS_RU +
                PATTERNS_TR)

SUPPORTED_LANGUAGES = [
    "bg",
    "cz",
    "de",
    "en",
    "es",
    "fr",
    "it",
    "pl",
    "pt",
    "ru",
    "tr",
]
