# -*- coding: utf-8 -*-
"""Precomputed pattern fingerprint index.

The matcher used to build per-instance buckets on every ``DateParser()``
construction (``_patterns_by_length``, ``_patterns_by_separator``,
``_patterns_by_language``, ``_patterns_by_year_format``, …) and then walk
them with branching merge logic in ``_filter_patterns_hierarchical``.

This module precomputes, **once at import time**, the same data as a single
dictionary indexed by a ``FingerprintKey`` namedtuple. The key captures
every dimension the existing 6-level filter cares about:

- ``length_min`` / ``length_max`` — the pattern's documented length range.
- ``chars`` — the pattern's required character sets (``CHAR_SET_DIGITS``,
  ``CHAR_SET_LATIN``, ``CHAR_SET_CYRILLIC``, ``CHAR_SET_ACCENTED``,
  ``CHAR_SET_SEPARATORS``). ``frozenset`` so the key is hashable.
- ``separator`` — one of ``"slash"``, ``"dot"``, ``"dash"``, ``"space"``,
  ``"none"``, ``"mixed"`` (matches ``_PATTERN_METADATA``).
- ``language`` — the pattern's explicit language code (``"en"``, ``"ru"``,
  …) or ``None`` for language-agnostic numeric patterns.
- ``year_format`` — ``"4digit"``, ``"2digit"``, ``"noyear"``, or ``"any"``
  (matches ``_build_year_format_index``).

A consumer can ask for the candidate set as a single dict walk:

>>> candidate_keys = candidate_keys_for(text_length=10, text_chars=frozenset({"digits", "separators"}),
...                                     detected_separator="slash", detected_language=None,
...                                     detected_year_format="4digit")

The result is a **superset-or-equal** of the existing 6-level filter for
the same input. The filter pipeline keeps running unchanged in this
release; a future round wires the candidate set as the consumer of
``match()`` with the existing pipeline as the parity fallback.

See ``openspec/changes/fingerprint-based-matcher/design.md`` for the full
design rationale, the per-dimension projection rules, and the rationale for
splitting the data layer from the consumer wiring.
"""

from __future__ import annotations

from typing import FrozenSet, Mapping, NamedTuple, Optional

from . import ALL_PATTERNS, annotate_patterns

# Character-set constants — re-exported here so this module is self-contained
# (callers don't have to import qddate.qdparser just to read the flags).
CHAR_SET_DIGITS = "digits"
CHAR_SET_LATIN = "latin"
CHAR_SET_CYRILLIC = "cyrillic"
CHAR_SET_ACCENTED = "accented"
CHAR_SET_SEPARATORS = "separators"


class FingerprintKey(NamedTuple):
    """A pattern's precomputed fingerprint across every filter dimension.

    Equality + hashing are structural — two patterns with the same
    fingerprint are interchangeable as candidates, which is exactly what
    the index relies on for bucketing.
    """

    length_min: int
    length_max: int
    chars: FrozenSet[str]
    separator: str
    language: Optional[str]
    year_format: str


def _pattern_year_format(pattern: dict) -> str:
    """Derive the pattern's year-format bucket, matching ``_build_year_format_index``.

    The rules are:
      1. ``noyear`` flag → ``"noyear"``
      2. ``yearshort`` flag → ``"2digit"``
      3. basekey in ``{date_iso8601, date_9, date_10}`` → ``"4digit"``
      4. else → ``"any"``

    This mirrors the bucket assignment in ``DateParser._build_year_format_index``
    so the legacy bucket is a projection of the fingerprint index.
    """
    if pattern.get("noyear", False):
        return "noyear"
    if pattern.get("yearshort", False):
        return "2digit"
    basekey = pattern.get("basekey", pattern.get("key", ""))
    if any(token in basekey for token in ("date_iso8601", "date_9", "date_10")):
        return "4digit"
    return "any"


def _pattern_length_range(pattern: dict) -> tuple[int, int]:
    """Return ``(length_min, length_max)`` from the pattern's length spec."""
    length = pattern.get("length") or {}
    return (int(length.get("min", 0)), int(length.get("max", 0)))


