
# qddate — quick and dirty date parsing for scraped HTML

[![CI](https://github.com/ivbeg/qddate/workflows/CI/badge.svg)](https://github.com/ivbeg/qddate/actions)
[![PyPI Version](https://img.shields.io/pypi/v/qddate.svg?style=flat-square)](https://pypi.python.org/pypi/qddate)
[![Docs](https://readthedocs.org/projects/qddate/badge/?version=latest)](https://qddate.readthedocs.org/en/latest/)
[![Coverage](https://codecov.io/gh/ivbeg/qddate/branch/master/graph/badge.svg)](https://codecov.io/gh/ivbeg/qddate)
[![Gitter](https://badges.gitter.im/qddate/Lobby.svg)](https://gitter.im/qddate/Lobby)

`qddate` is a Python 3 library focused on parsing date strings extracted from messy HTML pages as fast as possible. It was born out of long-term news aggregation work and is intentionally pragmatic: fewer abstractions, lots of hard-coded optimizations, and enough language coverage to process millions of strings at scale. The parser ships as part of the "news reconstruction" toolchain that can build RSS feeds for sites that never offered one.

If you need broader language coverage (but can trade speed for flexibility), check out [dateparser](https://github.com/scrapinghub/dateparser) or [dateutil](https://launchpad.net/dateutil).

## Documentation

Full documentation is automatically published at [Read the Docs](https://qddate.readthedocs.org/en/latest/).

## Features

- 712+ date patterns (expanded from 89 base patterns) and growing on demand
- Multi-language parsing (English, Russian, Spanish, Portuguese, and more)
- Handles left-aligned dates with trailing text: `12.03.1999 some text here`
- Prioritizes speed via pyparsing, hard-coded constants, and dirty tricks

## Limitations

- Limited language coverage compared to larger projects
- Adding new languages requires editing pattern tables manually
- Rare/odd formats may still slip through
- No relative date parsing or calendar support

## Speed Optimization

- All constants are embedded directly; no runtime configuration files
- Only depends on `datetime` and `pyparsing` (plus packaging tooling)
- Avoids regular expressions in favor of pre-generated pyparsing patterns
- Aggressive pattern filtering using min/max length filters and prefix heuristics
- Nothing is loaded from disk at runtime besides the Python modules themselves

## Benchmark & Performance Notes

- **Standard benchmarks**: `benchmarks/bench.py` compares qddate with dateparser on the bundled corpus. Run `python benchmarks/bench.py` to execute.
- **Webpage data benchmarks**: `benchmarks/benchmark_webpage_data.py` tests qddate against other libraries using real-world text snippets extracted from webpages. Use `scripts/generate_webpage_test_data.py` to generate test data from government and international organization websites.
- **Comprehensive performance tests**: `benchmarks/comprehensive_performance_test.py` provides extensive performance testing with detailed metrics, pattern analysis, and regression detection. See [`benchmarks/README_PERFORMANCE_TEST.md`](benchmarks/README_PERFORMANCE_TEST.md) for details.
- [`PERFORMANCE_ANALYSIS.md`](PERFORMANCE_ANALYSIS.md) documents the 2025 profiling work (length-based indexing, prefix caching, packrat parsing, etc.) and how to evaluate future optimizations.
- Benchmark numbers depend on hardware, Python version, and workload. Please share your results in issues if you run the benchmark elsewhere.

## Usage

The simplest way to work with qddate is through `qddate.DateParser` and its `parse` method:

```python
import qddate

parser = qddate.DateParser()
print(parser.parse('2012-12-15'))
print(parser.parse('Fri, 12 Dec 2014 10:55:50'))
print(parser.parse('пятница, июля 17, 2015'))
```

The parser auto-detects languages for each string and returns `datetime.datetime` instances when it finds a match.

## Dependencies

- [pyparsing](https://pypi.python.org/pypi/pyparsing)

## Supported Languages

- Bulgarian
- Czech
- English
- French
- German
- Italian
- Polish
- Portuguese
- Russian
- Spanish
- Turkish

## Thanks

The original parser dates back to 2008 and evolved from regular expressions into pyparsing over time. Thanks to the [ScrapingHub](https://github.com/scrapinghub/dateparser) team for the inspiration to clean up the code, documentation, and build tooling, and for motivating the public release.
