---
title: "Filter pipeline"
description: "How DateParser narrows 1,000+ generated patterns to the active value for a given input string."
---

# Filter pipeline

Every parse first narrows the pattern catalog to a short list of candidates,
then runs pyparsing only on those. The narrowing is described as six filter
levels, from cheapest to most selective, so the bulk of the catalog is dropped
before the slow pyparsing step ever runs. A last check before each grammar
(see [Before the grammar runs](#before-the-grammar-runs)) drops the
candidates the text cannot match.

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
that index. Level 6, the prefix filter, runs afterwards on the result. The
walk depends only on the text's fingerprint (length, character sets,
separators, detected language, year format), so its result is kept per
fingerprint: the text nodes of a page share a few of them.

The **legacy filter** (`DateParser(use_fingerprint=False)`) runs the six levels
one after another over separate indexes. It is deprecated, emits
`DeprecationWarning`, and will be removed in `2.0`.

Both honour the same flags and sessions. The fingerprint filter may keep a few
more candidates than the legacy one, but `match()`, `match_all()` and
`parse()` return the same results on both paths;
`tests/test_fingerprint_parity.py` checks this under every flag combination.

During a session (`start_session(keys)`), only the session's patterns are
candidates. With a per-call `languages=` hint, the first pass walks an index
of the hinted languages' patterns and the language-neutral ones (built once
per set of languages); the second pass, run only when the first finds nothing,
walks the rest.

## Why filter at all

A default `DateParser` carries about 1,650 generated patterns (about 140 base
patterns, each with six time-of-day forms and trailing-text variants; the
README lists the exact counts) and a single pyparsing scan costs around a millisecond.
Without filtering, every parse would run 1,000+ scans.

The filters reduce the average parse to **1–5 pyparsing scans**, which is what
makes `qddate` fast by design.

## Before the grammar runs

The filters look at the text as a whole (its length, scripts, separators).
Text that is not a date but looks like one to them, such as `Comments (12)`
or `Price: 1 200 руб.`, can still keep hundreds of candidates. So each
candidate is checked against two facts read from its grammar once:

- the characters a match can start with (a digit for `01.12.2009`), and
- the month or weekday names and the literal words it requires (`年` for
  `2022年5月5日`): from each required list, one must occur in the text. A
  list every alternative of a grammar requires is required, so the ordinal
  suffix `nd` in `Some random text` does not stand in for a month name.

A candidate that fails either check cannot match and is skipped without
running pyparsing. Such text now usually runs no grammar at all. The checks
change no result; `tests/test_match_prefilter.py` renders every grammar and
compares results with the checks switched off.

The grammar itself is then parsed at position 0 only. Releases up to
`1.0.17` scanned it from every position of the text and discarded a match
that did not start at position 0.

Compared with `1.0.17`, these cut `match()` on text without a date from
5–50 ms to under 1 ms, and on dates by about 4×.

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

`match()` returns the match that consumes the most input (a date with its
time beats the bare date); among matches of the same length the
highest-priority one wins. It tries candidates in priority order and stops
as soon as one covers the whole text. `match_all()` keeps going and returns
every distinct match, ranked the same way. Both methods go through the same
filters.

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