def compute_pattern_fingerprint(pattern: dict) -> FingerprintKey:
    """Return the deterministic fingerprint tuple for one pattern.

    Pure function — no side effects, no shared state. Calling twice on the
    same pattern dict yields equal ``FingerprintKey`` instances (verified by
    the determinism test in ``tests/test_fingerprint_index.py``).

    Reads ``language``, ``separator`` and ``required_chars`` from the
    pattern. ``annotate_patterns()`` stamps those fields onto every entry
    of ``ALL_PATTERNS`` at import time, so this helper can rely on them
    being present for canonical patterns; tests cover the
    not-yet-annotated fallback (uses ``_PATTERN_METADATA`` for
    language/separator, infers ``required_chars`` from the pattern body).
    """
    length_min, length_max = _pattern_length_range(pattern)
    chars = frozenset(pattern.get("required_chars") or frozenset({CHAR_SET_DIGITS}))
    separator = pattern.get("separator") or "mixed"
    language = pattern.get("language")
    year_format = _pattern_year_format(pattern)
    return FingerprintKey(
        length_min=length_min,
        length_max=length_max,
        chars=chars,
        separator=separator,
        language=language,
        year_format=year_format,
    )


def _build_index() -> Mapping[FingerprintKey, FrozenSet[str]]:
    """Build the module-level fingerprint → pattern-keys index.

    Stamps ``language`` / ``separator`` / ``required_chars`` onto a private
    copy of ``ALL_PATTERNS`` so the fingerprint derivation is robust against
    patterns that haven't been pre-annotated. The canonical ``ALL_PATTERNS``
    itself is already annotated at import time in ``qddate/patterns/__init__.py``,
    so the ``annotate_patterns`` call here is a defensive no-op for the
    common case and a safety net for callers who build a fresh list.
    """
    local_patterns = [dict(p) for p in ALL_PATTERNS]
    annotate_patterns(local_patterns)
    index: dict[FingerprintKey, set[str]] = {}
    for pat in local_patterns:
        fp = compute_pattern_fingerprint(pat)
        index.setdefault(fp, set()).add(pat["key"])
    return {fp: frozenset(keys) for fp, keys in index.items()}


# Module-level singleton. Built once at import; ~700 unique fingerprints for
# the current ALL_PATTERNS corpus.
_PATTERN_FINGERPRINTS: Mapping[FingerprintKey, FrozenSet[str]] = _build_index()


