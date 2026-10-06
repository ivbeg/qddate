# Specification: Packaging and Public API

The distribution, dependency, and public API surface of the `qddate` package.

## Purpose

Pin the supported Python versions, the runtime dependency footprint, and the names of
the public symbols so that releases remain installable and downstream code does not
break.

---
## Requirements
### Requirement: Supported Python versions

The package SHALL support Python 3.10, 3.11, 3.12, 3.13, and 3.14 on CPython
and PyPy. End-of-life Python versions SHALL NOT be advertised as supported
nor tested in CI.

#### Scenario: Install on a supported interpreter
- **GIVEN** a Python 3.10–3.14 interpreter
- **WHEN** the package is installed
- **THEN** `import qddate` SHALL succeed

#### Scenario: EOL Python versions not advertised
- **WHEN** the `pyproject.toml` classifiers and `tox.ini` envlist are
  inspected
- **THEN** no Python version older than 3.10 SHALL appear

### Requirement: Minimal runtime dependencies

The runtime dependency set SHALL be limited to `pyparsing`. Heavy general-purpose
date libraries (e.g. `dateparser`, `python-dateutil`, `arrow`, `pendulum`) SHALL be
optional, available only through extras, and SHALL NOT be imported by the library at
runtime.

> Note: the current `pyproject.toml` lists `dateparser>=1.2.0` as a hard runtime
> dependency despite no runtime import. That is tracked as a proposed change in
> `changes/cleanup-project-hygiene/`.

#### Scenario: Import without optional deps installed
- **GIVEN** an environment with only `pyparsing` installed
- **WHEN** `import qddate` and `qddate.DateParser()` are executed
- **THEN** no `ImportError` or `ModuleNotFoundError` SHALL be raised

---

### Requirement: Public API surface

The package SHALL expose, at top level, at minimum: the `DateParser` class, the
`__version__` string, and the module `qddate.patterns`.

#### Scenario: Top-level imports
- **WHEN** `from qddate import DateParser` and `import qddate; qddate.__version__`
- **THEN** both SHALL succeed without error

---

### Requirement: Constructor configuration parameters

`DateParser.__init__` SHALL accept the parameters `generate`, `patterns`,
`base_only`, and `languages`, preserving their documented meaning across releases.

#### Scenario: Default construction
- **WHEN** `DateParser()` is constructed with no arguments
- **THEN** all supported patterns SHALL be generated and indexed

#### Scenario: Custom pattern list
- **GIVEN** a caller-supplied list of pattern dicts
- **WHEN** `DateParser(patterns=custom)` is constructed
- **THEN** the parser SHALL use exactly those patterns

---

### Requirement: Deterministic module import

Importing the library SHALL NOT perform network or filesystem I/O beyond reading the
package's own Python modules, and SHALL NOT mutate global process state other than
enabling pyparsing's packrat parsing cache.

#### Scenario: Import side effects
- **WHEN** `import qddate` is executed
- **THEN** no files SHALL be read from disk and no network calls SHALL occur

### Requirement: Single source of truth for month names

Month-name lists and `month_to_int` mappings SHALL be defined once in
`qddate/patterns/months.py` and consumed by the per-language pattern
modules and the language-detection logic in `qddate/qdparser.py`.

#### Scenario: Adding a new language touches one file
- **WHEN** a new language is added to `qddate`
- **THEN** the contributor SHALL add a single entry to `MONTHS_BY_LANGUAGE`
  in `qddate/patterns/months.py` and (optionally) a small pattern module
- **AND** language detection SHALL pick it up automatically

#### Scenario: Per-language names are unchanged externally
- **WHEN** tests import `EN_MONTHS`, `de_mname2mon`, etc.
- **THEN** the names SHALL be present and equal to the canonical table
  values (verified by `test_each_language_month_to_int_matches_legacy`)
- **AND** no test code SHALL need to change

### Requirement: Detection logic uses the same table

The language-detection logic in `qddate/qdparser.py` SHALL resolve month
names from `MONTHS_BY_LANGUAGE` rather than from a hand-maintained
duplicate list.

