# Tasks: Harden CI and add coverage gate

## Ruff gating

- [ ] Run `ruff check qddate tests scripts --fix` to auto-fix the 259
      fixable errors (whitespace, trailing space, unsorted imports).
- [ ] Manually fix the remaining ~83 errors (mostly E501 line-too-long; a few
      F401 unused imports).
- [ ] Edit `.github/workflows/ci.yml` to drop `--exit-zero` from the Ruff step.
- [ ] Confirm the new Ruff command is `ruff check qddate tests scripts`.

## Python matrix refresh

- [ ] Edit `.github/workflows/ci.yml` matrix:
      `python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]`.
- [ ] Edit `pyproject.toml` `requires-python = ">=3.10"`.
- [ ] Edit `tox.ini` `envlist = py310,py311,py312,py313,py314`.
- [ ] Edit the classifiers in `pyproject.toml` to drop 3.8 and 3.9 and add
      3.13 and 3.14.

## Coverage gate

- [ ] Edit `.github/workflows/ci.yml` pytest step:
      `pytest --cov=qddate --cov-report=xml --cov-fail-under=85`.
- [ ] Verify local coverage is comfortably above 85% by running
      `pytest --cov=qddate` once.

## Perf smoke test

- [ ] Add `tests/test_performance_smoke.py` with a single smoke test gated by
      `@pytest.mark.skipif(not os.environ.get("QDDATE_PERF"), reason="perf-gated")`.
- [ ] The test constructs a `DateParser`, times 1,000 iterations of
      `parse("01.12.2009")`, and asserts the mean is under 50 ms.
- [ ] Edit `.github/workflows/ci.yml` to set `QDDATE_PERF=1` in the perf job's
      env (or in the main test job's env so it runs by default).

## Verification

- [ ] `pytest tests/` passes locally.
- [ ] `pytest tests/test_performance_smoke.py` passes when `QDDATE_PERF=1`.
- [ ] `ruff check qddate tests scripts` returns zero errors.
- [ ] `pytest --cov=qddate --cov-fail-under=85` passes locally.
- [ ] The full `.github/workflows/ci.yml` is re-read and confirmed coherent.