def candidate_keys_for(
    *,
    text_length: int,
    text_chars: FrozenSet[str],
    detected_separator: str,
    detected_language: Optional[str],
    detected_year_format: str,
    language_allowlist: Optional[FrozenSet[str]] = None,
    text_has_letters: bool = False,
) -> FrozenSet[str]:
    """Return the set of pattern keys whose fingerprint is satisfied by the input.

    A pattern is satisfied when:

    - ``length_min ≤ text_length ≤ length_max``
    - the pattern's ``chars`` are a subset of ``text_chars``, with the
      same accented→Latin substitution the existing 6-level filter uses:
      a pattern whose ``chars`` contains ``CHAR_SET_ACCENTED`` is still
      satisfied when the text carries ``CHAR_SET_LATIN`` instead.
    - the pattern's ``separator`` is either ``"mixed"`` (wildcard) or
      equal to ``detected_separator``; **or** ``text_has_letters`` is
      ``True`` and ``detected_separator`` is ``"space"`` or ``"mixed"``
      and the pattern's ``language`` is non-``None`` (the legacy
      "language tokens survive ambiguous separator" rule).
    - the pattern's ``language`` is either ``None`` (language-agnostic) or
      equal to ``detected_language``, or — when ``language_allowlist`` is
      supplied — equal to one of the allow-listed codes.
    - the pattern's ``year_format`` matches ``detected_year_format``,
      ``"any"`` (wildcard), or — when the detected format isn't
      ``"4digit"`` — ``"noyear"`` (so short texts like ``"05.12"``
      keep reaching no-year patterns, matching the existing
      ``_filter_patterns_hierarchical`` rule).

    The function performs **a single walk over the index**, returning the
    union of all matching buckets. ``frozenset[str]`` is the canonical
    return type for downstream consumers that need a hashable, immutable
    candidate set.

    :param text_length: ``len(text)`` for the input being matched.
    :param text_chars: the text's character-set flags from
        ``scan_char_sets`` (``qddate.qdparser.scan_char_sets``).
    :param detected_separator: one of ``"slash"``, ``"dot"``, ``"dash"``,
        ``"space"``, ``"none"``, ``"mixed"``.
    :param detected_language: the language code returned by
        ``_detect_language`` (or ``None`` if no high-confidence detection).
    :param detected_year_format: one of ``"4digit"``, ``"2digit"``,
        ``"unknown"`` (mapped to ``"any"`` here), ``"noyear"``.
    :param language_allowlist: optional caller-supplied allow-list
        (intersected with the detected-language rule so the German "Juli"
        regression fix is preserved).
    :param text_has_letters: when ``True`` and the detected separator is
        ``"space"`` or ``"mixed"``, language-specific patterns with any
        separator reach the candidate set (the legacy "language tokens
        survive ambiguous separator" rule). Default ``False`` keeps the
        pure-intersection semantics.
    """
    # Patterns with ``separator == "mixed"`` are wildcards; they accept
    # every detected separator (matches the existing pipeline behaviour).
    # When ``text_has_letters`` is set and the detected separator is
    # "space" or "mixed", language-specific patterns (any separator) are
    # also kept — the legacy "language tokens survive ambiguous separator"
    # rule.
    def sep_match(fp_sep: str, fp_lang: Optional[str]) -> bool:
        if fp_sep == "mixed" or fp_sep == detected_separator:
            return True
        if (
            text_has_letters
            and fp_lang is not None
            and detected_separator in ("space", "mixed")
        ):
            return True
        return False

    # Language rule: language-agnostic patterns (``language is None``)
    # always match; language-specific patterns match if the detected
    # language equals the pattern's language, or if a caller allow-list
    # explicitly admits it.
    def lang_match(fp_lang: Optional[str]) -> bool:
        if fp_lang is None:
            return True
        if detected_language is not None and fp_lang == detected_language:
            return True
        if language_allowlist is not None and fp_lang in language_allowlist:
            return True
        return False

    # Year-format rule: matches ``_filter_patterns_hierarchical`` exactly.
    # When detection is "unknown", the existing pipeline skips the
    # year-format filter entirely (every bucket stays eligible, including
    # ``"noyear"``). When detection is "4digit", only "4digit" + "any" pass
    # (no-year excluded). When detection is "2digit" or "noyear", the
    # rule is symmetric.
    def year_match(fp_year: str) -> bool:
        if fp_year == "any":
            return True
        if detected_year_format == "unknown":
            return True
        if detected_year_format == "4digit":
            return fp_year == "4digit"
        if detected_year_format == "2digit":
            return fp_year in ("2digit", "noyear")
        if detected_year_format == "noyear":
            return fp_year in ("noyear", "2digit")
        return False

    # Charset rule: the pattern's required set must be a subset of the
    # text's char sets, with ``CHAR_SET_ACCENTED`` substitutable for
    # ``CHAR_SET_LATIN`` (matches the existing pipeline).
    def chars_match(fp_chars: FrozenSet[str]) -> bool:
        if not fp_chars:
            return True
        if fp_chars <= text_chars:
            return True
        # Accented → Latin substitution
        if (
            CHAR_SET_ACCENTED in fp_chars
            and CHAR_SET_LATIN in text_chars
            and (fp_chars - {CHAR_SET_ACCENTED}) <= text_chars
        ):
            return True
        return False

    out: set[str] = set()
    for fp, keys in _PATTERN_FINGERPRINTS.items():
        if fp.length_min > text_length or fp.length_max < text_length:
            continue
        if not chars_match(fp.chars):
            continue
        if not sep_match(fp.separator, fp.language):
            continue
        if not lang_match(fp.language):
            continue
        if not year_match(fp.year_format):
            continue
        out.update(keys)
    return frozenset(out)


__all__ = [
    "CHAR_SET_DIGITS",
    "CHAR_SET_LATIN",
    "CHAR_SET_CYRILLIC",
    "CHAR_SET_ACCENTED",
    "CHAR_SET_SEPARATORS",
    "FingerprintKey",
    "compute_pattern_fingerprint",
    "candidate_keys_for",
]


# Convenience re-exports: ``qddate.patterns._PATTERN_FINGERPRINTS`` mirrors
# the private module-level singleton so consumers don't reach into this
# sub-module's private names.
_PATTERN_FINGERPRINTS_PUBLIC = _PATTERN_FINGERPRINTS
