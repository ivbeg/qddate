#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Prefix-bucket matching derived from `_PATTERN_METADATA`.
#
# Previously, this module kept ~15 hand-synced basekey lists (`_DE_BASEKEYS`,
# `_ES_BASEKEYS`, `_DOT_SEPARATOR_BASEKEYS`, …) that had to be hand-maintained
# alongside pattern definitions. Adding a pattern required editing multiple
# inference sites to avoid silently discarding it from the prefix filter — the
# root cause of bug 4.4 in `IMPROVEMENT_PLAN.md` (the `date_eng4_short` and
# `*_abbrev*` families were unreachable because they were missing from the
# buckets).
#
# The buckets are now built once at import time from `_PATTERN_METADATA`
# (the single source of truth for `language` and `separator`). Adding a new
# pattern means appending to `_PATTERN_METADATA` and `ALL_PATTERNS` — nothing
# else.
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

from .patterns import ALL_PATTERNS


def _build_buckets():
    """Group `ALL_PATTERNS` basekeys by their stamped `(separator, language)`
    metadata, then fold them into the same combined views the legacy hand-synced
    buckets used to expose.

    Returns
    -------
    dict[str, tuple[str, ...]]
        A mapping from bucket name to a sorted tuple of basekeys. The names
        match the legacy module-level constants so `matchPrefix()` can read
        them in place of the old code.
    """
    by_sep = {}      # separator -> set[str]
    by_lang = {}     # language  -> set[str]

    for p in ALL_PATTERNS:
        sep = p.get("separator", "mixed")
        lang = p.get("language")
        key = p["key"]
        by_sep.setdefault(sep, set()).add(key)
        if lang:
            by_lang.setdefault(lang, set()).add(key)

    # Build combined views that the original `matchPrefix()` used. The hand-synced
    # lists intentionally duplicated keys across multiple views (e.g. `date_1`
    # appears in both `_SLASH_SEPARATOR_BASEKEYS` and `_EXTENDED_DIGIT_BASEKEYS`).
    # The derived buckets do this naturally: any pattern whose metadata
    # appears in multiple combined views contributes its key once to each.

    def _u(*names):
        """Union of multiple named groups (sets already in by_sep / by_lang)."""
        out = set()
        for n in names:
            if n in by_sep:
                out |= by_sep[n]
            elif n in by_lang:
                out |= by_lang[n]
        return out

    # alpha: all language-tagged patterns. English + the historical core.
    alpha_english_full = _u("en", "pt", "es", "it", "fr", "ro", "uk",
                            "de", "nl")  # anything that resolves to "alpha English" view
    alpha_non_english = _u("ru", "bg", "cz", "pl", "tr")  # Cyrillic / mixed-script
    all_alpha = alpha_english_full | alpha_non_english

    # Digit-separator: patterns whose separator is slash/dot/dash/none/mixed.
    all_separator = _u("slash", "dot", "dash", "none", "mixed")

    # Default digit: every separator bucket AND every language-tagged pattern.
    # The legacy `_DEFAULT_DIGIT_FULL` was a UNION of the per-language basekey
    # lists (German, Spanish, Bulgarian, …) plus the digit-separator lists;
    # doing the same here preserves the historical "consider everything in the
    # fallback path" behaviour. The downstream filter pipeline removes the
    # patterns that can't actually match, so over-inclusion is safe.
    default_digit = _u("slash", "dot", "dash", "none", "mixed",
                       "en", "pt", "es", "it", "fr", "ro", "uk",
                       "de", "nl", "ru", "bg", "cz", "pl", "tr")

    # Aliases the old `matchPrefix()` used (named groups for clarity).
    return {
        # Alpha (letter-prefixed inputs)
        "_ALPHA_ENGLISH_BASEKEYS":  tuple(sorted(alpha_english_full)),
        "_ALPHA_NON_ENGLISH_BASEKEYS": tuple(sorted(alpha_non_english)),
        "_ALL_ALPHA_PATTERNS":     tuple(sorted(all_alpha)),
        # Dot separator
        "_DOT_SEPARATOR_BASEKEYS": tuple(sorted(by_sep.get("dot", set()))),
        # Slash separator
        "_SLASH_SEPARATOR_BASEKEYS": tuple(sorted(by_sep.get("slash", set()))),
        # Dash separator (also includes ISO/dash-long patterns)
        "_DASH_SEPARATOR_BASEKEYS": tuple(sorted(by_sep.get("dash", set()))),
        # Russian comma-separated
        "_RUS_SEPARATOR_BASEKEYS": tuple(sorted(by_lang.get("ru", set()) & _u("dot"))) or ("dt:date:date_rus",),
        # Combined views
        "_ALPHA_ENGLISH_FULL": tuple(sorted(alpha_english_full)),
        "_DOT_SEPARATOR_FULL": tuple(sorted(_u("dot"))),
        "_DEFAULT_DIGIT_FULL": tuple(sorted(default_digit)),
        "_DASH_LONG_BASEKEYS": tuple(sorted(_u("dash"))),  # everything in 'dash'
        "_DOT_LONG_BASEKEYS": tuple(sorted(_u("dot"))),       # everything in 'dot'
        "_ALL_SEPARATOR_PATTERNS": tuple(sorted(all_separator)),
    }


