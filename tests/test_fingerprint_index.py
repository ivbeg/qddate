# -*- coding: utf-8 -*-
"""Tests for ``qddate.patterns.fingerprint`` (item #19, data layer)."""

from __future__ import annotations

import pytest

from qddate.patterns import ALL_PATTERNS, PATTERNS_BY_LANGUAGE
from qddate.patterns.fingerprint import (
    _PATTERN_FINGERPRINTS,
    CHAR_SET_ACCENTED,
    CHAR_SET_CYRILLIC,
    CHAR_SET_DIGITS,
    CHAR_SET_LATIN,
    CHAR_SET_SEPARATORS,
    FingerprintKey,
    candidate_keys_for,
    compute_pattern_fingerprint,
)

# ---------------------------------------------------------------------------
# Determinism + key shape
# ---------------------------------------------------------------------------

def test_fingerprint_key_is_namedtuple_with_six_fields():
    """``FingerprintKey`` is a hashable NamedTuple with exactly 6 fields."""
    assert FingerprintKey._fields == (
        "length_min", "length_max", "chars", "separator", "language", "year_format",
    )


@pytest.mark.parametrize("pat", [ALL_PATTERNS[0], ALL_PATTERNS[len(ALL_PATTERNS) // 2], ALL_PATTERNS[-1]])
def test_compute_pattern_fingerprint_is_deterministic(pat):
    """Calling twice on the same pattern dict yields equal FingerprintKeys."""
    fp_a = compute_pattern_fingerprint(pat)
    fp_b = compute_pattern_fingerprint(pat)
    assert fp_a == fp_b
    assert hash(fp_a) == hash(fp_b)


def test_compute_pattern_fingerprint_reads_length_range():
    """``length_min`` / ``length_max`` come straight from ``pattern['length']``."""
    pat = {
        "key": "x",
        "length": {"min": 5, "max": 12},
        "separator": "mixed",
        "language": None,
        "required_chars": frozenset({"digits"}),
    }
    fp = compute_pattern_fingerprint(pat)
    assert fp.length_min == 5
    assert fp.length_max == 12


def test_compute_pattern_fingerprint_reads_separator_and_language():
    """The helper trusts the pattern's pre-annotated fields."""
    pat = {
        "key": "x",
        "length": {"min": 0, "max": 0},
        "separator": "slash",
        "language": "de",
        "required_chars": frozenset({"digits"}),
    }
    fp = compute_pattern_fingerprint(pat)
    assert fp.separator == "slash"
    assert fp.language == "de"


def test_compute_pattern_fingerprint_year_format_noyear():
    """``noyear`` flag → ``"noyear"`` bucket."""
    pat = {
        "key": "x",
        "length": {"min": 5, "max": 5},
        "separator": "mixed",
        "language": None,
        "required_chars": frozenset({"digits"}),
        "noyear": True,
    }
    assert compute_pattern_fingerprint(pat).year_format == "noyear"


def test_compute_pattern_fingerprint_year_format_2digit():
    """``yearshort`` flag → ``"2digit"`` bucket."""
    pat = {
        "key": "dt:date:date_iso8601_short",
        "length": {"min": 6, "max": 8},
        "separator": "dash",
        "language": None,
        "required_chars": frozenset({"digits"}),
        "yearshort": True,
    }
    # Even though the key contains date_iso8601, yearshort wins → "2digit".
    assert compute_pattern_fingerprint(pat).year_format == "2digit"


def test_compute_pattern_fingerprint_year_format_4digit():
    """``date_iso8601*`` / ``date_9`` / ``date_10`` basekeys → ``"4digit"``."""
    for basekey in ("dt:date:date_iso8601", "dt:date:date_9", "dt:date:date_10"):
        pat = {
            "key": basekey,
            "length": {"min": 8, "max": 10},
            "separator": "dash" if "iso" in basekey else "dot",
            "language": None,
            "required_chars": frozenset({"digits"}),
        }
        assert compute_pattern_fingerprint(pat).year_format == "4digit", basekey


def test_compute_pattern_fingerprint_year_format_any():
    """Anything else → ``"any"``."""
    pat = {
        "key": "dt:date:date_2",
        "length": {"min": 8, "max": 10},
        "separator": "dot",
        "language": None,
        "required_chars": frozenset({"digits"}),
    }
    assert compute_pattern_fingerprint(pat).year_format == "any"


# ---------------------------------------------------------------------------
# Index coverage
# ---------------------------------------------------------------------------

def test_index_covers_every_pattern_in_all_patterns():
    """Every ``key`` in ``ALL_PATTERNS`` appears in exactly one index bucket."""
    bucketed_keys: set[str] = set()
    for fp_keys in _PATTERN_FINGERPRINTS.values():
        bucketed_keys.update(fp_keys)
    all_keys = {p["key"] for p in ALL_PATTERNS}
    missing = all_keys - bucketed_keys
    duplicates = sum(len(v) for v in _PATTERN_FINGERPRINTS.values()) - len(bucketed_keys)
    assert not missing, f"Patterns missing from index: {sorted(missing)[:5]}"
    assert duplicates == 0, "Index contains duplicate key references"


def test_index_size_is_bounded():
    """Sanity guard: index shouldn't blow up. ~100 buckets for current corpus."""
    # ALL_PATTERNS has 134 patterns, currently 80 unique fingerprints. The
    # guard allows generous headroom for adding patterns in future rounds.
    assert len(_PATTERN_FINGERPRINTS) <= 200, (
        f"Fingerprint index grew to {len(_PATTERN_FINGERPRINTS)} unique tuples; "
        "expected ~100. Re-audit before adding new patterns."
    )


def test_every_language_has_at_least_one_fingerprint():
    """Every supported language must appear in at least one fingerprint."""
    fp_languages = {fp.language for fp in _PATTERN_FINGERPRINTS}
    for lang in PATTERNS_BY_LANGUAGE:
        assert lang in fp_languages, f"Language {lang!r} missing from fingerprint index"


# ---------------------------------------------------------------------------
# Projections (legacy buckets are reachable from the index)
# ---------------------------------------------------------------------------

def test_legacy_length_bucket_is_a_projection():
    """The per-length bucket from the legacy pipeline is reconstructible."""
    for n in (5, 8, 10, 12):
        projected: set[str] = set()
        for fp, keys in _PATTERN_FINGERPRINTS.items():
            if fp.length_min <= n <= fp.length_max:
                projected.update(keys)
        assert projected, f"No patterns satisfy length={n}"


def test_legacy_separator_bucket_is_a_projection():
    """Patterns are bucketed by separator exactly once."""
    seen: dict[str, set[str]] = {}
    for fp, keys in _PATTERN_FINGERPRINTS.items():
        for key in keys:
            assert key not in seen, f"Pattern {key!r} in multiple separator buckets"
            seen[key] = {fp.separator}
    for key, seps in seen.items():
        assert len(seps) == 1, f"Pattern {key!r} has multiple separators: {seps}"


def test_legacy_language_bucket_is_a_projection():
    """Patterns' language field matches the per-language pattern list."""
    for lang, pats in PATTERNS_BY_LANGUAGE.items():
        lang_keys = {p["key"] for p in pats}
        # At least one fingerprint per language.
        lang_fps = [fp for fp in _PATTERN_FINGERPRINTS if fp.language == lang]
        assert lang_fps, f"No fingerprints with language={lang!r}"
        # Every base pattern shows up in at least one fingerprint.
        for key in lang_keys:
            in_any = any(key in v for v in _PATTERN_FINGERPRINTS.values())
            assert in_any, f"Pattern {key!r} ({lang}) not in any fingerprint"


# ---------------------------------------------------------------------------
# Char-set filter behaviour (the trickiest dimension)
# ---------------------------------------------------------------------------

def test_chars_match_pure_digits_subset():
    """``digits``-only patterns are kept for any text that has digits."""
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="slash",
        detected_language=None,
        detected_year_format="4digit",
    )
    assert keys, "Expected at least one candidate for a typical 10-char numeric text"


def test_chars_match_accented_substitutes_for_latin():
    """Patterns requiring ``CHAR_SET_ACCENTED`` are kept when text has ``CHAR_SET_LATIN``."""
    # Find a pattern whose chars require accented Latin (e.g. French).
    fr_pattern = None
    for fp, keys in _PATTERN_FINGERPRINTS.items():
        if CHAR_SET_ACCENTED in fp.chars and fp.language == "fr":
            fr_pattern = next(iter(keys))
            break
    if fr_pattern is None:
        pytest.skip("No French accented-required pattern found")
    # Text has LATIN only (no accented chars), but should still include the French pattern.
    keys = candidate_keys_for(
        text_length=11,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_LATIN, CHAR_SET_SEPARATORS}),
        detected_separator="space",
        detected_language="fr",
        detected_year_format="any",
    )
    assert fr_pattern in keys, (
        "French accented pattern should still match via ACCENTED→LATIN substitution"
    )


