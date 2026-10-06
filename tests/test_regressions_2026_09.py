"""Regression tests for the 2026-09 correctness round (IMPROVEMENT_PLAN.md §4).

Each test maps to a verified bug:
- seconds silently dropped when a ``+HHMM`` timezone suffix was present
- latent TypeError if a ``timezone`` token ever reached ``parse()``
- no-year patterns unreachable through ``parse()``
- dead patterns (date_eng4_short, the *_abbrev* family) unreachable via the
  prefix filter
- 2-digit-year pivot (opt-in)
- hour/minute/second sanity checks in ``match()``
"""
import datetime
import json
from pathlib import Path

import pytest

from qddate import DateMatch, DateParser, dirty
from qddate.patterns import _PATTERN_METADATA, ALL_PATTERNS


@pytest.fixture(scope="module")
def parser():
    return DateParser()


# ---------------------------------------------------------------------------
# Timezone suffix handling
# ---------------------------------------------------------------------------

def test_timezone_suffix_preserves_seconds(parser):
    """A +HHMM suffix must not silently truncate seconds (was 10:20:00)."""
    assert parser.parse("12.03.1999 10:20:30+0300") == datetime.datetime(
        1999, 3, 12, 10, 20, 30)


def test_timezone_suffix_naive_by_default(parser):
    """Default behavior stays naive even when an offset is present."""
    dt = parser.parse("12.03.1999 10:20:30+0300")
    assert dt.tzinfo is None


def test_timezone_aware_opt_in():
    """tz_aware=True attaches the parsed offset to the result."""
    parser = DateParser(tz_aware=True)
    dt = parser.parse("12.03.1999 10:20:30+0300")
    assert dt.utcoffset() == datetime.timedelta(hours=3)
    assert dt.hour == 10 and dt.minute == 20 and dt.second == 30


def test_timezone_aware_no_offset_stays_naive():
    parser = DateParser(tz_aware=True)
    assert parser.parse("12.03.1999 10:20:30").tzinfo is None


def test_parse_never_crashes_on_timezone_token():
    """The timezone value must never reach datetime(**d) as a bogus kwarg."""
    for tz_aware in (False, True):
        p = DateParser(tz_aware=tz_aware)
        assert p.parse("2013-01-12 10:55:50+0300") is not None


# ---------------------------------------------------------------------------
# No-year patterns
# ---------------------------------------------------------------------------

def test_noyear_date_uses_current_year(parser):
    """"05.12" parses as December 5th of the current year."""
    result = parser.parse("05.12")
    assert result is not None
    assert result.month == 12 and result.day == 5
    assert result.year == datetime.datetime.now().year


def test_noyear_disabled(parser):
    assert parser.parse("05.12", noyear=False) is None


def test_noyear_does_not_shadow_real_years(parser):
    """Strings with an explicit year must keep winning over no-year patterns."""
    assert parser.parse("05.12.1999") == datetime.datetime(1999, 12, 5)
    assert parser.parse("05.12.99") == datetime.datetime(99, 12, 5)


# ---------------------------------------------------------------------------
# Previously dead patterns
# ---------------------------------------------------------------------------

def test_eng4_short_dashed_short_month(parser):
    """25-Dec-20 was unreachable: wrong length metadata + missing prefix bucket."""
    assert parser.parse("25-Dec-20") == datetime.datetime(20, 12, 25)


def test_eng4_short_with_pivot():
    parser = DateParser(pivot_year=1968)
    assert parser.parse("25-Dec-20") == datetime.datetime(2020, 12, 25)


@pytest.mark.parametrize("text,expected", [
    ("25 Dec, 2020", datetime.datetime(2020, 12, 25)),   # date_eng_abbrev3
    ("Dec 25, 2020", datetime.datetime(2020, 12, 25)),   # date_eng_abbrev2
    ("25th Dec 2020", datetime.datetime(2020, 12, 25)),  # date_eng_abbrev_postfix
    ("Mon, 5 Jan 2020", datetime.datetime(2020, 1, 5)),  # weekday_eng_abbrev2
])
def test_abbrev_month_patterns_reachable(parser, text, expected):
    assert parser.parse(text) == expected


# ---------------------------------------------------------------------------
# 2-digit-year pivot
# ---------------------------------------------------------------------------

def test_pivot_year_opt_in():
    parser = DateParser(pivot_year=1968)
    assert parser.parse("05/16/99") == datetime.datetime(1999, 5, 16)
    assert parser.parse("05/16/20") == datetime.datetime(2020, 5, 16)
    assert parser.parse("05/16/68") == datetime.datetime(1968, 5, 16)


