# Contributing

Contributions are welcome and greatly appreciated—every bit helps, and credit is always given. You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/ivbeg/qddate/issues>. When reporting:

- Include your operating system name and version.
- Describe any local setup details that might help with troubleshooting.
- Provide detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for entries tagged with `bug`—they are open to anyone who wants to tackle them.

### Implement Features

Look for issues tagged with `feature`; they are open to anyone. We especially encourage contributions that add support for new languages.

### Write Documentation

qddate always benefits from more documentation. Edit markdown in `docs/docs/`
and preview with `make docs-serve`. After changing date patterns, run
`python scripts/generate_pattern_docs.py`.

### Submit Feedback

The best way to send feedback is to open an issue at <https://github.com/ivbeg/qddate/issues>. When proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible so it remains easy to implement.
- Remember that contributions are always welcome.

## Get Started

Ready to contribute? Here's how to set up `qddate` for local development.

1. Fork the `qddate` repo on GitHub.
2. Clone your fork locally.
3. Install your local copy into a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
cd qddate/
pip install -e ".[dev,test]"
```

4. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

   Now you can make your changes locally.

5. When you're done, run Ruff and the tests:

```bash
ruff check qddate tests
pytest
```

   We use `max-line-length = 100` (configured in `pyproject.toml` and `setup.cfg`).

6. Commit your changes and push your branch:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before opening a pull request, ensure that:

1. The PR includes tests.
2. Documentation is updated if the PR adds functionality. Put new functionality inside a function with a docstring and update pages under `docs/docs/` plus the feature list in `README.md`.
3. The test suite passes on GitHub Actions for all supported Python versions.
4. You follow the core developers' guidance to keep the codebase consistent.
5. If you cannot finish a PR, leave a short comment so someone else can pick it up.

## Guidelines for Adding New Languages

English and Russian are the primary languages in qddate. All languages are pre-configured and manually added for speed optimization. Prefix matching in `qddate/dirty.py` filters patterns before pyparsing runs.

Add a module under `qddate/patterns/`, register it in `qddate/patterns/__init__.py` (`ALL_PATTERNS`, `SUPPORTED_LANGUAGES`, `_PATTERN_METADATA`), and add tests. See the documentation page **Adding languages** in `docs/docs/development/adding-languages.md`.

