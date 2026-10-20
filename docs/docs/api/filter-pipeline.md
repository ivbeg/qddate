---
title: "Filter pipeline"
description: "How DateParser narrows 1,000+ generated patterns to the active value for a given input string."
---

# Filter pipeline

Every parse first narrows the pattern catalog to a short list of candidates,
then runs pyparsing only on those. The narrowing is described as six filter
levels, from cheapest to most selective, so the bulk of the catalog is dropped
before the slow pyparsing `scan_string` step ever runs.

| # | Filter | Default state | Disable flag | What it does |
|---|---|---|---|---|
| 1 | Length | on | (none) | keeps patterns whose length range covers `len(text)` |
| 2 | Character set | on (text len > 5) | `nocharsetfilter=True` (also skipped by `noprefix=True`) | drops patterns whose required script is absent from the input |
| 3 | Separator | on | `noseparatorfilter=True` | drops patterns that only accept different separators |
| 4 | Language | on (text len > 5) | `nolanguagefilter=True` | narrows to the detected language (with allow-list override) |
| 5 | Year format | on | `noyearformatfilter=True` | 4-digit / 2-digit / no-year partition |
| 6 | Prefix | on (text len > 5) | `noprefix=True` | `matchPrefix(text[:6])`: basekey union of plausible candidates |

## Two implementations

Since `1.0.14` the default (`use_fingerprint=True`) is the **fingerprint
filter**: every pattern has a precomputed fingerprint (length range, character
sets, separator, language, year format), and levels 1–5 run as one walk over
that index. Level 6, the prefix filter, runs afterwards on the result.

The **legacy filter** (`DateParser(use_fingerprint=False)`) runs the six levels
one after another over separate indexes. It is deprecated, emits
`DeprecationWarning`, and will be removed in `2.0`.

Both honour the same flags and sessions. The fingerprint filter may keep a few
more candidates than the legacy one, but `match()`, `match_all()` and
`parse()` return the same results on both paths;
`tests/test_fingerprint_parity.py` checks this under every flag combination.

During a session (`start_session(keys)`), only the session's patterns are
candidates.

## Why filter at all

A default `DateParser` carries about 1,100 generated patterns (about 140 base
patterns, each with time-of-day and trailing-text variants; the README lists
the exact counts) and a single pyparsing scan costs around a millisecond.
Without filtering, every parse would run 1,000+ scans.

The filters reduce the average parse to **1–5 pyparsing scans**, which is what
makes `qddate` fast by design.

## Language detection

The language level uses month and weekday names found in the input. When a
month name is shared by several languages (German/Dutch "Juni", German/French
"Mai", Russian/Bulgarian "Август"), a weekday name picks the language. If the
detected language's patterns find nothing, the parser tries the patterns of
every active language, so detection never turns a parseable date into `None`.
With `languages=`, detection is intersected with the allow-list.

## When to disable a filter

Each filter has a `no…` flag that disables it. Disabling a filter only widens
the candidate set: the parser tries more patterns, so it can match inputs that
would otherwise be discarded, but it takes longer.

| Use case | Recommended flags |
|---|---|
| Normal scraping | (no flags; defaults are tuned for the typical case) |
| Inputs with unusual separators (e.g. `‒`, `—`, `，`) | `noseparatorfilter=True` |
| Inputs in Cyrillic / CJK mixed with Latin | `nocharsetfilter=True` |
| Inputs that are ambiguous about the year | `noyearformatfilter=True` |
| Inputs that mix weekday prefixes with bare numbers | `nolanguagefilter=True` |
| Debugging a slow tool: try `noprefix=True` to confirm the prefix index is doing its job |

A reasonable diagnostic order: `noprefix` first (it's the single most
effective filter; disabling it typically slows the parser by ~10×), then
the others one at a time.

## Filter vs. `match_all()`

`match()` returns the highest-priority match; it stops scanning as soon as
the priority drops below the current best. `match_all()` keeps going and
returns every distinct match. Both methods go through the same filters.

If you need to know **whether** an input has more than one plausible
interpretation (e.g. `01/02/2020` could be D/M/Y or M/D/Y), use
`match_all()`: it's the right tool for ambiguity reporting.

## Implementation

Both filters live in
[`qddate/qdparser.py`](https://github.com/ivbeg/qddate/blob/master/qddate/qdparser.py):
`_filter_patterns_fingerprint` (default) and `_filter_patterns_hierarchical`
(legacy). The fingerprint index is built in
[`qddate/patterns/fingerprint.py`](https://github.com/ivbeg/qddate/blob/master/qddate/patterns/fingerprint.py).

The prefix buckets (level 6) are derived from `_PATTERN_METADATA` at import
time; see [the dirty.py derivation in `fix-dirty-py-bucket-drift`](https://github.com/ivbeg/qddate/blob/master/openspec/changes/archive/2026-10-05-fix-dirty-py-bucket-drift).
