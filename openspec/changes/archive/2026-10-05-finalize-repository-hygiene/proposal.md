# OpenSpec Change: Finalize repository hygiene

Finish the hygiene cleanup that `IMPROVEMENT_PLAN.md` §4.5–§4.10 started:
gitignore the `benchmarks/results/` output directory that is currently committed
(105 timestamped JSON files, ~1.4 MB), delete the untracked scratch files at the
repo root, reconcile `requirements.txt` with the now-canonical `pyproject.toml`
extras, and update the README's stale pattern counts.

## Why

The earlier `cleanup-project-hygiene` change shipped the most important bits
(runtime-deps slimdown, bare-except narrowing, dedup, typo fixes) but left a
handful of small loose ends that are still confusing to new contributors:

- `benchmarks/results/` is committed. 105 timestamped performance reports and a
  baseline JSON ship with every clone and bloat history. They are regenerable
  output and have no business being in source control.
- The README claims "1024+ generated from 128 base". The actual numbers today
  are **1,072 generated from 134 base**. The discrepancy is small but tells
  readers the numbers are made up.
- `requirements.txt` lists `dateparser`, `arrow`, `pendulum`, `myst-parser` and
  others as if they were runtime deps, contradicting the now-canonical
  `pyproject.toml`. Either to fix by reducing it to a thin wrapper of the
  canonical file or to delete it.
- Untracked scratch at the repo root (`tests.py`, `reproduce_issues.py`,
  `dateparser.code-workspace`) is harmless today but a footgun for future
  commits: anyone running `git add .` will pull them in by reflex.

## What changes

**Gitignore `benchmarks/results/` and untrack its contents**
- From: 105 `performance_report_*.json` files plus `baseline_test.json` tracked
  in git (~1.4 MB committed).
- To: `benchmarks/results/` ignored; contents removed from the index; the
  directory stays in the working tree as a regeneration target.
- Reason: These are regenerable benchmark outputs.
- Impact: Non-breaking; the `comprehensive_performance_test.py` script still
  writes to this directory.

**Untrack root scratch files**
- From: `tests.py`, `reproduce_issues.py`, `dateparser.code-workspace`
  untracked at the repo root (or accidentally tracked).
- To: Either deleted or moved under `scripts/` (the legitimate ones) or gitignored
  (the personal-editor file). The script `reproduce_issues.py` is preserved
  under `scripts/` because it is referenced by the IMPROVEMENT_PLAN as the
  repro for the 2026-09 bugs.
- Reason: Prevent accidental commits; tidy repo root.

**Reconcile `requirements.txt` with `pyproject.toml`**
- From: `requirements.txt` lists 11 lines including `dateparser`, `arrow`,
  `pendulum`, `myst-parser` (some of which contradict the canonical extras).
- To: Either deleted entirely, or reduced to `-e .[dev,test,bench]`.
- Reason: One canonical place for dependencies is `pyproject.toml`.
- Impact: Non-breaking. `pip install -r requirements.txt` becomes
  `pip install -e .[dev,test,bench]` (or just the latter).

**Update README pattern counts**
- From: "1024+ generated date patterns (from 128 base patterns)".
- To: "1,072 generated date patterns (from 134 base patterns)".
- Reason: Stale numbers undermine trust.
- Impact: Non-breaking; docs only.

## Impact

- **Breaking?** No. Pure repo hygiene; externally observable behavior is
  unchanged.
- **Affected:** New contributors (less ambiguity at the repo root);
  contributors adding languages (no `tests.py` confusion); readers of the
  README.
- **Risk:** Anyone depending on `benchmarks/results/` files shipping in the repo
  loses access — but they are regenerable in seconds via
  `python benchmarks/comprehensive_performance_test.py`.
- **Rollback:** Trivial git revert.