"""Lock-in test for ``qddate.patterns.ALL_PATTERNS`` immutability.

After this change ``annotate_patterns()`` stamps every field
``__generate()`` would have stamped, so constructing any number of
``DateParser()`` instances must not mutate the observable fields of
``ALL_PATTERNS`` (``required_chars``, ``language``, ``separator``,
``basekey``, etc.).

The previous behaviour was a real footgun: every ``DateParser`` construction
called ``__generate()`` which wrote ``pat["required_chars"]`` to each base
pattern. The defensive copy in ``DateParser.__init__`` saved end users, but
anyone reading ``ALL_PATTERNS`` directly during construction saw stale data.
"""


from qddate import DateParser
from qddate.patterns import ALL_PATTERNS, annotate_patterns

# Fields that ``__generate()`` used to mutate on the source patterns. The
# immutability contract is that these stay stable across DateParser() calls.
_MUTABLE_FIELDS = ("required_chars", "language", "separator", "format")


def _snapshot_fields():
    """Read every observable field of every pattern into a JSON-friendly tuple."""
    rows = []
    for p in ALL_PATTERNS:
        row = [p["key"]]
        for f in _MUTABLE_FIELDS:
            v = p.get(f)
            # frozenset is not orderable; convert to sorted tuple.
            if isinstance(v, frozenset):
                v = tuple(sorted(v))
            row.append(v)
        rows.append(tuple(row))
    return tuple(rows)


def test_all_patterns_unchanged_after_repeated_dateparser_construction():
    """Construct 5 DateParser() instances; ALL_PATTERNS must be byte-identical."""
    snapshot = _snapshot_fields()
    for _ in range(5):
        DateParser()
    assert _snapshot_fields() == snapshot, (
        "ALL_PATTERNS was mutated by DateParser construction. "
        "This was the original __generate() mutation hazard."
    )


def test_generate_does_not_mutate_all_patterns():
    """Calling __generate() directly leaves the observable fields untouched."""
    snapshot = _snapshot_fields()
    parser = DateParser(generate=False)
    parser._DateParser__generate(base_only=False)
    parser._DateParser__generate(base_only=False)
    assert _snapshot_fields() == snapshot


def test_annotate_patterns_is_idempotent():
    """annotate_patterns can run twice without changing the patterns."""
    snapshot = _snapshot_fields()
    annotate_patterns(ALL_PATTERNS)
    annotate_patterns(ALL_PATTERNS)
    assert _snapshot_fields() == snapshot


def test_required_chars_already_stamped_at_import():
    """Every pattern must carry required_chars after import (no first-parse stamp)."""
    missing = [p["key"] for p in ALL_PATTERNS if "required_chars" not in p]
    assert missing == [], (
        f"Patterns missing required_chars at import time: {missing}. "
        "annotate_patterns() must stamp every pattern."
    )
