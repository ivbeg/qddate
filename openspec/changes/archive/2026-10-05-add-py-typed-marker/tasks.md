# Tasks: Add py.typed marker

## Implementation

- [ ] Create `qddate/py.typed` (empty file; the marker is just its presence).
- [ ] Edit `pyproject.toml`:
      ```
      [tool.setuptools.package-data]
      "qddate" = ["py.typed", "*.md", "*.txt"]
      ```
- [ ] Build a wheel locally (`python -m build --wheel`) and verify
      `unzip -l dist/*.whl | grep py.typed` shows `qddate/py.typed`.

## Documentation

- [ ] Add a one-liner to `docs/docs/api/index.md`: "This package ships inline
      type hints (PEP 561 marker present)."

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `python -m mypy qddate/__init__.py qddate/qdparser.py` clean.
- [ ] `ruff check qddate tests scripts` clean.
- [ ] Wheel contains `qddate/py.typed`.