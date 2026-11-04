"""The checks ``match()`` runs before a candidate grammar.

Each candidate is parsed at position 0 only (``scan_string`` used to try
every later position of a text that does not start with a date). Before
that, a grammar is skipped when the text lacks what any match needs: a
character the date can start with, or a month or weekday name the grammar
requires (``qddate.qdparser._grammar_needs``). Text that is not a date
("Comments (12)") used to run hundreds of grammars, 5 to 50 ms per call.

The checks may only skip grammars that cannot match. The tests below render
every grammar, compare results with the checks switched off, and count the
grammars run on text that is not a date.
"""
import datetime

import pytest

import qddate.qdparser as qdparser
from qddate import DateParser
from tests.test_fingerprint_parity import _PROBE_STRINGS
from tests.test_pattern_lengths import _render, _variants

# Text without a date, as found in the HTML text nodes a scraper feeds in.
_NOT_DATES = [
    "Comments (12)",
    "Page 2 of 10",
    "© 2022 Company",
    "Price: 1 200 руб.",
    "Read more »",
    "+7 495 123-45-67",
    "Опубликовано 5 мая 2022",
    "Some random text node 123",
    "15 комментариев",
    "评论 (12)",
    "共 2022 条",
    "1 2 3 4 5",
    # Leading whitespace: scan_string skipped it before a match and the match
    # was dropped, except for "\n" before a ``:t_right`` variant.
    " 01.12.2009",
    "\n01.12.2009",
    "\t5 May 2022",
    " 2009/12/01 10:20",
]

# Texts that start with neither a digit nor a month or weekday name: no
# grammar can match them, so none may run.
_NO_GRAMMAR_RUNS = [
    "Comments (12)",
    "Page 2 of 10",
    "© 2022 Company",
    "Price: 1 200 руб.",
    "Read more »",
    "+7 495 123-45-67",
    "Опубликовано 5 мая 2022",
    # "nd" in "random" satisfied the ordinal suffix of date_eng2, whose
    # alternatives both need a month name.
    "Some random text node 123",
    "评论 (12)",
]


@pytest.fixture(scope="module")
def parser():
    return DateParser()


def _grammars_run(parser, text):
    """Return how many grammars ``parser.match(text)`` runs."""
    run = []
    anchored = parser._anchored

    def counting(grammar):
        run.append(grammar)
        return anchored(grammar)

    parser._anchored = counting
    try:
        parser.match(text)
    finally:
        del parser._anchored
    return len(run)


def test_every_rendered_date_passes_its_grammar_checks(parser):
    """A text a grammar matches at position 0 always has what it needs.

    Renders every generated grammar (shortest and longest leaves, optional
    parts absent and present; see ``tests/test_pattern_lengths.py``).
    """
    cache: dict = {}
    skipped = []
    for pattern in parser.patterns:
        grammar = pattern["pattern"]
        located = qdparser.Located(grammar)
        texts = {_render(tokens, tight_dots)
                 for tokens in _variants(grammar) for tight_dots in (False, True)}
        for text in sorted(texts):
            try:
                result = located.parse_string(text)
            except qdparser.ParseBaseException:
                continue
            if result.locn_start != 0:
                continue
            if not qdparser._may_match(grammar, text, cache, {}):
                skipped.append((pattern["key"], text))
    assert skipped == []


def test_month_name_grammars_need_a_month_name(parser):
    """The analysis reaches the month list of every month-name grammar."""
    cache: dict = {}
    needs = qdparser._grammar_needs(
        next(p["pattern"] for p in parser.patterns if p["key"] == "dt:date:date_eng1"), cache)
    assert needs.words
    assert any(rx.search("May") for regexes in needs.words for rx in regexes)
    numeric = qdparser._grammar_needs(
        next(p["pattern"] for p in parser.patterns if p["key"] == "dt:date:date_1"), cache)
    assert numeric.words == frozenset()
    assert numeric.first == frozenset("0123456789")


@pytest.mark.parametrize("text", _NO_GRAMMAR_RUNS)
def test_text_without_a_date_runs_no_grammar(parser, text):
    assert _grammars_run(parser, text) == 0
    assert parser.match(text) is None


def test_a_date_runs_few_grammars(parser):
    assert _grammars_run(parser, "5 May 2022") <= 10
    assert _grammars_run(parser, "12.03.1999 10:20") <= 10
    assert _grammars_run(parser, "2022年5月5日") <= 10
    assert _grammars_run(parser, "May 5") <= 10