# Build once at import time. The buckets are frozen tuples so they hash and
# iterate identically to the legacy hand-synced lists.
_BUCKETS = _build_buckets()
globals().update(_BUCKETS)


def matchPrefix(text):
    """Accuracy-first pattern prefix matcher.

    Analyses the prefix of the input and returns a set of pattern basekeys
    that could plausibly match. The bucket groupings are derived once at
    import time from `_PATTERN_METADATA`, so the function no longer depends
    on hand-synced lists.

    Behaviour-preserving: for every probe string in the snapshot at
    `tests/fixtures/dirty_py_bucket_snapshot.json`, this function returns a
    set that contains every basekey the legacy implementation would have
    returned (and may contain additional ones — over-inclusion is safe; the
    extra candidates are filtered out by the downstream filter pipeline).

    :param text: prefix of the input (typically first 6 characters)
    :return: list of pattern basekeys to run against
    """
    # Local aliases for the derived bucket tuples. Names are resolved via
    # `_BUCKETS` (built at import time) so static analysis tools can see the
    # source of every constant.
    default_digit = _BUCKETS["_DEFAULT_DIGIT_FULL"]
    all_alpha = _BUCKETS["_ALL_ALPHA_PATTERNS"]
    all_separator = _BUCKETS["_ALL_SEPARATOR_PATTERNS"]
    dot_full = _BUCKETS["_DOT_SEPARATOR_FULL"]
    dot_long = _BUCKETS["_DOT_LONG_BASEKEYS"]
    slash_full = _BUCKETS["_SLASH_SEPARATOR_BASEKEYS"]
    dash_full = _BUCKETS["_DASH_SEPARATOR_BASEKEYS"]
    dash_long = _BUCKETS["_DASH_LONG_BASEKEYS"]
    rus_full = _BUCKETS["_RUS_SEPARATOR_BASEKEYS"]
    alpha_eng = _BUCKETS["_ALPHA_ENGLISH_FULL"]
    alpha_non_eng = _BUCKETS["_ALPHA_NON_ENGLISH_BASEKEYS"]

    text_len = len(text)
    if text_len == 0:
        return []

    text_stripped = text.lstrip()
    if not text_stripped:
        # All whitespace — comprehensive fallback.
        return list(set(list(default_digit) + list(all_alpha) + list(all_separator)))

    first_char = text_stripped[0]
    result_patterns = []

    # Letter-prefixed input -> alpha patterns + separator patterns (catches
    # "Wed 12/31/2023" and similar leading-text formats).
    if not first_char.isdigit():
        fc = first_char.lower()
        if fc.isalpha():
            result_patterns.extend(all_alpha)
            result_patterns.extend(all_separator)
            return list(set(result_patterns))

    # Digit-prefixed input. Scan up to the first 10 characters for separators.
    separators_found = set()
    has_dot = has_slash = has_dash = has_comma = has_space = False
    scan_len = min(10, len(text_stripped))
    for i in range(1, scan_len):
        ch = text_stripped[i]
        if ch == '.':
            has_dot = True
            separators_found.add('dot')
        elif ch == '/':
            has_slash = True
            separators_found.add('slash')
        elif ch == '-':
            has_dash = True
            separators_found.add('dash')
        elif ch == ',':
            has_comma = True
            separators_found.add('comma')
        elif ch == ' ':
            has_space = True
            separators_found.add('space')
        if len(separators_found) >= 4:
            break

    if has_dot:
        result_patterns.extend(dot_full)
        result_patterns.extend(dot_long)
    if has_slash:
        result_patterns.extend(slash_full)
    if has_dash:
        result_patterns.extend(dash_full)
        result_patterns.extend(dash_long)
    if has_comma:
        result_patterns.extend(rus_full)
        # Comma can also appear in some English formats.
        result_patterns.extend(alpha_eng)
    if has_space:
        # Space is common in many formats — include alpha patterns.
        result_patterns.extend(alpha_eng)
        result_patterns.extend(alpha_non_eng)
        # Also digit-based patterns with spaces (e.g. Russian dates).
        result_patterns.extend(default_digit)

    # Always include default digit patterns as fallback. This handles cases
    # like "20231215" (no separators) and unusual formats.
    result_patterns.extend(default_digit)

    # If no separators were found but the input begins with 4 digits, it's
    # probably an ISO format — include dash patterns.
    if not separators_found and text_len >= 4 and text_stripped[:4].isdigit():
        result_patterns.extend(dash_full)

    return list(set(result_patterns))
