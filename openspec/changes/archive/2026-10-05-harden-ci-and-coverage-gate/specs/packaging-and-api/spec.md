## MODIFIED Requirements

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

## ADDED Requirements

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