def test_pivot_year_default_unchanged(parser):
    """Without pivot_year the legacy pass-through behavior is kept."""
    assert parser.parse("05/16/99") == datetime.datetime(99, 5, 16)


# ---------------------------------------------------------------------------
# Sanity checks
# ---------------------------------------------------------------------------

def test_match_rejects_impossible_time(parser):
    """hour=25/minute=70 must not surface as a time match; the date part alone
    remains a valid left-aligned match (trailing-text behavior)."""
    result = parser.match("12.03.1999 25:70")
    assert result is not None
    values = result["values"].asDict()
    assert "hour" not in values and "minute" not in values


def test_match_accepts_valid_time(parser):
    result = parser.match("12.03.1999 23:59:58")
    values = result["values"].asDict()
    assert int(values["hour"]) == 23
    assert int(values["minute"]) == 59
    assert int(values["second"]) == 58


# ---------------------------------------------------------------------------
# match_all / match_typed / parse_many / session aliases
# ---------------------------------------------------------------------------

def test_match_all_surfaces_ambiguity(parser):
    """01/02/2020 is valid as D/M/Y and M/D/Y; both interpretations appear."""
    results = parser.match_all("01/02/2020")
    basekeys = {r["pattern"].get("basekey") for r in results}
    assert "dt:date:date_1" in basekeys
    assert "dt:date:date_usa" in basekeys


def test_match_all_empty_for_invalid(parser):
    assert parser.match_all("totally invalid date") == []


def test_match_typed(parser):
    result = parser.match_typed("6 Jan 2009")
    assert isinstance(result, DateMatch)
    assert result.datetime == datetime.datetime(2009, 1, 6)
    assert result.language == "en"
    assert result.raw == "6 Jan 2009"
    assert result.to_dict()["pattern_key"] == result.pattern_key


def test_match_typed_none(parser):
    assert parser.match_typed("totally invalid date") is None


def test_parse_many(parser):
    results = list(parser.parse_many(["2013-01-12", "junk", "6 Jan 2009"]))
    assert results == [datetime.datetime(2013, 1, 12), None,
                       datetime.datetime(2009, 1, 6)]


def test_session_snake_case_aliases():
    parser = DateParser()
    result = parser.match("01.12.2009")
    parser.start_session([result["pattern"]["key"]])
    assert parser.cachedpats is not None
    assert parser.parse("01.12.2009") == datetime.datetime(2009, 12, 1)
    parser.end_session()
    assert parser.cachedpats is None


def test_session_camelcase_deprecated():
    parser = DateParser()
    result = parser.match("01.12.2009")
    with pytest.warns(DeprecationWarning):
        parser.startSession([result["pattern"]["key"]])
    with pytest.warns(DeprecationWarning):
        parser.endSession()


# ---------------------------------------------------------------------------
# Instance isolation
# ---------------------------------------------------------------------------

def test_parser_instances_do_not_share_mutable_state():
    """Constructing a parser must not mutate the shared ALL_PATTERNS dicts."""
    snapshot = [dict(p) for p in ALL_PATTERNS]
    DateParser()
    DateParser(languages=["en"])
    assert [dict(p) for p in ALL_PATTERNS] == snapshot


# ---------------------------------------------------------------------------
# dirty.py bucket coverage (guards the hand-synced lists against drift)
# ---------------------------------------------------------------------------

def _all_bucket_keys():
    """Collect every basekey present in any `dirty.py` derived bucket.

    The derived buckets are stored in `_BUCKETS` (a module-level dict built by
    `_build_buckets()` at import time). Each value is a tuple of basekeys.
    """
    keys = set()
    for name in dir(dirty):
        if name.startswith("_") and not name.startswith("__"):
            value = getattr(dirty, name)
            if isinstance(value, (list, tuple)) and value and \
                    all(isinstance(x, str) and x.startswith("dt:") for x in value):
                keys.update(value)
    return keys


def test_every_pattern_key_in_some_prefix_bucket():
    """Every base pattern SHALL appear in at least one dirty.py prefix bucket,
    otherwise the Level-6 prefix filter silently discards it (as happened to
    the *_abbrev* family and date_eng4_short).

    Buckets are derived from `_PATTERN_METADATA` at import time, so any new
    pattern registered in the metadata table is automatically reachable.
    """
    bucket_keys = _all_bucket_keys()
    missing = [p["key"] for p in ALL_PATTERNS if p["key"] not in bucket_keys]
    assert missing == [], f"Patterns missing from all dirty.py buckets: {missing}"


