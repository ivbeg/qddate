"""Coarse performance smoke test.

Gated by ``QDDATE_PERF=1``. Runs a fixed corpus of common parses and asserts the
mean latency stays under a generous threshold. Designed to catch catastrophic
regressions (broken length-index prefilter, accidentally disabled packrat) on
CI runners without slowing down local development.

The threshold is intentionally conservative; CI runner variance dominates
real perf regressions at this granularity. Tune the constant in this module
after a baseline is established on the runner image.
"""

import os
import statistics
import time

import pytest

from qddate import DateParser

_PERF_GATED = bool(os.environ.get("QDDATE_PERF"))

_SAMPLES = [
    "01.12.2009",
    "2013-01-12",
    "7/12/2009",
    "6 Jan 2009",
    "16 May 2009 14:10",
    "01.03.2009 14:53:12",
    "July 01, 2015",
    "28. Juli 2015",
    "3 Января 2003 года",
    "lunedì 5 gennaio 2020",
]

# Text nodes without a date, as a scraper sees them on every page. Before the
# checks in ``_match_candidates`` each cost 5 to 50 ms (hundreds of grammars,
# each tried at every position of the text).
_NOT_DATES = [
    "Some random text node 123",
    "Comments (12)",
    "Page 2 of 10",
    "© 2022 Company",
    "Price: 1 200 руб.",
    "15 комментариев",
    "+7 495 123-45-67",
    "Read more »",
    "Опубликовано 5 мая 2022",
    "Thu, 05 May 2022 10:00:00 GMT",
]

# Conservative threshold. A real regression (>10x slowdown) trips this; healthy
# CI runners stay well under.
_THRESHOLD_MEAN_MS = 50.0

# Under 1 ms locally; 15 ms before the checks.
_NOT_DATES_THRESHOLD_MEAN_MS = 5.0


@pytest.mark.skipif(not _PERF_GATED, reason="perf-gated (set QDDATE_PERF=1)")
def test_parse_latency_under_threshold():
    parser = DateParser()

    # Warm up packrat + parser caches.
    for s in _SAMPLES:
        parser.parse(s)

    # Measure 200 parses per sample (2000 total).
    durations_ms = []
    for _ in range(200):
        for s in _SAMPLES:
            t0 = time.perf_counter()
            parser.parse(s)
            durations_ms.append((time.perf_counter() - t0) * 1000.0)

    mean_ms = statistics.mean(durations_ms)
    p95_ms = sorted(durations_ms)[int(len(durations_ms) * 0.95)]

    assert mean_ms < _THRESHOLD_MEAN_MS, (
        f"Mean parse latency {mean_ms:.2f}ms exceeds threshold "
        f"{_THRESHOLD_MEAN_MS:.2f}ms (p95={p95_ms:.2f}ms over {len(durations_ms)} samples). "
        "This usually means the length-index prefilter or packrat parsing is broken."
    )


@pytest.mark.skipif(not _PERF_GATED, reason="perf-gated (set QDDATE_PERF=1)")
def test_text_without_a_date_is_rejected_fast():
    parser = DateParser()
    for s in _NOT_DATES:
        parser.match(s)

    durations_ms = []
    for _ in range(100):
        for s in _NOT_DATES:
            t0 = time.perf_counter()
            parser.match(s)
            durations_ms.append((time.perf_counter() - t0) * 1000.0)

    mean_ms = statistics.mean(durations_ms)
    assert mean_ms < _NOT_DATES_THRESHOLD_MEAN_MS, (
        f"Mean match latency on text without a date {mean_ms:.2f}ms exceeds "
        f"{_NOT_DATES_THRESHOLD_MEAN_MS:.2f}ms. This usually means "
        "_match_candidates runs grammars the text cannot match "
        "(see tests/test_match_prefilter.py)."
    )