def test_chars_match_cyrillic_required_text_without_cyrillic_rejected():
    """Russian/Cyrillic-required patterns are filtered out when text has no Cyrillic."""
    keys = candidate_keys_for(
        text_length=15,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_LATIN, CHAR_SET_SEPARATORS}),
        detected_separator="space",
        detected_language=None,
        detected_year_format="any",
    )
    # No Cyrillic-required pattern should leak in.
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if CHAR_SET_CYRILLIC in fp.chars:
            assert not (bucket_keys & keys), (
                f"Cyrillic-required pattern {fp.language!r} reached a non-Cyrillic text"
            )


# ---------------------------------------------------------------------------
# Year-format filter behaviour
# ---------------------------------------------------------------------------

def test_year_format_unknown_keeps_all_buckets():
    """When detected year format is unknown, every bucket is reachable.

    Each year-format bucket has its own length sweet-spot, so we run four
    independent calls (one per bucket) and assert each reaches at least
    one of its kind.
    """
    # "any" bucket: typical 10-char numeric date.
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="slash",
        detected_language=None,
        detected_year_format="unknown",
    )
    seen_any = any(
        fp.year_format == "any" and bucket_keys & keys
        for fp, bucket_keys in _PATTERN_FINGERPRINTS.items()
    )
    assert seen_any, "year_format='any' bucket unreachable when detection='unknown'"

    # "4digit" bucket: 10-char ISO-style date.
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="dash",
        detected_language=None,
        detected_year_format="unknown",
    )
    seen_4digit = any(
        fp.year_format == "4digit" and bucket_keys & keys
        for fp, bucket_keys in _PATTERN_FINGERPRINTS.items()
    )
    assert seen_4digit, "year_format='4digit' bucket unreachable when detection='unknown'"

    # "2digit" bucket: 8-char short-year date (``date_iso8601_short``).
    keys = candidate_keys_for(
        text_length=8,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="dash",
        detected_language=None,
        detected_year_format="unknown",
    )
    seen_2digit = any(
        fp.year_format == "2digit" and bucket_keys & keys
        for fp, bucket_keys in _PATTERN_FINGERPRINTS.items()
    )
    assert seen_2digit, "year_format='2digit' bucket unreachable when detection='unknown'"

    # "noyear" bucket: 5-char ``"05.12"`` style.
    keys = candidate_keys_for(
        text_length=5,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="dot",
        detected_language=None,
        detected_year_format="unknown",
    )
    seen_noyear = any(
        fp.year_format == "noyear" and bucket_keys & keys
        for fp, bucket_keys in _PATTERN_FINGERPRINTS.items()
    )
    assert seen_noyear, "year_format='noyear' bucket unreachable when detection='unknown'"