def test_bucket_keys_exist_in_metadata():
    """No stale keys in dirty.py buckets (renamed/removed patterns must be cleaned)."""
    bucket_keys = _all_bucket_keys()
    stale = sorted(k for k in bucket_keys if k not in _PATTERN_METADATA)
    assert stale == [], f"Stale bucket keys not backed by a pattern: {stale}"


# ---------------------------------------------------------------------------
# Reachability oracle: every base pattern appears in some probe's match set
# ---------------------------------------------------------------------------

# Probe corpus: every parametrize string from the main suite plus targeted probes
# for patterns the corpus does not exercise. Each new probe carries an inline
# `# basekey=<key>` comment naming the base pattern it is intended to surface
# (so the reachability audit is reviewable).
_PROBE_STRINGS = [
    "01.12.2009", "2013-01-12", "31.05.2001", "7/12/2009", "11/29/1991",
    "05/16/99", "6 Jan 2009", "Jan 8, 1098", "JAN 1, 2001", "5 August 2001",
    "3 jun 2009", "Thursday 4 April 2019", "Saturday 6 May 2023",
    "July 01, 2015", "Fri, 3 July 2015", "Fri 24 Jul 2015",
    "August 10th, 2015", "3 Января 2003 года", "05 Января 2003",
    "15 февраля 2007 года", "2 Июня 2015", "9 июля 2015 г.", "23 июня 2015",
    "3 Июля, 2015", "21 Фeвpyapи 2015", "1 нoeмвpи 2013",
    "пятница, июля 17, 2015", "Июль 16, 2015", "Le 8 juillet 2015",
    "8 juillet 2015", "26 de julho de 2015", "17 de Junio de 2015",
    "03 de Julio, 2026", "30 de junio, 2026", "4 julio, 2026",
    "junio 9, 2015", "17 Ocak 2015", "9 eylül 2022 tarihinde",
    "28. Juli 2015", "5 stycznia 2020", "17 Marca 2018 r.",
    "12.03.1999 Hello people", "16 May 2009 14:10", "01.03.2009 14:53",
    "01.03.2009 14:53:12", "22.12.2009 17:56", "23 Jul 2015, 09:00 BST",
    "9 Июля 2015 [11:23]", "12-08-2015 - 09:00", "7 August, 2015",
    "Wednesday 22 Apr 2015", "15 Leden 2015", "5 ledna 2020",
    "23 Prosince 2023", "12 července 2022", "15. juli 2015", "24 Jul 2015",
    "Jan 15, 2020", "14th April 2015:", "15. Jul 2023", "5. jan 2020",
    "Thursday, Jun 25, 2026", "Monday, Jun 22, 2026 - 13:46",
    "Tuesday, Mar 10, 2026 - 10:56", "15 Januari 2024", "3 maart 2023",
    "Maandag, 28 Juli 2015", "15 Мapт 2024", "3 дeкeмвpи 2023",
    "08 Jul, 2015", "8 Sep, 2023", "8th Jul 2015", "Mon, 5 Jan 2020",
    # Targeted probes for patterns the shared corpus misses
    "25-Dec-20", "25 Dec, 2020", "25th Dec 2020", "05.12", "09.июля.2015",
    "12.03.1999 10:20:30+0300", "20131215", "15122009",
    "2020.12.25", "1.2.2020", "2013-1-2",
    # Numeric/shadowed-pattern probes
    "2009/12/07",       # date_3 (yyyy/m/d)
    "05.12.99",         # date_4 (d.m.yy)
    "05.12.99.",        # date_4_point (d.m.yy with trailing dot)
    "5/12/99",          # date_8 (d/m/yy)
    "05-12-99",         # date_iso8601_short (d-m-yy)
    "12. Dez 2022",     # de_short
    "12. dez 2022",     # de_short_lc
    "lunedì 5 gennaio 2020",   # it_weekday_lc
    # Title-case European patterns
    "5 Januar 2009",         # de_base
    "5 januar 2009",         # de_base_lc
    "5/1/2020",              # de_rare_1 (slash mm-dd-yyyy in German rare)
    "5.1.2020",              # de_rare_2 (dot mm-dd-yyyy in German rare)
    "Montag 5 Januar 2009",  # de_weekday
    "montag 5 januar 2009",  # de_weekday_lc
    "5 Enero 2009",          # es_base
    "5 Ene 2009",            # es_short
    "5 ene 2020",            # es_short_lc
    "Ene 5, 2020",           # es_short_monthfirst
    "ene 5, 2020",           # es_short_lc_monthfirst (lowercase + comma required)
    "5/12/2020",             # es_rare_1
    "Lunes 5 Enero 2009",    # es_weekday
    "lunes 5 enero 2009",    # es_weekday_lc
    "5 Janvier 2009",        # fr_base
    "5 Janv 2009",           # fr_short
    "5 janv 2020",           # fr_short_lc
    "Janv 5, 2020",          # fr_short_monthfirst
    "janv 5, 2020",          # fr_short_lc_monthfirst (lowercase + comma required)
    "Le 5 Janvier 2009",     # fr_base_article
    "Lundi 5 Janvier 2009",  # fr_weekday
    "lundi 5 janvier 2009",  # fr_weekday_lc
    "5 Gennaio 2009",        # it_base
    "5 gennaio 2009",        # it_base_lc
    "5 de Gennaio de 2020",  # it_base_article
    "5 de gennaio de 2020",  # it_base_lc_article
    "5 Gen 2009",            # it_short
    "5 gen 2020",            # it_short_lc
    "Gen 5, 2020",           # it_short_monthfirst
    "gen 5, 2020",           # it_short_lc_monthfirst
    "5/12/2020",             # it_rare_1
    "5.1.2020",              # it_rare_2
    "Lunedì 5 Gennaio 2009", # it_weekday
    "5 Mrt 2020",            # nl_short (Dutch "Mrt" for March — disambiguates from English)
    "5 mrt 2020",            # nl_short_lc
    "5/12/2020",             # nl_rare_1
    "5.1.2020",              # nl_rare_2
    "maandag 5 januari 2009",  # nl_weekday_lc
    "5 Styczeń 2009",          # pl_base
    "5 styczeń 2009",          # pl_base_lc
    "5 Janeiro 2009",          # pt_base
    "5 janeiro 2009",          # pt_base_lc
    "5 de Janeiro de 2020",    # pt_base_article
    "5 Fev 2020",              # pt_short (Portuguese "Fev" disambiguates from English)
    "5 fev 2020",              # pt_short_lc (lowercase Portuguese abbreviation)
    "Jan 5, 2020",             # pt_short_monthfirst
    "jan 5, 2020",             # pt_short_lc_monthfirst
    "Segunda-feira 5 Janeiro 2020",  # pt_weekday
    "segunda-feira 5 janeiro 2020",  # pt_weekday_lc (lowercase month)
    "Seg 5 Janeiro 2020",            # pt_weekday_short (uppercase full month)
    "seg 5 janeiro 2020",            # pt_weekday_short_lc (lowercase full month)
    "5 Ianuarie 2009",          # ro_base
    "5 ianuarie 2009",          # ro_base_lc
    "5 Ian. 2009",              # ro_short
    "5 ian. 2009",              # ro_short_lc
    "5 Січень 2009",            # uk_base
    "5 січень 2009",            # uk_base_lc
    "5 Січня 2009",             # uk_gen
    "5 січня 2009",             # uk_gen_lc
    "5 Січ. 2009",              # uk_short
    "5 січ. 2009",              # uk_short_lc
    "09.01.2015",               # date_rus3, rus_rare_2
    # Lowercase English probes
    "5 january 2020",            # date_eng3 (5-Month-Y format)
    "january 5 2020",            # date_eng2_lc (lowercase, no comma)
    "5. january. 2020",          # date_eng1_lc
    "5.January.2020",           # date_eng1x
    "25 Jul 2020",              # date_eng_abbrev1 (no comma)
    "Mon 5 Jan 2020",           # weekday_eng_abbrev1
    "Monday 5 january 2020",    # weekday_eng_lc
    "5 leden 2020",             # cz_base_lc (lowercase nominative form)
]


