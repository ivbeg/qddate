# Tasks: Cleanup project hygiene

## Dependencies

- [ ] Move `dateparser>=1.2.0` out of `dependencies` in `pyproject.toml`.
- [ ] Add `[project.optional-dependencies] bench = ["dateparser>=1.2.0",
      "python-dateutil", "arrow", "pendulum"]`.
- [ ] Update `benchmarks/README*` and any CI config to install `.[bench]`.
- [ ] Verify `import qddate; qddate.DateParser()` works with only `pyparsing`
      installed (clean venv).

## Exception handling & dead imports

- [ ] Replace bare `except:` at `qdparser.py:16` with `except ImportError:`.
- [ ] Replace bare `except:` at `qdparser.py:23` with `except Exception:` (or remove
      the try/except if packrat enabling is safe to let propagate).
- [ ] Delete the `dill` import and `DILL_ENABLED` block entirely.

## Deduplicate pattern keys

- [ ] In `qddate/patterns/base.py`, remove the duplicate `pat:date:ddmmyyyy` and
      `pat:date:mmyyyy` entries (keep one of each).
- [ ] Add a test asserting `BASE_DATE_PATTERNS` has no duplicate keys.

## Repo artifacts

- [ ] `git rm --cached -r profile_results/`; add `profile_results/` to `.gitignore`.
- [ ] Delete root `tests.py` and `reproduce_issues.py`, or move under `scripts/`.
- [ ] Extend `.gitignore` for `build/`, `dist/`, `.venv*/`, `qddate.egg-info/`,
      `.pytest_cache/` (verify not already covered).
- [ ] Confirm `dateparser.code-workspace` is intentional or gitignored.

## README

- [ ] Update pattern counts: "124 base patterns → 992 generated".
- [ ] Reconcile the "Supported Languages" list with `SUPPORTED_LANGUAGES` (12 codes).
- [ ] Add a usage example showing the `languages=` parameter.

## Verification

- [ ] Clean-venv install + import succeeds without `dateparser`.
- [ ] `pytest -q` still green.
- [ ] `git status` shows no unintended deletions of source.
