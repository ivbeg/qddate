# Specification: Packaging and Public API

The distribution, dependency, and public API surface of the `qddate` package.

## Purpose

Pin the supported Python versions, the runtime dependency footprint, and the names of
the public symbols so that releases remain installable and downstream code does not
break.

---

### Requirement: Supported Python versions

The package SHALL support Python 3.8, 3.9, 3.10, 3.11, and 3.12, on CPython and PyPy.

#### Scenario: Install on a supported interpreter
- **GIVEN** a Python 3.8–3.12 interpreter
- **WHEN** the package is installed
- **THEN** `import qddate` SHALL succeed

---

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