def test_year_format_4digit_excludes_noyear_patterns():
    """When text has a 4-digit year, no-year patterns are filtered out."""
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="dot",
        detected_language=None,
        detected_year_format="4digit",
    )
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if fp.year_format == "noyear":
            assert not (bucket_keys & keys), (
                f"noyear pattern reached a text with a 4-digit year: {bucket_keys & keys}"
            )


def test_year_format_2digit_keeps_noyear_patterns():
    """Short texts (no 4-digit year) must still reach no-year patterns (e.g. ``"05.12"``)."""
    keys = candidate_keys_for(
        text_length=5,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="dot",
        detected_language=None,
        detected_year_format="2digit",
    )
    # At least one no-year pattern should be in the candidate set.
    no_year_keys: set[str] = set()
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if fp.year_format == "noyear":
            no_year_keys.update(bucket_keys)
    assert no_year_keys & keys, (
        "No-year patterns dropped from the candidate set on a 5-char text"
    )


# ---------------------------------------------------------------------------
# Language filter behaviour
# ---------------------------------------------------------------------------

def test_language_match_returns_wildcard_patterns():
    """Language-agnostic patterns (``language=None``) reach every text."""
    # Use a 10-char numeric+Cyrillic+dot text. Russian is detected; numeric
    # wildcards (no language, separator="dot", length 8–10) must still pass.
    # ``date_2`` is the canonical dot-separator wildcard; ``date_10`` is
    # also dot-separator and 4-digit. Both have language=None and the same
    # chars subset as text_chars.
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_CYRILLIC, CHAR_SET_SEPARATORS}),
        detected_separator="dot",
        detected_language="ru",
        detected_year_format="4digit",
    )
    # A numeric-language-agnostic pattern must be there.
    wildcard_keys: set[str] = set()
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if fp.language is None:
            wildcard_keys.update(bucket_keys)
    assert wildcard_keys & keys, (
        "Language-agnostic patterns were filtered out by language match"
    )


