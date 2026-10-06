---
title: "Filter pipeline"
description: "How DateParser narrows 1,000+ generated patterns to the active value for a given input string."
---

# Filter pipeline

Every parse goes through a six-level filter pipeline. Each level is a cheap,
selective index that drops patterns which cannot possibly match the input.
The levels run in order from cheapest/most-selective to most-expensive, so
the bulk of the candidate set is filtered out before the slow pyparsing
`scanString` step ever runs.

| # | Filter | Default state | Disable flag | What it does |
|---|---|---|---|---|
| 1 | Length | on | (none) | `self._patterns_by_length[len(text)]` |
| 2 | Character set | on (text len > 5) | `nocharsetfilter=True` | drops patterns whose required script is absent from the input |
| 3 | Separator | on | `noseparatorfilter=True` | drops patterns that only accept different separators |
| 4 | Year format | on | `noyearformatfilter=True` | 4-digit / 2-digit / no-year partition |
| 5 | Language | on | `nolanguagefilter=True` | narrows to the detected language (with allow-list override) |
| 6 | Prefix | on (text len > 5) | `noprefix=True` | `matchPrefix(text[:6])` — basekey union of plausible candidates |

Each filter corresponds to a precomputed index built in `DateParser.__init__`.
The indexes let each filter run as a constant-time lookup rather than a
linear scan over the full pattern list.

## Why six filters

A `DateParser` carries **1,072 generated patterns** (134 base × ~8
time/trailing-text combinations) and a single `scanString` call against
pyparsing costs ~1 ms each on a modern machine. Without filtering, every
parse would do 1,000+ pyparsing scans and never finish.

The six filters collectively reduce the average parse to **1–5 pyparsing
scans**, which is what makes `qddate` "fast" by design.

## When to disable a filter

Each filter has a `no…` flag that disables it. The trade-off is precision
versus recall: disabling a filter means more patterns are tried, so the
parser can match inputs that would otherwise be discarded — but it also
takes longer.

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
returns every distinct match. Both methods go through the same six filters.

If you need to know **whether** an input has more than one plausible
interpretation (e.g. `01/02/2020` could be D/M/Y or M/D/Y), use
`match_all()` — it's the right tool for ambiguity reporting.

## Implementation

The filter pipeline lives in
[`qddate/qdparser.py::_filter_patterns_hierarchical`](https://github.com/ivbeg/qddate/blob/master/qddate/qdparser.py)
and the indexes in
[`_build_length_index`, `_build_separator_index`, `_build_year_format_index`, `_build_language_index`](https://github.com/ivbeg/qddate/blob/master/qddate/qdparser.py).

The prefix buckets (level 6) are derived from `_PATTERN_METADATA` at import
time — see [the dirty.py derivation in `fix-dirty-py-bucket-drift`](https://github.com/ivbeg/qddate/blob/master/openspec/changes/fix-dirty-py-bucket-drift).