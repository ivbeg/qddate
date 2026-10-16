# Tasks: Generate README stats from `ALL_PATTERNS`

## Script

- [ ] Create `scripts/generate_readme_stats.py` that reads
      `qddate.patterns.ALL_PATTERNS` and `qddate.patterns.SUPPORTED_LANGUAGES`,
      computes the counts, and prints a delimited markdown fragment.
- [ ] Test: `scripts/generate_readme_stats.py` is idempotent — running it
      twice on a clean README produces the same output.
- [ ] Test: the fragment delimiters (`<!-- BEGIN qddate-stats -->` /
      `<!-- END qddate-stats -->`) appear exactly once.

## README integration

- [ ] Insert the delimited block into `README.md`.
- [ ] Re-run the script; the README diff is just the numbers.

## CI

- [ ] New `update-readme-stats.yml` workflow that runs the script and commits
      any diff to `README.md`. Triggers on pushes to `master`.
- [ ] Or add the step to the existing `deploy-docs.yml` workflow.

## Verification

- [ ] `pytest tests/` passes 100%.
- [ ] `python scripts/generate_readme_stats.py` is idempotent.
- [ ] `ruff check scripts/` clean.
- [ ] The fragment matches the actual pattern table on every commit.