def test_language_allowlist_admits_explicit_codes():
    """A caller-supplied ``language_allowlist`` admits patterns outside detection."""
    # Use a 12-char German date like "1 Januar 2024" (13 actually) — text needs
    # Latin letters for the German month-name patterns to clear the charset
    # filter, and digits for the year.
    keys_no_allow = candidate_keys_for(
        text_length=13,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_LATIN, CHAR_SET_SEPARATORS}),
        detected_separator="space",
        detected_language=None,
        detected_year_format="4digit",
    )
    keys_with_allow = candidate_keys_for(
        text_length=13,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_LATIN, CHAR_SET_SEPARATORS}),
        detected_separator="space",
        detected_language=None,
        detected_year_format="4digit",
        language_allowlist=frozenset({"de"}),
    )
    # The allow-listed run should be a superset of the no-allow run
    # (same dimensions, plus German patterns).
    assert keys_no_allow <= keys_with_allow, (
        "Allow-listed run dropped patterns the no-allow run accepted"
    )
    # And the allow-listed run should include German patterns.
    de_keys: set[str] = set()
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if fp.language == "de":
            de_keys.update(bucket_keys)
    assert de_keys & keys_with_allow, (
        "Allow-list didn't admit German patterns when detection returned None"
    )


def test_language_match_unrelated_language_excluded():
    """Patterns of a different language than detected are excluded when not allowed."""
    keys = candidate_keys_for(
        text_length=11,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_CYRILLIC, CHAR_SET_SEPARATORS}),
        detected_separator="space",
        detected_language="ru",
        detected_year_format="any",
    )
    # French patterns (which require accented Latin, not Cyrillic) shouldn't sneak in.
    for fp, bucket_keys in _PATTERN_FINGERPRINTS.items():
        if fp.language == "fr":
            assert not (bucket_keys & keys), (
                f"French pattern reached a Russian detected text: {bucket_keys & keys}"
            )


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

def test_candidate_keys_for_returns_frozenset():
    """The return type is a hashable, immutable ``frozenset[str]``."""
    keys = candidate_keys_for(
        text_length=10,
        text_chars=frozenset({CHAR_SET_DIGITS, CHAR_SET_SEPARATORS}),
        detected_separator="slash",
        detected_language=None,
        detected_year_format="4digit",
    )
    assert isinstance(keys, frozenset)
    assert all(isinstance(k, str) for k in keys)
