# -*- coding: utf-8 -*-
"""Exact-equivalence parity between the legacy 6-level filter and the
fingerprint-based filter.

The two filters are invoked on the same string. The candidate set
returned by each MUST be identical — no additions, no removals.

A divergence (asymmetric set difference) means the consumer wiring
round (``wire-fingerprint-filter``) didn't precisely capture one of the
merge rules in the legacy pipeline. Each divergence must be
investigated and fixed in the fingerprint path; flipping the default
(``flip-fingerprint-default``) is gated on this test staying green on
the full probe corpus.
"""

from __future__ import annotations

import pytest

from qddate import DateParser

# Wide probe corpus covering every shipped language, every separator,
# every year-format bucket, weekday + short-month variants, compact
# digit formats, edge cases, and the regression probes from
# ``tests/test_regressions_2026_09.py``.
_PROBE_STRINGS = [
    # Numeric — slash / dot / dash / space
    "01.12.2009", "2013-01-12", "31.05.2001", "7/12/2009", "11/29/1991",
    "05/16/99", "2009/12/07", "05.12.99", "05.12.99.", "5/12/99",
    "05-12-99", "20131201", "15122009", "2020.12.25", "1.2.2020",
    "2013-1-2", "2013-01-12",
    # English — month names (full / abbrev / short) + weekday
    "6 Jan 2009", "Jan 8, 1098", "JAN 1, 2001", "5 August 2001",
    "3 jun 2009", "Thursday 4 April 2019", "Saturday 6 May 2023",
    "July 01, 2015", "Fri, 3 July 2015", "Fri 24 Jul 2015",
    "August 10th, 2015", "Jan 15, 2020", "14th April 2015:",
    "08 Jul, 2015", "8 Sep, 2023", "8th Jul 2015", "Mon, 5 Jan 2020",
    "5 january 2020", "january 5 2020", "5. january. 2020",
    "5.January.2020", "25 Jul 2020", "Mon 5 Jan 2020",
    "Monday 5 january 2020", "Wednesday 22 Apr 2015",
    "Thursday, Jun 25, 2026", "Monday, Jun 22, 2026 - 13:46",
    "Tuesday, Mar 10, 2026 - 10:56",
    # Russian
    "3 Января 2003 года", "05 Января 2003", "15 февраля 2007 года",
    "2 Июня 2015", "9 июля 2015 г.", "23 июня 2015", "3 Июля, 2015",
    "21 Фeвpyapи 2015", "1 нoeмвpи 2013",
    "пятница, июля 17, 2015", "Июль 16, 2015", "9 Июля 2015 [11:23]",
    "09.01.2015",
    # French (accented)
    "Le 8 juillet 2015", "8 juillet 2015", "5 Janvier 2009",
    "5 Janv 2009", "5 janv 2020", "Janv 5, 2020",
    "janv 5, 2020", "Le 5 Janvier 2009", "Lundi 5 Janvier 2009",
    "lundi 5 janvier 2009",
    # Portuguese
    "26 de julho de 2015", "5 Janeiro 2009", "5 janeiro 2009",
    "5 de Janeiro de 2020", "5 Fev 2020", "5 fev 2020",
    "Jan 5, 2020", "jan 5, 2020", "Segunda-feira 5 Janeiro 2020",
    "segunda-feira 5 janeiro 2020", "Seg 5 Janeiro 2020",
    "seg 5 janeiro 2020",
    # Spanish
    "17 de Junio de 2015", "03 de Julio, 2026", "30 de junio, 2026",
    "4 julio, 2026", "junio 9, 2015", "5 Enero 2009", "5 Ene 2009",
    "5 ene 2020", "Ene 5, 2020", "ene 5, 2020", "5/12/2020",
    "Lunes 5 Enero 2009", "lunes 5 enero 2009",
    # Italian
    "lunedì 5 gennaio 2020", "5 Gennaio 2009", "5 gennaio 2009",
    "5 de Gennaio de 2020", "5 de gennaio de 2020",
    "5 Gen 2009", "5 gen 2020", "Gen 5, 2020", "gen 5, 2020",
    "Lunedì 5 Gennaio 2009",
    # Dutch
    "15 Januari 2024", "3 maart 2023", "Maandag, 28 Juli 2015",
    "5 Mrt 2020", "5 mrt 2020", "5/12/2020", "5.1.2020",
    "maandag 5 januari 2009",
    # Turkish
    "17 Ocak 2015", "9 eylül 2022 tarihinde",
    # German (incl. accented → Latin substitution path)
    "28. Juli 2015", "15. Juli 2015", "12. Dez 2022", "12. dez 2022",
    "5 Januar 2009", "5 januar 2009", "5/1/2020", "5.1.2020",
    "Montag 5 Januar 2009", "montag 5 januar 2009", "15. Jul 2023",
    "5. jan 2020",
    # Polish (genitive forms; Polish requires accented chars)
    "5 stycznia 2020", "17 Marca 2018 r.", "5 Styczeń 2009",
    "5 styczeń 2009",
    # Czech
    "15 Leden 2015", "5 ledna 2020", "23 Prosince 2023", "12 července 2022",
    "5 leden 2020",
    # Romanian
    "5 Ianuarie 2009", "5 ianuarie 2009", "5 Ian. 2009", "5 ian. 2009",
    # Ukrainian
    "5 Січень 2009", "5 січень 2009", "5 Січня 2009", "5 січня 2009",
    "5 Січ. 2009", "5 січ. 2009",
    # Bulgarian (Latin-script legacy variants)
    "15 Мapт 2024", "3 дeкeмвpи 2023",
    # No-year short + leading text
    "05.12", "09.июля.2015", "12.03.1999 Hello people",
    # Times
    "16 May 2009 14:10", "01.03.2009 14:53", "01.03.2009 14:53:12",
    "22.12.2009 17:56", "23 Jul 2015, 09:00 BST",
    "12-08-2015 - 09:00", "12.03.1999 10:20:30+0300",
    # Compact digit formats + targeted probes
    "25-Dec-20", "25 Dec, 2020", "25th Dec 2020",
    # Edge cases
    " 01.12.2009", "01.12.2009 ", "7 August, 2015",
]


