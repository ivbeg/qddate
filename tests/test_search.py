"""``search()`` and ``find_all()``: dates that do not start the text (Q18 of
``dev/docs/IMPROVEMENT_PLAN_2026-10-21.md``).

``match()`` reads a date only at position 0, so ``Posted on May 5, 2022`` and
``Опубликовано: 5 мая 2022`` returned ``None``; newsworker stripped a dateline
with its own regex (``_DATELINE_PREFIX_RE``) before matching.
"""
import datetime
import re
import warnings

import pytest

import qddate.qdparser as qdparser
from qddate import DateMatch, DateParser
from qddate.patterns import DATE_LABELS
from tests.test_fingerprint_parity import _PROBE_STRINGS
from tests.test_pattern_lengths import _render, _variants

REFERENCE = datetime.datetime(2026, 10, 22, 12, 0)


@pytest.fixture(scope="module")
def parser():
    return DateParser()


def _grammars_run(parser, call):
    """Return how many grammars ``call()`` runs."""
    run = []
    anchored = parser._anchored

    def counting(grammar):
        run.append(grammar)
        return anchored(grammar)

    parser._anchored = counting
    try:
        call()
    finally:
        del parser._anchored
    return len(run)


@pytest.mark.parametrize("text, date, expected", [
    ("Posted on May 5, 2022", "May 5, 2022", datetime.datetime(2022, 5, 5)),
    ("Опубликовано: 5 мая 2022", "5 мая 2022", datetime.datetime(2022, 5, 5)),
    ("GENEVA, 29 July 2022", "29 July 2022", datetime.datetime(2022, 7, 29)),
    ("New York – 3 May 2022", "3 May 2022", datetime.datetime(2022, 5, 3)),
    ("Updated 5 May 2022 14:30", "5 May 2022 14:30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("Updated: 05.05.2022", "05.05.2022", datetime.datetime(2022, 5, 5)),
    ("By Jane Doe | Updated: 5 May 2022", "5 May 2022", datetime.datetime(2022, 5, 5)),
    ("Veröffentlicht am 5. Mai 2022", "5. Mai 2022", datetime.datetime(2022, 5, 5)),
    ("Publié le 5 mai 2022 à 14h30", "5 mai 2022 à 14h30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("Mis en ligne le 5 mai 2022", "5 mai 2022", datetime.datetime(2022, 5, 5)),
    ("Publicado el 5 de mayo de 2022", "5 de mayo de 2022", datetime.datetime(2022, 5, 5)),
    ("Posted on Monday, May 5, 2022", "Monday, May 5, 2022", datetime.datetime(2022, 5, 5)),
    ("发布时间：2022年5月5日 14:30", "2022年5月5日 14:30", datetime.datetime(2022, 5, 5, 14, 30)),
    ("입력 2022년 5월 5일", "2022년 5월 5일", datetime.datetime(2022, 5, 5)),
    ("POSTED ON May 5, 2022", "May 5, 2022", datetime.datetime(2022, 5, 5)),
    ("• 5 May 2022", "5 May 2022", datetime.datetime(2022, 5, 5)),
    ("(5 May 2022)", "5 May 2022", datetime.datetime(2022, 5, 5)),
    ("5 May 2022", "5 May 2022", datetime.datetime(2022, 5, 5)),
])
def test_date_after_a_label(parser, text, date, expected):
    for labels in (None, True):
        match = parser.search(text, labels=labels)
        assert isinstance(match, DateMatch)
        assert match.datetime == expected
        start, end = match.span
        assert text[start:end] == date
        assert match.raw == text


@pytest.mark.parametrize("text", [
    "Some text 5 May 2022",
    "The meeting was held on 5 May 2022",
    "Read the 2021 report, published in May",
    "Room 12, 5 May 2022",
    "© 2022 Company",
    "+7 495 123-45-67",
])
def test_labels_reject_other_text(parser, text):
    assert parser.search(text, labels=True) is None


def test_without_labels_any_position(parser):
    match = parser.search("The meeting was held on 5 May 2022 in Geneva")
    assert match.datetime == datetime.datetime(2022, 5, 5)
    assert match.span == (24, 34)


def test_custom_labels(parser):
    text = "Stand der Daten 5. Mai 2022"
    assert parser.search(text, labels=True) is None
    assert parser.search(text, labels=["Stand der Daten"]).datetime == datetime.datetime(2022, 5, 5)
    assert parser.search(text, labels="stand  der   DATEN").datetime == datetime.datetime(2022, 5, 5)
    # Custom labels replace the built-in ones; a dateline is still accepted.
    assert parser.search("Posted on May 5, 2022", labels=["Stand"]) is None
    assert parser.search("GENEVA, 29 July 2022", labels=["Stand"]) is not None


def test_max_offset(parser):
    text = "Posted on May 5, 2022"
    assert parser.search(text, max_offset=10).span == (10, 21)
    assert parser.search(text, max_offset=9) is None
    assert parser.search("5 May 2022", max_offset=0).span == (0, 10)
    with pytest.raises(ValueError):
        parser.search(text, max_offset=-1)
    with pytest.raises(TypeError):
        parser.search(text, max_offset=True)


def test_find_all(parser):
    text = "From 5 May 2022 to 7 May 2022"
    matches = parser.find_all(text)
    assert [m.datetime for m in matches] == [datetime.datetime(2022, 5, 5),
                                            datetime.datetime(2022, 5, 7)]
    assert [text[m.span[0]:m.span[1]] for m in matches] == ["5 May 2022", "7 May 2022"]
    # With labels: "From" and "to" are not labels.
    assert parser.find_all(text, labels=True) == []


def test_find_all_with_labels(parser):
    text = "Posted 5 May 2022, updated 7 May 2022 10:00"
    assert [m.datetime for m in parser.find_all(text, labels=True)] == [
        datetime.datetime(2022, 5, 5), datetime.datetime(2022, 5, 7, 10, 0)]
    # Punctuation alone between two dates.
    assert len(parser.find_all("5 May 2022 – 7 May 2022", labels=True)) == 2
    assert parser.find_all("no date here") == []


def test_find_all_does_not_overlap(parser):
    matches = parser.find_all("12.05.2022 14:30, 13.05.2022")
    assert [(m.datetime, m.span) for m in matches] == [
        (datetime.datetime(2022, 5, 12, 14, 30), (0, 16)),
        (datetime.datetime(2022, 5, 13), (18, 28)),
    ]


def test_a_date_at_the_start_reads_as_match_typed(parser):
    """At position 0 ``search`` finds what ``match_typed`` finds."""
    for text in _PROBE_STRINGS:
        typed = parser.match_typed(text, reference=REFERENCE)
        if typed is None:
            continue
        assert parser.search(text, reference=REFERENCE) == typed, text


def test_inside_numbers_and_words_is_not_a_start(parser):
    # "1.200" is a number, "v2" a word; "123" cannot start a date.
    assert list(qdparser._date_starts("1.200 v2 123 45")) == [0, 13]
    assert list(qdparser._date_starts("Posted on May 5")) == [0, 10, 14]
    # After a CJK character a number starts.
    assert list(qdparser._date_starts("发布于2022年5月5日")) == [0, 3, 8, 10]


def test_every_grammar_starts_with_one_two_four_or_eight_digits(parser):
    """``search`` skips runs of 3, 5–7 or 9+ digits; no grammar starts with
    one (the renderings of ``tests/test_pattern_lengths.py``)."""
    found = set()
    for pattern in parser.patterns:
        if pattern["key"].endswith(":t_right"):
            continue
        texts = {_render(tokens, tight) for tokens in _variants(pattern["pattern"])
                 for tight in (False, True)}
        for text in texts:
            digits = re.match(r"\d+", text)
            if digits is None:
                continue
            try:
                pattern["pattern"].parse_string(text)
            except qdparser.ParseBaseException:
                continue
            found.add(len(digits.group()))
    assert found <= qdparser._DATE_DIGIT_RUNS


def test_tabs(parser):
    text = "Posted\ton 5\tMay 2022"
    match = parser.search(text)
    assert text[match.span[0]:match.span[1]] == "5\tMay 2022"


def test_call_options(parser):
    match = parser.search("Updated Dec 25", labels=True,
                          reference=datetime.datetime(2026, 1, 3), prefer="past")
    assert match.datetime == datetime.datetime(2025, 12, 25)
    assert match.has_year is False
    assert parser.search("Updated Dec 25", labels=True, allow_no_year=False) is None
    assert parser.search("Date: 05/06/2022", date_order="MDY").datetime == datetime.datetime(2022, 5, 6)
    assert parser.search("Datum: 18 Juni 1953", languages="de").pattern_key == "dt:date:de_base"
    with pytest.raises(ValueError):
        parser.search("Updated Dec 25", prefer="later")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert parser.search("Updated Dec 25", noyear=False) is None
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_labels_cover_the_main_languages():
    assert {"en", "ru", "de", "fr", "es", "it", "pt", "nl", "pl", "cz", "uk"} <= set(DATE_LABELS)
    assert "posted on" in DATE_LABELS["en"]
    assert "опубликовано" in DATE_LABELS["ru"]


@pytest.mark.parametrize("text", [
    "Comments (12)",
    "Page 2 of 10",
    "© 2022 Company",
    "Price: 1 200 руб.",
    "+7 495 123-45-67",
    "Some random text node 123",
    "The 5 best restaurants in 2022 according to 12 critics",
    "Tel. +7 495 123-45-67, ext. 12",
])
def test_labels_keep_text_without_a_date_cheap(parser, text):
    """With ``labels=True`` only a position after a label runs a grammar."""
    assert _grammars_run(parser, lambda: parser.search(text, labels=True)) == 0
    assert parser.search(text, labels=True) is None
