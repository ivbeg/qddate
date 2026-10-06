# OpenSpec Change: Fix dirty.py bucket drift

The `matchPrefix()` prefix-bucket lists in `qddate/dirty.py` are still
hand-maintained. The metadata refactor shipped the data they need to be derived
from, but never wired it up. This change finishes the job: build the buckets
mechanically from `_PATTERN_METADATA` so adding a pattern no longer requires
editing `dirty.py` at all. The bug class from `IMPROVEMENT_PLAN.md` §4.4
(unreachable patterns because they were not registered in the prefix buckets)
becomes structurally impossible.

## Why

`qddate/dirty.py` keeps ~15 manually maintained basekey lists
(`_ALPHA_ENGLISH_BASEKEYS`, `_DOT_SEPARATOR_BASEKEYS`, `_DASH_SEPARATOR_BASEKEYS`,
`_DE_BASEKEYS`, `_ES_BASEKEYS`, …). Adding a pattern means:

- Adding a `dt:date:<key>` definition in a `patterns/<lang>.py` module.
- Adding an entry to `ALL_PATTERNS` in `patterns/__init__.py`.
- Adding a `(language, separator)` entry to `_PATTERN_METADATA`.
- **Adding the same key to one or more bucket lists in `dirty.py`** — this step
  has no compile-time or test-time guard except the existing
  `test_every_pattern_key_in_some_prefix_bucket` test, which is a coarse check.

This was the root cause of bug 4.4 in `IMPROVEMENT_PLAN.md` (`date_eng4_short`
and the `*_abbrev*` family were unreachable because they were missing from the
buckets). The bug was fixed by adding the missing keys — but the structural
problem remains. The next time someone adds a pattern, they can hit it again.

The metadata table already has everything `dirty.py` needs: `language` and
`separator` for every basekey. A single grouping pass over `ALL_PATTERNS` builds
the same buckets mechanically. Adding a pattern then requires **zero**
`dirty.py` edits.

## What changes

**Derive prefix buckets from `_PATTERN_METADATA`**
- From: ~15 hand-synced `_XX_BASEKEYS` lists in `dirty.py`, each maintained by
  the author of the corresponding language module.
- To: A single `_build_buckets()` pass at import time that groups `ALL_PATTERNS`
  by `(separator, language)` using the stamped metadata fields. The bucket
  keys/values are computed once and frozen into module-level tuples (same
  shape `matchPrefix` already expects).
- Reason: The metadata table is the single source of truth; `dirty.py` should
  read it, not duplicate it.
- Impact: Non-breaking, provided the resulting candidate sets are identical
  (verified by the existing oracle tests in `tests/test_pattern_metadata.py` and
  the probe corpus).

**Keep one safety-net test, drop the others**
- From: `test_every_pattern_key_in_some_prefix_bucket` and
  `test_bucket_keys_exist_in_metadata` in
  `tests/test_regressions_2026_09.py` test the *hand-synced* lists.
- To: Keep `test_bucket_keys_exist_in_metadata` (the stale-keys check is still
  useful). Replace `test_every_pattern_key_in_some_prefix_bucket` with an
  equivalent test against the *derived* buckets.
- Reason: The hand-synced lists go away; the test must target the new source.
- Impact: Non-breaking. Test-only change.

**Add a behavioral parity test**
- New: For a corpus of probe strings, assert that `matchPrefix(text[:6])`
  returns the same set of basekeys before and after the change.
- Reason: Guards against silent regression in the prefix-bucket logic, which is
  on the hot path for every parse call.
- Impact: Non-breaking. Test-only.

## Impact

- **Breaking?** No. The derived buckets must produce the same candidate sets
  the hand-synced lists did; verified by a parity test before the change is
  merged.
- **Affected:** Contributors adding languages (one less file to touch);
  maintainers (no more silent drift).
- **Risk:** If the grouping logic disagrees with the hand-synced lists, some
  inputs may silently start (or stop) matching. Mitigated by the parity test
  above; the existing reachability oracle will catch any net loss.
- **Rollback:** Self-contained revert; `dirty.py` reverts to its previous
  shape.