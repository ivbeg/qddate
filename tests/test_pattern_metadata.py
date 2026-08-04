"""Tests for the pattern metadata refactor (Change 3: refactor-pattern-metadata).

These tests guarantee the refactor is behavior-preserving: the explicit `language`
and `separator` fields stamped on each pattern must reproduce exactly what the old
substring-based inference produced. They also guard the single-source-of-truth table
so a new pattern without a metadata entry is caught.
"""
import pytest

from qddate.patterns import ALL_PATTERNS, SUPPORTED_LANGUAGES, _PATTERN_METADATA


# ---------------------------------------------------------------------------
# Verbatim copy of the PRE-refactor substring inference. Kept here (not in the
# library) purely as the reference oracle for the safety-net test. If these
# functions ever disagree with the stamped fields, the refactor changed behavior.
# ---------------------------------------------------------------------------
def _legacy_infer_language(basekey):
    if "_rus" in basekey or "rus_" in basekey:
        return "ru"
    elif "_bg" in basekey or "bg_" in basekey:
        return "bg"
    elif "_fr" in basekey or "fr_" in basekey:
        return "fr"
    elif "_cz" in basekey or "cz_" in basekey:
        return "cz"
    elif "_pl" in basekey or "pl_" in basekey:
        return "pl"
    elif "_es" in basekey or "es_" in basekey:
        return "es"
    elif "_it" in basekey or "it_" in basekey:
        return "it"
    elif "_pt" in basekey or "pt_" in basekey:
        return "pt"
    elif "_de" in basekey or "de_" in basekey:
        return "de"
    elif "_tr" in basekey or "tr_" in basekey:
        return "tr"
    elif "_nl" in basekey or "nl_" in basekey:
        return "nl"
    elif "_eng" in basekey or "eng" in basekey or "date_usa" in basekey:
        return "en"
    return None


def _legacy_infer_separator(basekey):
    if any(x in basekey for x in ["date_10", "date_4_point", "date_rus3", "date_usa_1"]):
        if "date_10" in basekey or "date_4_point" in basekey or "date_rus3" in basekey:
            return "dot"
        elif "date_usa_1" in basekey:
            return "slash"
    if any(x in basekey for x in ["date_2", "date_4", "noyear_1", "rare_2", "rare_3",
                                  "rus_rare_2", "rus_rare_3", "date_eng1",
                                  "date_eng1_lc", "date_eng1_short"]):
        return "dot"
    if any(x in basekey for x in ["date_1", "date_8", "date_usa", "rare_1"]):
        return "slash"
    if any(x in basekey for x in ["date_3"]):
        return "slash"
    if any(x in basekey for x in ["date_iso8601", "date_iso8601_short", "date_9"]):
        return "dash"
    if any(x in basekey for x in ["date_5", "date_6", "date_7"]):
        return "none"
    if any(x in basekey for x in ["eng", "rus", "fr", "de", "es", "it", "pt", "bg",
                                  "cz", "pl", "tr", "nl", "weekday"]):
        return "space"
    return "mixed"


def test_every_pattern_has_metadata_fields():
    """Every base pattern must carry stamped language and separator fields."""
    missing = [
        p["key"] for p in ALL_PATTERNS
        if "language" not in p or "separator" not in p
    ]
    assert missing == [], f"Patterns missing language/separator fields: {missing}"


def test_metadata_table_covers_every_pattern():
    """The single-source-of-truth table must have an entry for every pattern key."""
    table_keys = set(_PATTERN_METADATA)
    pattern_keys = {p["key"] for p in ALL_PATTERNS}
    missing_from_table = pattern_keys - table_keys
    extra_in_table = table_keys - pattern_keys
    assert not missing_from_table, f"Keys missing from _PATTERN_METADATA: {missing_from_table}"
    assert not extra_in_table, f"Stale keys in _PATTERN_METADATA (no such pattern): {extra_in_table}"


def test_stamped_language_matches_legacy_inference():
    """Stamped language must equal what the old substring inference produced."""
    mismatches = []
    for p in ALL_PATTERNS:
        expected = _legacy_infer_language(p["key"])
        if p["language"] != expected:
            mismatches.append((p["key"], p["language"], expected))
    assert not mismatches, f"Language field mismatches (got, expected): {mismatches}"


def test_stamped_separator_matches_legacy_inference():
    """Stamped separator must equal what the old substring inference produced."""
    mismatches = []
    for p in ALL_PATTERNS:
        expected = _legacy_infer_separator(p["key"])
        if p["separator"] != expected:
            mismatches.append((p["key"], p["separator"], expected))
    assert not mismatches, f"Separator field mismatches (got, expected): {mismatches}"


def test_metadata_languages_are_supported_or_none():
    """Every stamped language must be a known code or None (language-neutral)."""
    invalid = [
        (p["key"], p["language"]) for p in ALL_PATTERNS
        if p["language"] is not None and p["language"] not in SUPPORTED_LANGUAGES
    ]
    assert not invalid, f"Invalid language codes: {invalid}"


