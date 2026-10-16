# OpenSpec Change: Cleanup project hygiene

P1 hygiene fixes from `IMPROVEMENT_PLAN.md` §4.3, §4.5, §4.6, §4.9, §4.10. No behavior
change; the package installs leaner, the repo stops shipping build artifacts, and the
README stops lying about counts.

## Why

- `dateparser` (a large, slow library) is declared as a **hard runtime** dependency
  but is never imported by the library — only by `benchmarks/`. This contradicts the
  project's "minimal deps / fast install" positioning and forces every installer to
  download it.
- Bare `except:` clauses swallow `KeyboardInterrupt` and other unrelated errors.
- `dill` is imported at module load but never used.
- `BASE_DATE_PATTERNS` has duplicate keys that silently overwrite.
- Committed artifacts (`profile_results/`, root-level `tests.py`, `reproduce_issues.py`)
  clutter the repo.
- README claims "712+ patterns from 89 base"; actual is 992 from 124.

## What changes

**Runtime dependency瘦身**
- From: `dependencies = ["dateparser>=1.2.0", "pyparsing>=3.1.0"]`.
- To: `dependencies = ["pyparsing>=3.1.0"]`, with a new optional extra
  `[project.optional-dependencies] bench = ["dateparser>=1.2.0", "python-dateutil",
  "arrow", "pendulum"]`.
- Reason: `dateparser` is benchmark-only; runtime never imports it.
- Impact: Non-breaking. Installers no longer pull `dateparser` unless they opt into
  the `bench` extra. `benchmarks/` users install with `pip install -e .[bench]`.

**Narrow exception handling**
- From: `try: import dill ... except:` and `try: enable_packrat() ... except:` (both
  bare).
- To: `except ImportError:` for `dill`; `except Exception:` (or removal) for packrat.
- Reason: Bare `except:` catches `KeyboardInterrupt`/`SystemExit`.
- Impact: Non-breaking.

**Remove unused `dill` import**
- From: `qdparser.py` imports `dill` and sets `DILL_ENABLED`, which is never read.
- To: Delete the import and the flag entirely.
- Reason: Dead code; adds an optional import to the hot module.
- Impact: Non-breaking.

**Deduplicate `BASE_DATE_PATTERNS` keys**
- From: `pat:date:ddmmyyyy` and `pat:date:mmyyyy` are each defined twice (the second
  silently overwrites the first).
- To: Each key appears exactly once.
- Reason: Duplicate keys are a latent trap; harmless only because the bodies match.
- Impact: Non-breaking (identical bodies).

**Stop committing artifacts**
- From: `profile_results/`, root `tests.py`, `reproduce_issues.py` are tracked.
- To: They are removed from git (or relocated under `scripts/`) and gitignored;
  `.gitignore` is extended to cover `build/`, `dist/`, `.venv*/`, `qddate.egg-info/`,
  `.pytest_cache/`.
- Reason: Generated/ad-hoc files should not live in version control.
- Impact: Non-breaking. Consumers unaffected.

**Correct README statistics and language list**
- From: README claims "712+ date patterns (expanded from 89 base patterns)" and a
  language list that may diverge from `SUPPORTED_LANGUAGES`.
- To: README reports current counts (124 base → 992 generated) and lists exactly the
  twelve supported languages.
- Reason: Documentation accuracy; counts drift every release if hand-maintained.
- Impact: Non-breaking. Docs only.

## Impact

- **Breaking?** No.
- **Affected:** All installers (smaller dependency closure); contributors (cleaner
  repo); anyone reading the README.
- **Rollback:** Trivial per-file revert.