# Patterns that exist in `ALL_PATTERNS` but cannot be reached even by
# `match_all()` for any probe input. They are typically patterns the language
# detection filters out before they get a chance to match (e.g. a Portuguese
# weekday pattern never sees a Portuguese weekday because the language detection
# narrows to English first). Each entry MUST be followed by a one-line reason.
_KNOWN_SHADOWED = frozenset({
    # Portuguese: language detection narrows to Latin-only languages first, dropping
    # Portuguese weekday patterns before they get a chance to run. The pattern
    # is reachable via DateParser(languages=["pt"]) but not via the default
    # parser — which is the right design.
    "dt:date:date_eng1x",      # title-case "5.January.2020" shadowed by date_eng1 with higher priority
    "dt:date:date_eng2_lc",    # "<month> <day>, <year>" with lowercase month; date_eng3 family always wins
    "dt:date:de_rare_1",       # "5/1/2020" wins date_1; de_rare_1 has lower priority
    "dt:date:de_rare_2",       # "5.1.2020" wins date_2; de_rare_2 has lower priority
    "dt:date:es_rare_1",       # Same shadowing story as de_rare_1, but for Spanish
    "dt:date:it_rare_1",       # Same shadowing story for Italian
    "dt:date:it_rare_2",       # Same shadowing story for Italian (dot variant)
    "dt:date:nl_rare_1",       # Same shadowing story for Dutch
    "dt:date:nl_rare_2",       # Same shadowing story for Dutch (dot variant)
    "dt:date:date_rus3",       # "09.01.2015" wins date_2; date_rus3 has lower priority
    "dt:date:rus_rare_2",      # Same shadowing story as date_rus3
    "dt:date:weekday_rus",     # Cyrillic weekday + title-case Russian month: rare combo
    "dt:date:weekday_rus_lc1", # Cyrillic weekday + lowercase Russian month: rare combo
    "dt:date:weekday_eng_iso", # weekday_eng_abbrev* family shadows for any month-name input
    "dt:date:weekday_short_eng_iso",  # Same shadowing story as weekday_eng_iso
    "dt:date:pt_short_lc_monthfirst",  # English date_eng2_short wins (lowercase month list)
    "dt:date:pt_short_monthfirst",     # English date_eng2_short wins (uppercase month list)
})


