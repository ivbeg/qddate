# OpenSpec Change: Harden CI and add coverage gate

Promote the GitHub Actions CI to actively enforce lint and coverage instead of
running them as advisory checks, refresh the Python matrix to current and
future-supported versions, and add a coarse performance smoke test that runs
on every CI run to catch broken-length-index regressions.

## Why

Today, `.github/workflows/ci.yml` runs Ruff with `--exit-zero` (so lint errors
never fail a build) and reports coverage as XML without ever gating on it.
`pyproject.toml` classifies Python 3.8 and 3.9 as supported — both are EOL.
And there is no perf gate, so the kind of silent regression that breaks the
length-index prefilter would only surface via the user noticing things slowed
down.

Three concrete improvements:

1. **Ruff should be a gate, not a hint.** The 259 auto-fixable errors and the
   56 line-too-long errors should fail the PR that introduces them. Today they
   don't.
2. **Python 3.8 and 3.9 are EOL.** `pyproject.toml` claims to support them; CI
   should not waste minutes confirming. Replace the matrix with 3.10–3.14.
3. **Coverage should have a floor.** The codebase is well-tested (~93%
   line coverage per the existing `--cov` runs); locking the gate at 85%
   catches new dead code without being brittle.

## What changes

**Ruff exit-zero is dropped**
- From: `ruff check . --exit-zero` (line 35 of `.github/workflows/ci.yml`).
- To: `ruff check qddate tests scripts` — fails the build on lint errors.
- Reason: Lint is a correctness tool, not a suggestion.
- Impact: Any future change that introduces a lint error fails CI. Pre-existing
  errors are fixed as part of this change (or in a follow-up commit) so the
  matrix turns green.

**Python matrix refresh**
- From: `["3.8", "3.9", "3.10", "3.11", "3.12"]`.
- To: `["3.10", "3.11", "3.12", "3.13", "3.14"]`.
- Reason: 3.8 (EOL Oct 2024) and 3.9 (EOL Oct 2025) are past end-of-life;
  continuing to test them wastes CI minutes and misleads users about support.
- Impact: Same external behaviour — qddate still works on 3.10+. The
  `requires-python = ">=3.8"` declaration in `pyproject.toml` is tightened to
  `">=3.10"` to match.

**Coverage gate**
- From: `pytest --cov=qddate --cov-report=xml` (no threshold).
- To: `pytest --cov=qddate --cov-report=xml --cov-fail-under=85`.
- Reason: Lock in current coverage as a floor; catches new dead code.
- Impact: Future dead code fails CI. The 85% threshold is comfortably below
  the current ~93% so the suite turns green immediately.

**Coarse perf smoke test (gated by env var)**
- New: `tests/test_performance_smoke.py` asserts that `parse("01.12.2009")` runs
  in under 50 ms averaged over 1,000 iterations on the CI runner. Gated by the
  `QDDATE_PERF=1` env var so local dev isn't slowed down.
- Reason: The length-index prefilter and packrat parsing are on the hot path;
  if they break (e.g. someone removes `_patterns_by_length`), the parser slows
  down by 10-100× but the unit tests don't.
- The threshold is conservative; CI runner variance is the main risk.

## Impact

- **Breaking?** No externally — same Python 3.10+ support policy already
  advertised for the project. The CI matrix and the `requires-python` field
  change in lock-step.
- **Affected:** Contributors will see Ruff errors block PRs (use
  `ruff check --fix`); a coverage drop will fail CI; a perf regression will
  fail CI on the perf smoke step.
- **Risk:** CI runner perf variance for the smoke threshold. Mitigation: gate
  behind `QDDATE_PERF=1` initially; loosen the threshold if flaky.
- **Rollback:** Revert the workflow change; thresholds revert.

## Out of scope

- Migrating from GitHub Actions to anything else — the existing workflow is
  appropriate.
- Adding per-commit benchmarks beyond the smoke step (covered by
  `benchmarks/comprehensive_performance_test.py`).
- Pre-commit hooks — orthogonal; can be a separate proposal.