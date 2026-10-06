# OpenSpec Change: Generate README pattern counts from `ALL_PATTERNS`

The README currently hard-codes "1,072 generated date patterns (from 134 base
patterns)". When a new base pattern is added, the README drifts out of sync
until someone remembers to update it manually. This change makes the count a
function of the canonical pattern table so the README cannot lie.

## Why

The first round of work fixed the README's "1024+ / 128" → "1,072 / 134"
drift manually. The drift will recur on the next pattern addition. The
honest fix is to compute the count at docs-build time and inject it into the
README, the same way `scripts/generate_pattern_docs.py` already generates
`docs/docs/languages/<code>.md` from the canonical tables.

## What changes

**Auto-generated stats block**
- New: a "Patterns" section in `README.md` whose counts come from a script.
- The script lives at `scripts/generate_readme_stats.py` and emits a
  markdown fragment like:
  ```
  <!-- BEGIN qddate-stats -->
  - 1,072 generated date patterns (from 134 base patterns)
  - 14 supported languages
  - 95.7% test coverage
  <!-- END qddate-stats -->
  ```
- The fragment is delimited by HTML comments so it's idempotent (re-running
  the script replaces just the block).
- The README still contains the surrounding prose; only the numbers are
  generated.

**CI / docs-build hook**
- A new CI job (`update-readme-stats.yml` or a step in `deploy-docs.yml`)
  runs the script and posts a commit if the fragment changed. No-op for
  contributors locally — the script just emits the stats and exits.
- Reason: Keeps the README accurate without manual effort.

## Out of scope

- Generating the entire README from a template.
- Generating docs for non-language things (API reference, cookbook) — already
  covered by `generate_pattern_docs.py`.

## Impact

- **Breaking?** No. README text changes inside the delimited block; the
  surrounding prose is preserved.
- **Affected:** Anyone who adds a new base pattern; the README updates
  automatically.
- **Risk:** A bug in the script that computes wrong counts would mislead.
  Mitigation: the script is tiny (~50 LOC) and covered by a unit test that
  asserts it produces the same count as a manual `len(ALL_PATTERNS)` walk.
- **Rollback:** Trivial revert; the README is still valid without the script.