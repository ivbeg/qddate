"""Declared ``length`` bounds versus strings generated from each grammar.

``DateParser`` skips a pattern for any input whose length lies outside the
pattern's declared ``length`` ``min``/``max``, before the grammar runs. A bound
narrower than the grammar silently drops valid inputs: ``dt:date:date_rus``
declared ``min=11`` so ``9 Мая 1998`` (10 characters) never matched, and
``dt:date:weekday_rus`` declared ``max=20`` while every real input with the
required ``года`` is longer.

The test renders each base grammar the way dates are written: one space
between words, no space before punctuation, none around ``/`` and ``-`` and
none after ``.``/``:`` before a digit; a second rendering drops the space after
every ``.`` (``1.мая.1945``). Leaves take their shortest and longest
form (``1``/``11`` for a day, ``Мая``/``Сентября`` for a month) and every
optional part is tried both absent and present. A rendering counts only when
the grammar consumes all of it and ``DateParser`` can build a datetime from the
result (so a Russian date without its optional year does not set the minimum).
"""
import pyparsing as pp
import pytest

from qddate import DateParser
from qddate.patterns import ALL_PATTERNS

# The grammar also accepts the digit groups separated by spaces ("15 12 2009");
# the patterns exist for the compact form and declare its exact length.
_EXEMPT = frozenset({
    "dt:date:date_5",
    "dt:date:date_6",
})

# Bounds known to be narrower than the grammar, each with the reason it stays
# narrow. Remove an entry once its bounds are fixed; the test fails on stale
# entries. Widening a bound is safe since ``match()`` prefers the candidate
# that consumes the most input: before, the length bonus in
# ``_calculate_pattern_priority`` let a pattern whose widened ``max`` covered
# ``22 Января 2003 14:15:01`` win with a partial match and drop the time.
_KNOWN_NARROW = frozenset()

_MAX_VARIANTS = 4096

# Tokens written without a space before them.
_ATTACHED = frozenset({",", ".", ":", ")", "]", "/", "-", " ", "st", "nd", "rd", "th"})


def _variants(expr):
    """Return the token tuples ``expr`` can produce (shortest/longest leaves,
    every optional part absent and present)."""
    if isinstance(expr, pp.White):
        return [(" ",)]
    if isinstance(expr, (pp.LineStart, pp.StringStart, pp.Empty)):
        # Match without consuming text (``:t_right`` variants start with one).
        return [()]
    if isinstance(expr, pp.Word):
        char = "1" if "1" in expr.initChars else sorted(expr.initChars)[0]
        shortest = max(expr.minLen, 1)
        longest = expr.maxLen if expr.maxLen < 100 else shortest
        return list(dict.fromkeys([(char * shortest,), (char * longest,)]))
    if isinstance(expr, pp.Regex):
        # Month and weekday lists compile to plain alternations.
        if expr.pattern == "[.,]":
            options = [".", ","]
        else:
            options = [o.replace("\\", "") for o in expr.pattern.split("|")]
        return list(dict.fromkeys([(min(options, key=len),), (max(options, key=len),)]))
    if isinstance(expr, (pp.Literal, pp.CaselessLiteral)):
        return [(expr.match,)]
    if isinstance(expr, pp.Opt):
        return [()] + _variants(expr.expr)
    if isinstance(expr, (pp.MatchFirst, pp.Or)):
        return list(dict.fromkeys(v for alt in expr.exprs for v in _variants(alt)))
    if isinstance(expr, pp.And):
        out = [()]
        for part in expr.exprs:
            out = list(dict.fromkeys(a + b for a in out for b in _variants(part)))
            assert len(out) <= _MAX_VARIANTS
        return out
    if isinstance(expr, pp.ParseElementEnhance):
        return _variants(expr.expr)
    raise TypeError(f"no rendering for {type(expr).__name__}")


def _render(tokens, tight_dots=False):
    """Join tokens; ``tight_dots`` also drops the space after every ``.``
    (``1.мая.1945`` as well as ``1. мая. 1945``)."""
    text, prev = "", None
    for tok in tokens:
        if (prev is None or tok in _ATTACHED or prev in (" ", "/", "-")
                or (prev in (".", ":") and tok[:1].isdigit())
                or (tight_dots and prev == ".")):
            text += tok
        else:
            text += " " + tok
        prev = tok
    return text


def _usable_lengths(parser, pattern):
    """Lengths of the renderings that ``pattern`` fully parses into a datetime."""
    grammar = pattern["pattern"]
    lengths = set()
    texts = {_render(tokens, tight) for tokens in _variants(grammar) for tight in (False, True)}
    for text in texts:
        found = next(grammar.scan_string(text, max_matches=1), None)
        if found is None or found[1] != 0 or found[2] != len(text):
            continue
        if parser._build_datetime({"values": found[0], "pattern": pattern}) is None:
            continue
        lengths.add(len(text))
    return lengths


@pytest.fixture(scope="module")
def grammar_lengths():
    parser = DateParser(generate=False)
    return {p["key"]: _usable_lengths(parser, p) for p in ALL_PATTERNS}


def test_every_pattern_renders_a_datetime(grammar_lengths):
    """Each grammar yields a parseable date; a pattern without ``day``/``month``
    result names (``weekday_rus`` before the fix) matched but never parsed."""
    empty = sorted(key for key, lengths in grammar_lengths.items() if not lengths)
    assert empty == []


def test_declared_lengths_cover_grammar(grammar_lengths):
    too_narrow = {}
    for p in ALL_PATTERNS:
        key = p["key"]
        lengths = grammar_lengths[key]
        if key in _EXEMPT or not lengths:
            continue
        shortest, longest = min(lengths), max(lengths)
        if shortest < p["length"]["min"] or longest > p["length"]["max"]:
            too_narrow[key] = (p["length"]["min"], p["length"]["max"], shortest, longest)
    unexpected = {k: v for k, v in too_narrow.items() if k not in _KNOWN_NARROW}
    assert unexpected == {}, (
        "Declared (min, max) narrower than the grammar's (shortest, longest): "
        f"{unexpected}")
    stale = sorted(_KNOWN_NARROW - set(too_narrow))
    assert stale == [], f"Remove fixed patterns from _KNOWN_NARROW: {stale}"


def test_exempt_and_known_keys_exist():
    keys = {p["key"] for p in ALL_PATTERNS}
    assert sorted((_EXEMPT | _KNOWN_NARROW) - keys) == []
