---
title: "Contributing"
description: "Development setup, tests, and documentation workflow"
---
# Contributing

Thank you for contributing to qddate. Bug reports, language patterns, and docs
fixes are all useful.

## Development setup

1. Fork and clone [ivbeg/qddate](https://github.com/ivbeg/qddate).
2. Create a virtual environment and install the package in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,test]"
```

3. Create a branch and make your change.
4. Run the test suite and linter:

```bash
ruff check qddate tests
pytest
```

Line length is 100 (Ruff / `setup.cfg`).

## Pull requests

- Include tests for new behavior or new date examples.
- Update docs in `docs/docs/` when you change the public API or add a language.
- After pattern edits, run `python scripts/generate_pattern_docs.py`.
- Keep the public surface (`DateParser`, `parse`, `match`) stable.

## Documentation site

The docs are a Docusaurus site in `docs/`:

```bash
cd docs
npm install
npm start
```

`make docs` builds the static site; `make docs-serve` starts the dev server.
See `docs/README.md`.

## Specs

Behavioral requirements live in `openspec/specs/`. Proposed changes go in
`openspec/changes/`. See `openspec/AGENTS.md` if you are editing specs.

## Related

- [Adding languages](/development/adding-languages)
- [Community](/development/community)