#### Scenario: Detection table is data-only
- **WHEN** the detection logic searches the input for a known language
- **THEN** the lookup SHALL go through `MONTHS_BY_LANGUAGE[code]`
- **AND** no per-language `_MONTH_LANGUAGES` constant SHALL exist outside
  `qddate/patterns/months.py`

### Requirement: README pattern counts are auto-generated

The pattern counts in `README.md` SHALL be a function of
`qddate.patterns.ALL_PATTERNS` (and the package's supported-language list),
not a hand-written string. A delimited markdown fragment SHALL be inserted
into the README so the script can replace it idempotently.

#### Scenario: Generated counts match the canonical table
- **WHEN** `python scripts/generate_readme_stats.py` is run against the
  current codebase
- **THEN** the emitted fragment SHALL report the same count as
  `len(qddate.patterns.ALL_PATTERNS)` (or the equivalent generated-pattern
  count from a fresh `DateParser().patterns`)
- **AND** the language count SHALL equal `len(qddate.patterns.SUPPORTED_LANGUAGES)`

#### Scenario: Script is idempotent
- **WHEN** the script runs twice on the same `README.md`
- **THEN** the second run SHALL NOT produce a diff (or only a no-op diff
  where the script replaces the block with itself)

#### Scenario: Adding a new pattern updates the README
- **GIVEN** a new base pattern is added to `qddate.patterns`
- **WHEN** `python scripts/generate_readme_stats.py` is run
- **THEN** the emitted count SHALL increase by 1
- **AND** the README SHALL be updated to reflect the new count

### Requirement: Package advertises inline type hints via PEP 561

The shipped wheel and installed package directory SHALL contain a
`py.typed` marker file at the package root so downstream mypy/pyright
configuration can pick up the inline type hints without manual configuration.

#### Scenario: Wheel contains the marker
- **WHEN** `python -m build --wheel` is run and the produced wheel is
  inspected
- **THEN** the wheel SHALL contain a `qddate/py.typed` file

#### Scenario: Installed package exposes the marker
- **WHEN** `pip install qddate-*.whl` is run and `python -c
  "import qddate; open(os.path.join(os.path.dirname(qddate.__file__),
  'py.typed'))"` is executed
- **THEN** the file SHALL open without `FileNotFoundError`

#### Scenario: Downstream mypy picks up hints automatically
- **WHEN** a downstream project imports `qddate` and runs `mypy` against its
  own code
- **THEN** the `qddate` package SHALL be type-checked using the inline hints
  (no `# type: ignore` on the import line)

### Requirement: Public API is type-hinted

The public methods of `DateParser` and `DateMatch` SHALL carry parameter and
return type hints. Internal helpers MAY be untyped.

#### Scenario: Static type-checking finds the public surface
- **WHEN** a downstream consumer runs `mypy` (or equivalent) against code
  that imports `qddate`
- **THEN** calls to `DateParser.parse()`, `.match()`, `.match_all()`,
  `.match_typed()`, `.parse_many()`, `.format_date()`, and attribute access
  on the returned `DateMatch` SHALL be type-checked without `# type: ignore`

#### Scenario: DateMatch fields carry hints
- **WHEN** `DateMatch` is introspected (e.g. by `dataclasses.fields()` or an
  IDE)
- **THEN** every declared field SHALL declare a type
- **AND** the hints SHALL be consistent with the runtime types documented in
  the `DateMatch` docstring

### Requirement: Round-trip format helper

The library SHALL expose a `format_date()` function and equivalent instance
methods that round-trip a parsed `datetime` back into a string the parser
will accept again, using the format string attached to the matched pattern.

#### Scenario: Round-trip a parsed English date
- **GIVEN** `parser.parse("6 Jan 2009")` returns a `DateMatch` for
  `pattern_key="dt:date:date_eng1_short"` with `datetime(2009, 1, 6)`
- **WHEN** `match.format_date()` is called
- **THEN** the returned string SHALL be `"6 Jan 2009"`
- **AND** the returned string SHALL be parseable back to the same datetime

#### Scenario: Locale round-trip via Russian pattern
- **GIVEN** `parser.parse("05 Января 2003")` returns a `DateMatch`
- **WHEN** `format_date(match.datetime, pattern_key="dt:date:date_rus1_short")` is called
- **THEN** the returned string SHALL contain the Russian month word
- **AND** the returned string SHALL be parseable back to the same datetime

#### Scenario: Unknown pattern key raises
- **WHEN** `format_date(dt, pattern_key="not:a:real:key")` is called
- **THEN** `ValueError` SHALL be raised with a message naming the unknown key

#### Scenario: format_date exposed on DateParser
- **GIVEN** a `DateParser` instance `parser` and a `datetime` `dt`
- **WHEN** `parser.format_date(dt, pattern_key=...)` is called
- **THEN** the result SHALL match the standalone `format_date(dt, pattern_key=...)`

### Requirement: DateMatch exposes format_date

`DateMatch` SHALL expose `format_date()` as an instance method that uses the
match's own `format` string and `datetime` to produce the round-trip output.

#### Scenario: DateMatch.format_date() works without explicit pattern key
- **GIVEN** a `DateMatch` produced by any `DateParser.match()` or
  `DateParser.parse()` call
- **WHEN** `match.format_date()` is called
- **THEN** the returned string SHALL be the result of
  `match.datetime.strftime(match.format)`
- **AND** no `ValueError` SHALL be raised for any successful match

### Requirement: Pattern tables use pyparsing 3 snake_case API

All pattern definitions SHALL use the pyparsing 3 snake_case API
(`set_results_name`, `one_of`, `set_parse_action`) rather than the deprecated
camelCase aliases.

#### Scenario: Library emits no pyparsing DeprecationWarnings at import
- **WHEN** `import qddate` is run with `-W error::DeprecationWarning`
- **THEN** no pyparsing deprecation warning SHALL be raised
- **AND** the module SHALL still expose the same `ALL_PATTERNS` table

#### Scenario: Pattern tables parse identically after migration
- **GIVEN** any historical parse probe from the regression test suite
- **WHEN** the probe is parsed by `qddate.DateParser()`
- **THEN** the result SHALL match the historical golden value

### Requirement: Public parsing methods accept `allow_no_year=`

`DateParser.parse`, `DateParser.match`, and `DateParser.match_all` SHALL
accept an `allow_no_year: bool = True` keyword parameter that controls whether
patterns carrying the ``noyear`` flag are eligible to match.

The legacy keyword ``noyear=`` SHALL continue to work as a deprecated alias
that emits `DeprecationWarning` recommending `allow_no_year=`.

#### Scenario: Default behaviour unchanged
- **WHEN** a caller invokes `parser.parse(text)` without any keyword
- **THEN** no-year patterns SHALL be eligible (the historical default)
- **AND** the caller SHALL NOT see a `DeprecationWarning`

#### Scenario: Explicit allow_no_year=False disables no-year patterns
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", allow_no_year=False)` is called
- **THEN** the result SHALL be `None` (no-year patterns are excluded)
- **AND** the caller SHALL NOT see a `DeprecationWarning`

#### Scenario: Legacy noyear= alias still works
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", noyear=True)` is called
- **THEN** the result SHALL equal the `allow_no_year=True` result
- **AND** a `DeprecationWarning` SHALL be emitted

#### Scenario: Legacy noyear=False still works
- **GIVEN** `parser = DateParser()`
- **WHEN** `parser.parse("05.12", noyear=False)` is called
- **THEN** the result SHALL be `None`
- **AND** a `DeprecationWarning` SHALL be emitted

### Requirement: ALL_PATTERNS is not mutated after import

The module-level `qddate.patterns.ALL_PATTERNS` list SHALL be a stable,
read-only structure after import. Constructing any number of `DateParser`
instances SHALL NOT modify it.

#### Scenario: Repeated DateParser construction is idempotent
- **GIVEN** a snapshot of `qddate.patterns.ALL_PATTERNS` taken right after
  import
- **WHEN** five `DateParser()` instances are constructed sequentially
- **THEN** the snapshot SHALL match `ALL_PATTERNS` byte-for-byte afterward

#### Scenario: __generate is read-only against ALL_PATTERNS
- **GIVEN** `qddate.patterns.ALL_PATTERNS` before any `DateParser` is created
- **WHEN** `DateParser._DateParser__generate(ALL_PATTERNS)` is called twice
- **THEN** the second call SHALL produce the same list of generated patterns
  as the first
- **AND** `ALL_PATTERNS[i]` SHALL be byte-identical after each call

### Requirement: Pattern metadata drives prefix buckets

The `matchPrefix()` function SHALL derive its prefix-bucket groupings from the
single-source-of-truth `_PATTERN_METADATA` table, not from hand-synced lists.

#### Scenario: Adding a new pattern updates the buckets automatically
- **GIVEN** a new pattern dict is appended to `qddate.patterns.ALL_PATTERNS`
  with a registered `_PATTERN_METADATA` entry
- **WHEN** `matchPrefix(text[:6])` is called for any input
- **THEN** the new pattern SHALL be eligible for inputs whose prefix matches
  its `(language, separator)` grouping
- **AND** the contributor SHALL NOT need to edit `qddate/dirty.py` to enable
  this

#### Scenario: Removing a pattern clears the buckets automatically
- **GIVEN** a pattern is removed from `qddate.patterns.ALL_PATTERNS`
- **WHEN** `matchPrefix(text[:6])` is called
- **THEN** the removed pattern SHALL NOT appear in any bucket

### Requirement: Prefix bucket parity is regression-tested

The test suite SHALL include a parity test that asserts the derived buckets
produce the same candidate set as the legacy hand-synced lists (during the
migration window) and that any subsequent regression in the derivation logic
is caught at CI time.

#### Scenario: Parity test exists
- **WHEN** `pytest tests/test_regressions_2026_09.py` runs
- **THEN** the parity test SHALL execute against the full probe corpus
- **AND** any disagreement SHALL fail the suite with a clear diff

### Requirement: Repository ships no regenerable benchmark outputs

The repository SHALL NOT track files under `benchmarks/results/` or other
clearly-regenerable output directories; only sources, tests, fixtures,
documentation, and non-regenerable baselines SHALL be tracked.

#### Scenario: benchmarks/results is not in git
- **WHEN** a fresh clone is inspected
- **THEN** `git ls-files benchmarks/results/` SHALL return zero files
- **AND** `benchmarks/results/` SHALL appear in `.gitignore`
- **AND** the directory SHALL exist locally as the script's normal write target

#### Scenario: scratch files are not at the repo root
- **WHEN** the repo root is listed
- **THEN** no `tests.py`, `reproduce_issues.py`, or
  `*.code-workspace` file SHALL be present
- **AND** legitimate scratch scripts SHALL live under `scripts/`

### Requirement: Single canonical source for dependencies

Dependencies SHALL be declared in `pyproject.toml` (PEP 621). `requirements.txt`
SHALL either be absent or be a thin alias of the canonical file.

#### Scenario: pip install with the canonical file
- **GIVEN** a clean virtual environment
- **WHEN** the contributor follows `CONTRIBUTING.md` and runs the documented
  install command
- **THEN** the runtime dependency set SHALL include only `pyparsing`
- **AND** `dateparser`, `python-dateutil`, `arrow`, and `pendulum` SHALL only
  be installed when the contributor opts into the `bench` extra

### Requirement: Continuous integration is enforcing

The GitHub Actions CI SHALL fail on lint errors and on coverage below the
configured threshold. Advisory-only checks SHALL NOT be used for lint.

#### Scenario: Lint error blocks merge
- **GIVEN** a pull request that introduces a lint error
- **WHEN** the CI workflow runs
- **THEN** the Ruff step SHALL exit non-zero
- **AND** the workflow SHALL report the failing job

#### Scenario: Coverage regression blocks merge
- **GIVEN** a pull request that drops line coverage below the configured
  threshold (currently 85%)
- **WHEN** the CI workflow runs
- **THEN** the pytest step SHALL exit non-zero
- **AND** the coverage report SHALL identify the affected files

