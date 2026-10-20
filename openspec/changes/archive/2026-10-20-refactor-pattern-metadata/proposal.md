# OpenSpec Change: Refactor pattern metadata

Make `language` and `separator` first-class fields on each pattern dict, then delete
the three copies of substring-based language inference and the hand-synced basekey
lists in `dirty.py`. Internal refactor; behavior unchanged. From
`IMPROVEMENT_PLAN.md` §4.1, §4.2, §6.1, §6.2.

## Why

The same fragile 12-branch chain
`if "_rus" in basekey ... elif "_bg" in basekey ...` is duplicated verbatim in
`_infer_char_sets`, `_build_language_index`, and (variant) `_calculate_priority`.
Separately, `dirty.py` keeps ~15 hardcoded basekey lists (`_DE_BASEKEYS`,
`_ES_BASEKEYS`, …) that must be hand-synced with pattern definitions — there is no
test guarding them. This is the root cause of `dirty.py` drift and a contributing
factor to the `languages=` regression fixed in Change 1.

Every pattern already *knows* its language and separator at definition time; the
information is just thrown away and re-derived from the key string.

## What changes

**Add `language` and `separator` fields to pattern definitions**
- From: Pattern dicts carry `key`, `pattern`, `length`, `format`, optional flags.
  Language and separator are re-derived from `key` substrings in three places.
- To: Each pattern dict carries explicit `language` (e.g. `"de"`, or `None` for
  language-neutral numeric patterns) and `separator` (`"slash"`, `"dot"`, `"dash"`,
  `"space"`, `"none"`, `"mixed"`).
- Reason: Replace fragile string inference with a single dict lookup.
- Impact: Non-breaking (internal data shape only); patterns gain two fields.

**Replace the three inference copies with one lookup**
- From: Three near-identical 12-branch `if/elif` chains on `basekey` substrings.
- To: A single helper, e.g. `pattern["language"]`, read wherever the language is
  needed. Net deletion of code.
- Reason: DRY; eliminates a whole class of "added a language, forgot a place" bugs.
- Impact: Non-breaking.

**Derive `dirty.py` prefix buckets from metadata**
- From: `matchPrefix()` consults ~15 manually maintained `_XX_BASEKEYS` lists.
- To: The separator/language groupings are built once at import time from the pattern
  metadata, and `matchPrefix` reads those computed groupings.
- Reason: Stops the silent drift where renaming/adding a key breaks prefix filtering.
- Impact: Non-breaking, provided a coverage test is added (see tasks).

**Centralize month/weekday table generation**
- From: Each `patterns/xx.py` re-declares month lists, LC/short/genitive variants,
  weekday lists, and `xxx_mname2mon` dicts by hand.
- To: A small helper (e.g. `month_table(full, lc=..., short=..., genitive=...)`)
  generates the `oneOf` pattern and the name→number map, removing hundreds of lines
  of boilerplate and making the `Satuday`/`jule` typo class impossible.
- Reason: Reduces per-language boilerplate and typo surface.
- Impact: Non-breaking.

## Impact

- **Breaking?** No. Internal-only refactor; `parse`/`match` behavior and the public
  API are unchanged.
- **Affected:** Contributors adding languages (much simpler); maintainers (less drift).
- **Risk:** Prefix-filtering groupings must produce identical candidate sets before
  and after — covered by a differential test (see tasks).
- **Rollback:** Self-contained revert; no public API depends on the new fields.
