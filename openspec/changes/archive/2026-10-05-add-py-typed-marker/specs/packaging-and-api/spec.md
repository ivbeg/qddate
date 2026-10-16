## ADDED Requirements

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