def _candidate_keys(parser: DateParser, text: str, **kwargs) -> set[str]:
    """Return the set of pattern keys yielded by ``match_all()``."""
    matches = parser.match_all(text, **kwargs)
    return {m["pattern"]["key"] for m in matches}


@pytest.fixture
def legacy_parser() -> DateParser:
    """Parser using the legacy 6-level filter.

    ``use_fingerprint=False`` emits a ``DeprecationWarning`` since
    ``v1.0.15``; this fixture catches it explicitly so the parity test
    suite stays green while the legacy path is still reachable.
    """
    with pytest.warns(DeprecationWarning, match="use_fingerprint=False is deprecated"):
        return DateParser(use_fingerprint=False)


@pytest.fixture
def fp_parser() -> DateParser:
    """Parser using the fingerprint-based filter."""
    return DateParser(use_fingerprint=True)


@pytest.mark.parametrize("text", _PROBE_STRINGS)
def test_fingerprint_equals_legacy(legacy_parser, fp_parser, text):
    """For every probe string the fingerprint candidate set === legacy candidate set."""
    legacy_keys = _candidate_keys(legacy_parser, text)
    fp_keys = _candidate_keys(fp_parser, text)
    extras = fp_keys - legacy_keys
    missing = legacy_keys - fp_keys
    if missing or extras:
        pytest.fail(
            f"Candidate-set divergence for {text!r}:\n"
            f"  only in legacy: {sorted(missing)[:5]}\n"
            f"  only in fingerprint: {sorted(extras)[:5]}"
        )


def test_default_use_fingerprint_is_true(fp_parser):
    """The default flag is ``True`` so the fingerprint path runs by default."""
    assert fp_parser.use_fingerprint is True


def test_legacy_path_still_works_when_explicitly_disabled(legacy_parser):
    """Setting use_fingerprint=False still produces a non-empty candidate set for canonical input."""
    text = "01.12.2009"
    matches = legacy_parser.match_all(text)
    assert matches, "Legacy filter dropped a canonical probe string"


def test_filter_toggles_preserve_equality(legacy_parser, fp_parser):
    """Toggling ``noprefix`` and ``allow_no_year`` must preserve exact equality."""
    text = "12.03.1999 Hello people"
    legacy_keys = _candidate_keys(legacy_parser, text, noprefix=True)
    fp_keys = _candidate_keys(fp_parser, text, noprefix=True)
    assert legacy_keys == fp_keys, (
        f"Divergence with noprefix=True: legacy={sorted(legacy_keys - fp_keys)[:3]} "
        f"fp={sorted(fp_keys - legacy_keys)[:3]}"
    )

    text = "05.12"
    legacy_keys = _candidate_keys(legacy_parser, text, allow_no_year=False)
    fp_keys = _candidate_keys(fp_parser, text, allow_no_year=False)
    assert legacy_keys == fp_keys, (
        f"Divergence with allow_no_year=False: legacy={sorted(legacy_keys - fp_keys)[:3]} "
        f"fp={sorted(fp_keys - legacy_keys)[:3]}"
    )