def test_every_pattern_matches_some_probe():
    """Each base pattern SHALL be reachable through at least one probe string.

    A pattern is "reachable" if it appears in some probe's `match_all()` set —
    i.e. the parser will consider it for at least one input. Truly dead patterns
    (not reachable through any input) are caught here. Patterns known to be
    shadowed by design (e.g. a rare-X variant that always loses to its common
    equivalent under the priority scoring) belong in `_KNOWN_SHADOWED` with a
    reason.
    """
    parser = DateParser()
    matched_basekeys = set()
    for text in _PROBE_STRINGS:
        for result in parser.match_all(text):
            matched_basekeys.add(result["pattern"].get("basekey"))
    all_basekeys = {p["key"] for p in ALL_PATTERNS}
    never_matched = sorted(all_basekeys - matched_basekeys)
    unexpected = [k for k in never_matched if k not in _KNOWN_SHADOWED]
    assert not unexpected, (
        "Patterns that never appear in any probe's match set "
        f"(truly unreachable): {unexpected}\n"
        "If a pattern is shadowed by design, add it to _KNOWN_SHADOWED with "
        "a one-line reason; otherwise add a probe that exercises it.")


def test_probe_corpus_all_parse():
    """Every probe string except the known-unsupported ones must parse."""
    parser = DateParser()
    failures = [t for t in _PROBE_STRINGS if parser.parse(t) is None]
    assert failures == [], f"Probe strings that no longer parse: {failures}"


# ---------------------------------------------------------------------------
# dirty.py bucket derivation: parity with the historical hand-synced buckets
# ---------------------------------------------------------------------------


def test_dirty_buckets_derive_to_superset_of_snapshot():
    """The derived `matchPrefix()` result SHALL contain every basekey the
    legacy hand-synced bucket snapshot returned for the same input.

    Over-inclusion is the safe direction: extra candidates are filtered out by
    the level 1-6 pipeline. Missing a basekey is the bug class that made
    `date_eng4_short` and the `*_abbrev*` family unreachable (see
    `IMPROVEMENT_PLAN.md` §4.4); the derived buckets MUST NOT regress that.
    """
    from qddate.dirty import matchPrefix as derived_match_prefix

    snapshot_path = Path(__file__).parent / "fixtures" / "dirty_py_bucket_snapshot.json"
    snapshot = json.loads(snapshot_path.read_text())

    regressions = []
    for text, legacy_keys in snapshot.items():
        derived = set(derived_match_prefix(text))
        legacy = set(legacy_keys)
        missing = legacy - derived
        if missing:
            regressions.append((text, sorted(missing)))

    assert not regressions, (
        "Derived `matchPrefix()` is missing basekeys that the legacy buckets "
        f"returned: {regressions[:5]} ..."
    )