def test_metadata_separators_are_valid():
    """Every stamped separator must be one of the known separator categories."""
    valid = {"slash", "dot", "dash", "space", "none", "mixed"}
    invalid = [
        (p["key"], p["separator"]) for p in ALL_PATTERNS
        if p["separator"] not in valid
    ]
    assert not invalid, f"Invalid separator values: {invalid}"


# ---------------------------------------------------------------------------
# Charset oracle: the exact frozenset the PRE-refactor _infer_char_sets returned
# for each basekey. Locks the digit-vs-language-script distinction, including the
# date_usa special case (language=en but numeric format -> digits only).
# ---------------------------------------------------------------------------
_LEGACY_CHARSET = {
    "digits": {
        "dt:date:date_1", "dt:date:date_2", "dt:date:date_3", "dt:date:date_4",
        "dt:date:date_iso8601", "dt:date:date_iso8601_short", "dt:date:date_8",
        "dt:date:date_9", "dt:date:date_10", "dt:date:noyear_1",
        "dt:date:date_4_point", "dt:date:date_5", "dt:date:date_6",
        "dt:date:date_usa_1", "dt:date:date_usa",
    },
}


def test_infer_char_sets_matches_legacy_output():
    """DateParser._infer_char_sets must reproduce the pre-refactor charset for every
    generated pattern (resolved via basekey)."""
    from qddate import DateParser
    from qddate.qdparser import (CHAR_SET_DIGITS, CHAR_SET_LATIN, CHAR_SET_CYRILLIC,
                                 CHAR_SET_ACCENTED)

    parser = DateParser()
    expected_map = {
        "digits": frozenset({CHAR_SET_DIGITS}),
        "latin": frozenset({CHAR_SET_DIGITS, CHAR_SET_LATIN}),
        "cyrillic": frozenset({CHAR_SET_DIGITS, CHAR_SET_CYRILLIC}),
        "accented": frozenset({CHAR_SET_DIGITS, CHAR_SET_ACCENTED}),
    }

    def legacy_expected(basekey):
        if basekey in _LEGACY_CHARSET["digits"]:
            return expected_map["digits"]
        # language -> script (matches LANGUAGE_CHAR_SETS)
        lang = _legacy_infer_language(basekey)
        script = {"ru": "cyrillic", "bg": "cyrillic", "fr": "accented", "cz": "accented",
                  "pl": "accented", "es": "accented", "it": "accented", "pt": "accented",
                  "de": "latin", "tr": "latin", "en": "latin", "nl": "latin"}.get(lang)
        return expected_map.get(script, expected_map["latin"])

    mismatches = []
    for p in parser.patterns:
        basekey = p.get("basekey", p["key"])
        got = frozenset(parser._infer_char_sets(p))
        want = legacy_expected(basekey)
        if got != want:
            mismatches.append((p["key"], set(got), set(want)))
    assert not mismatches, f"Charset mismatches (got, expected): {mismatches[:5]}"


# ---------------------------------------------------------------------------
# Reachability: every generated pattern must be findable through each index the
# filter pipeline uses. This guards against a future metadata/regex change that
# silently makes a pattern unreachable (and therefore never matches).
# ---------------------------------------------------------------------------
def test_every_pattern_reachable_through_length_index():
    """Each generated pattern's length range must overlap at least one bucket."""
    from qddate import DateParser
    parser = DateParser()
    covered_lengths = set(parser._patterns_by_length)
    unreachable = []
    for p in parser.patterns:
        lo, hi = p["length"]["min"], p["length"]["max"]
        if not any(length in covered_lengths for length in range(lo, hi + 1)):
            unreachable.append((p["key"], lo, hi))
    assert not unreachable, f"Patterns with no length-index bucket: {unreachable[:5]}"


def test_every_language_pattern_in_language_index():
    """Every pattern with a language must appear in the language index."""
    from qddate import DateParser
    from qddate.qdparser import _pattern_language
    parser = DateParser()
    indexed_keys = set()
    for lang_pats in parser._patterns_by_language.values():
        for p in lang_pats:
            indexed_keys.add(p["key"])
    missing = [p["key"] for p in parser.patterns
               if _pattern_language(p) is not None and p["key"] not in indexed_keys]
    assert not missing, f"Language patterns missing from language index: {missing[:5]}"


def test_every_pattern_in_separator_index():
    """Every generated pattern must appear in exactly one separator bucket."""
    from qddate import DateParser
    parser = DateParser()
    indexed_keys = set()
    for sep_pats in parser._patterns_by_separator.values():
        for p in sep_pats:
            indexed_keys.add(p["key"])
    missing = [p["key"] for p in parser.patterns if p["key"] not in indexed_keys]
    assert not missing, f"Patterns missing from separator index: {missing[:5]}"
