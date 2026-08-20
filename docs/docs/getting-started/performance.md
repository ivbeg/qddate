---
title: "Performance"
description: "How qddate stays fast, and how to measure it"
---
# Performance

qddate is built for high-throughput parsing of date-like strings from HTML. The
hot path avoids regular expressions, disk I/O, and heuristic language guessing
beyond a cheap candidate filter.

## Why it is fast

- **Pre-generated grammars.** Base patterns are expanded into time and trailing-text variants once at construction.
- **Length indexing.** Only patterns whose min/max length covers the input are considered.
- **Prefix heuristics.** `matchPrefix()` drops obviously incompatible catalogs in microseconds.
- **Charset, separator, year-format, and language filters** shrink the candidate set before pyparsing runs.
- **Packrat parsing** is enabled on import for pyparsing's parse cache.
- **No runtime files.** Constants live in Python modules; nothing is loaded from disk besides the package itself.

Typical construction of a full parser is well under a second. Prefix matching is
on the order of microseconds per call. Wall-clock parse time depends on hardware,
Python version, and how unique the string is.

## Faster still: restrict languages

Loading only the languages you need is the largest practical speedup:

```python
parser = qddate.DateParser(languages=["en"])
```

Fewer patterns means less indexing work and a smaller candidate set on every
call. Prefer this for known-locale crawls.

## Reuse the parser

Construct `DateParser` once per process (or per worker) and call `parse()` in a
loop. Construction compiles patterns; parsing does not.

## Benchmarks in this repository

| Script | Purpose |
|--------|---------|
| `benchmarks/bench.py` | Compare qddate with dateparser on the bundled corpus (`pip install -e ".[bench]"`) |
| `benchmarks/benchmark_webpage_data.py` | Real webpage snippets vs other libraries |
| `benchmarks/comprehensive_performance_test.py` | Timing, throughput, pattern breakdown, regression vs a baseline |
| `scripts/profile_performance.py` | cProfile-style hot-path inspection |

See `benchmarks/README_PERFORMANCE_TEST.md` for flags and report formats.
Numbers depend on hardware; please share results in issues if you run them
elsewhere.

```bash
pip install -e ".[bench]"
python benchmarks/bench.py
python scripts/generate_webpage_test_data.py   # optional corpus from public sites
python benchmarks/benchmark_webpage_data.py
```

## What not to expect

qddate is not a general NLP date extractor. Scanning arbitrary prose for dates
that are **not** left-aligned, or interpreting "yesterday", is out of scope and
would undo the performance model. See [when to use](/getting-started/when-to-use).