@pytest.mark.parametrize("flags", [
    {},
    {"noprefix": True},
    {"nolanguagefilter": True},
    {"allow_no_year": False},
])
@pytest.mark.parametrize("checks", ["needs", "heads", "both"])
def test_checks_change_no_result(parser, monkeypatch, flags, checks):
    """``match_all()`` gives the same results with the checks switched off.

    ``needs`` are the first character and words a grammar needs; ``heads``
    skip a generated variant when the date (or time) it starts with does
    not match on its own.
    """
    texts = _PROBE_STRINGS + _NOT_DATES

    def results():
        return [
            [(m["pattern"]["key"], m["values"].as_dict()) for m in parser.match_all(text, **flags)]
            for text in texts
        ]

    with_checks = results()
    if checks in ("needs", "both"):
        monkeypatch.setattr(qdparser, "_may_match", lambda *args: True)
        monkeypatch.setattr(qdparser, "_select_candidates",
                            lambda plan, text, found: list(plan.pats))
    if checks in ("heads", "both"):
        monkeypatch.setattr(parser, "_requires", {})
    assert results() == with_checks


def test_variants_require_the_grammar_they_start_with(parser):
    """Each generated variant starts with the grammar ``_requires`` names, so
    a text that grammar does not match is not a match of the variant."""
    time_any = qdparser.BASE_TIME_PATTERNS["pat:time:any"]
    by_key = parser._patterns_by_key
    date = by_key["dt:date:date_1"]["pattern"]
    assert parser._requires["dt:date:date_1:time_1"] == (date,)
    assert parser._requires["dt:date:date_1:time_1:t_right"] == (
        date, by_key["dt:date:date_1:time_1"]["pattern"])
    assert parser._requires["dt:date:date_1:t_right"] == (date,)
    assert parser._requires["dt:date:date_1:time_left"] == (time_any,)
    # Every variant except the date alone ("dt:date:date_1").
    assert set(parser._requires) == {
        p["key"] for p in parser.patterns if p["key"] != p["basekey"]}


@pytest.mark.parametrize("text", [
    "5 May 2022 10:20, more text",
    "10:20 5 May 2022",
    "01.12.2009 garbage",
    "2022-05-05T10:00:00+03:00",
])
def test_variants_run_once_per_text(parser, text):
    """No grammar is parsed twice for one text."""
    run = []
    anchored = parser._anchored

    def counting(grammar):
        run.append(id(grammar))
        return anchored(grammar)

    parser._anchored = counting
    try:
        parser.match_all(text)
    finally:
        del parser._anchored
    assert len(run) == len(set(run))


@pytest.mark.parametrize("text, expected", [
    ("5\tMay 2022", datetime.datetime(2022, 5, 5)),
    ("01.12.2009\t10:20", datetime.datetime(2009, 12, 1, 10, 20)),
    ("5 May 2022\t", datetime.datetime(2022, 5, 5)),
])
def test_tab_inside_the_text(parser, text, expected):
    """pyparsing reads the text with tabs expanded; ``match()`` measured the
    match end in that text but indexed the original with it, and raised
    IndexError for "5\\tMay 2022"."""
    assert parser.parse(text) == expected


@pytest.mark.parametrize("text", [
    "05.05.22", "5/5/22", "May 22", "5 05 22", "a,22", "x\t22", "x\n22",
    "x\xa022", "x　22", "1 , 22", "12345", "a1234b", "٣٣٣٣", "22", ",22x",
    "-22-", ".221", "Mar 2022", "2022", "", "© 2025 Example. Updated 01.09.25.",
])
def test_year_format_regexes_match_scan_string(text):
    """``_detect_year_format`` searches with regexes; it finds what
    ``scan_string`` with ``_YEAR_4DIGIT_PATTERN`` / ``_YEAR_2DIGIT_PATTERN``
    found (pyparsing skips whitespace before a position, so a space or a
    newline never serves as the 2-digit separator)."""
    assert (qdparser._YEAR_4DIGIT_RE.search(text) is not None) == (
        next(qdparser._YEAR_4DIGIT_PATTERN.scan_string(text), None) is not None)
    assert (qdparser._YEAR_2DIGIT_RE.search(text) is not None) == (
        next(qdparser._YEAR_2DIGIT_PATTERN.scan_string(text), None) is not None)
