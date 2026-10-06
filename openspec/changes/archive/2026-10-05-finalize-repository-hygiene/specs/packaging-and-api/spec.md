## ADDED Requirements

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