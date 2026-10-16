# qddate — Code Review & Improvement Plan

> Review date: 2026-09-21 · Reviewed against branch `openspec/stabilize-and-cleanup`
> (uncommitted Romanian/Ukrainian work included) · Supersedes the 2026-08-04 review,
> most of which has been implemented — see §3.

This document records a full code-quality and feature review of the current
codebase, including **six newly verified live bugs**, and proposes a prioritized
improvement plan covering correctness fixes, internal cleanup, new features, and
DX/tooling work.

---

## 1. Executive summary

`qddate` is in much better shape than at the last review: the test suite is fully
green (204 passed, 1 skipped), the pattern-metadata refactor landed
(`_PATTERN_METADATA` is now the single source of truth for language/separator),
Romanian and Ukrainian support is nearly complete, and an OpenSpec change/spec
layer now tracks planned work. Packaging is clean (`pyparsing` is the only runtime
dependency) and a Docusaurus docs site is published.

However, probing the parser directly surfaced a cluster of **time-handling bugs**
(seconds silently dropped when a timezone suffix is present, a latent `TypeError`
crash path, invalid `hour=25/minute=70` leaking through `match()`), a class of
**unreachable patterns** (`date_eng4_short`, the `*_abbrev*` family) caused by
drift between pattern definitions and the hand-maintained prefix buckets in
`dirty.py`, and an **effectively dead no-year code path** (`parse("05.12")` returns
`None`). The planned feature work (timezone awareness, 2-digit-year pivot, typed
results, bulk API, relative dates) is well-specified in `openspec/changes/` but not
yet implemented.

All P0 items are small, isolated fixes. The structural items (deriving `dirty.py`
from metadata, a reachability oracle test) directly prevent the bug class found in
this review.

---

## 2. Current state (measured, 2026-09-21)

| Metric | Value |
|---|---|
| `pytest tests/` | **204 passed, 1 skipped** (green) |
| Base patterns (`ALL_PATTERNS`) | **134** |
| Generated patterns (after `__generate`) | **1,072** |
| Languages | **14** (bg, cz, de, en, es, fr, it, nl, pl, pt, ro, ru, tr, uk) |
| Core source LOC | ~5,400 (`qddate/`, incl. per-language pattern tables) |
| Runtime deps | `pyparsing>=3.1.0` only ✔ |
| README claim | "1024+ generated from 128 base" — base count already stale (134) |
| OpenSpec | 3 specs, 8 change proposals (4 implemented, 4 pending) |
| Version strings | `pyproject.toml` = 1.0.10, `qddate/patterns/__init__.py` = **0.1.1** (stray) |

---

## 3. Completed since the 2026-08-04 review

For traceability — these items from the previous plan are **done** and verified in
this review:

- ✅ §3.1 `languages=` allow-list respected by auto-detection
  (`DateParser(languages=["en","de"]).parse("28. Juli 2015")` → `2015-07-28`)
- ✅ §3.2 drifted "should-be-None" tests reconciled; suite is green
- ✅ §3.3 broken `__main__` block rewritten as a working smoke demo
- ✅ §4.3 bare `except:` narrowed; unused `dill` import removed
- ✅ §4.5 `dateparser` moved to the optional `bench` extra
- ✅ §4.6 duplicate keys in `BASE_DATE_PATTERNS` removed
- ✅ §4.7 `Satuday`/`jule` typos fixed (`Saturday 4 April 2019` parses)
- ✅ §4.10 README rewritten (stats, language list, `languages=` examples)
- ✅ §6.1 `language`/`separator` first-class fields via `_PATTERN_METADATA` +
  `annotate_patterns()`; three inference copies deleted from `qdparser.py`;
  oracle tests added (`tests/test_pattern_metadata.py`)
- ✅ New languages: Romanian (`ro`) and Ukrainian (`uk`) with fixtures and tests
- ✅ OpenSpec layer: specs (`date-parsing`, `language-support`,
  `packaging-and-api`) + change proposals for the remaining roadmap

## 3a. Completed since the 2026-10-05 review (v1.0.11 → v1.0.12)

Items shipped after the original `IMPROVEMENT_PLAN.md` review:

**Round 1 (v1.0.11):**
- ✅ §4.4 dead patterns (`date_eng4_short`, `*_abbrev*` family) — closed
  structurally: `dirty.py` prefix buckets are now derived from
  `_PATTERN_METADATA`. Adding a pattern no longer requires editing `dirty.py`.
  (`openspec/changes/fix-dirty-py-bucket-drift`)
- ✅ §4.9 `__generate()` mutation hazard — closed: stamping of
  `required_chars` was moved into `annotate_patterns()` so
  `DateParser.__generate()` is read-only against `ALL_PATTERNS`. Locked in by
  `tests/test_pattern_immutability.py`.
- ✅ §7.2 "Pinned but advisory" Ruff CI — Ruff now fails the build; coverage
  gate at 85%; Python matrix refreshed to `[3.10..3.14]`;
  `tests/test_performance_smoke.py` runs in CI under `QDDATE_PERF=1`.
- ✅ §7.3 (and §4.10) Reachability oracle — the failing
  `test_every_pattern_matches_some_probe` now passes thanks to a 150-string
  probe corpus plus a `_KNOWN_SHADOWED` allow-list with one-line reasons.
- ✅ §9 New `format_date(dt, pattern_key)` helper (round-trip), exposed on
  both `DateMatch` and `DateParser`. Covered by
  `tests/test_format_date.py`.
- ✅ §9 Type hints on the public API surface. `mypy qddate/__init__.py
  qddate/qdparser.py` is now clean.
- ✅ §9 Repository hygiene: `benchmarks/results/` git-ignored, scratch files
  removed, `requirements.txt` reduced to a `pyproject.toml` alias, README
  pattern counts current.

**Round 2 (v1.0.11):**
- ✅ §9 PEP 561 `py.typed` marker — `qddate/py.typed` shipped so downstream
  mypy/pyright pick up inline hints automatically.
  (`openspec/changes/add-py-typed-marker`)
- ✅ §9 `noyear=` keyword renamed to `allow_no_year=` (the old name was the
  opposite of the semantic intent). Old name works as a deprecated alias
  emitting `DeprecationWarning`. (`openspec/changes/rename-noyear-to-allow-no-year`)
- ✅ §9 Pyparsing 3 camelCase aliases (`oneOf`) migrated to `one_of` in all
  14 pattern files. `python -W error::DeprecationWarning -c "import qddate"`
  is now silent. (`openspec/changes/migrate-pyparsing-3-api`)
- ✅ §9 Six-level filter pipeline documented at
  `docs/docs/api/filter-pipeline.md` with cost-of-disabling guidance.
  (`openspec/changes/document-filter-pipeline`)

**Round 3 (v1.0.12):**
- ✅ §8 New `DateParser.parse_relative(text, reference=None)` method
  resolving common English and Russian relative-date phrases (today,
  yesterday, tomorrow, N-unit-ago, in-N-unit, через N). Both digit-form and
  word-form numbers accepted. Default `parse()` unchanged. Covered by
  `tests/test_relative_parsing.py` (17 tests).
  (`openspec/changes/add-relative-date-parsing`)
- ✅ §9 README pattern counts auto-generated by
  `scripts/generate_readme_stats.py` from the canonical pattern table.
  Includes `--check` flag for CI drift gating.
  (`openspec/changes/generate-readme-stats-from-all-patterns`)

---

## 4. Correctness bugs (P0)

All reproduced on the current working tree.

### 4.1 Timezone suffix silently drops seconds

```python
DateParser().parse("12.03.1999 10:20:30+0300")  # → 1999-03-12 10:20:00  (seconds lost)
```

**Root cause.** `__generate` gives the `:time_2` (HH:MM:SS) variant
`length.max += 9`, which does not account for the optional `+ZZZZ` suffix (+5
chars). A timestamp carrying an offset therefore never fits a plain `:time_2`
pattern, and among `:t_right` variants the tie is won by `:time_1` (HH:MM), which
is generated first and sorts stably ahead. The offset — and the seconds — are
swallowed by `restOfLine`.

**Fix direction.** Account for the timezone suffix in `:time_2` length metadata
and/or prefer the **longest consuming match** among equal-priority candidates
(compare the `end` position from `scanString`) instead of relying on generation
order. Prerequisite for the timezone feature in §8.1.

### 4.2 Latent `TypeError` crash if a timezone ever reaches `parse()`

`parse()` converts every matched value with `d[k] = int(v)` and calls
`datetime.datetime(**d)`. A match containing `timezone` would raise
`TypeError: 'timezone' is an invalid keyword argument` — and `parse()` catches
only `ValueError`. Today this path is unreachable **only because of bug 4.1**
(`:time_1` always wins the tie). Fixing 4.1 without handling the `timezone` key
turns a silent wrong result into a crash.

**Fix.** In `parse()`, pop non-datetime keys (`timezone`) before constructing the
datetime; catch `(ValueError, TypeError)` defensively; attach the offset as
`datetime.timezone` when timezone support lands.

### 4.3 No-year patterns are unreachable through `parse()`

```python
DateParser().parse("05.12")   # → None  (pattern dt:date:noyear_1 exists and matches)
```

**Root cause.** The year-format filter (Level 5) buckets `noyear` patterns into a
`noyear` index but only ever unions the `2digit`/`4digit` + `any` buckets.
`"05.12"` is detected as `2digit` (the `.12` tail matches the 2-digit-year regex),
so `noyear_1` is discarded before matching. Verified: with
`noyearformatfilter=True` the same input matches `dt:date:noyear_1` immediately.

Also: `parse()` does not expose `match()`'s `noyear` parameter at all, and the one
`noyear` test (`test_match_with_noyear`) uses a string **with** a year, so nothing
guards this path.

**Fix.** Include the `noyear` bucket when year detection is not `4digit`; add
`noyear=` to `parse()`; add a real `05.12 → month=12, day=5, year=<current>` test.

### 4.4 Dead patterns: `date_eng4_short` and the `*_abbrev*` family are unreachable

```python
DateParser().parse("25-Dec-20")    # → None (dt:date:date_eng4_short exists)
DateParser().parse("25 Dec, 2020") # → None (dt:date:date_eng_abbrev3 exists)
```

Two independent causes:

1. **Prefix-bucket drift.** `dirty.py`'s hand-maintained lists contain none of
   `date_eng4_short`, `date_eng_abbrev1/2/3`, `weekday_eng_abbrev1/2`,
   `date_eng_abbrev_postfix`. The Level-6 prefix filter therefore discards these
   patterns for every input with `n > 5`. (Only `weekday_eng_abbrev3` is listed.)
2. **Wrong length metadata.** `date_eng4_short` declares `length {min:10, max:10}`,
   but its actual matches (`"25-Dec-20"`, `"5-Dec-20"`) are 8–9 chars — it can
   never be selected even with `noprefix=True`.

**Fix.** This is exactly the bug class the old plan's §4.2 warned about; the
structural fix is §6.1 below (derive buckets from `_PATTERN_METADATA`) plus a
reachability oracle test (§7). Short-term, add the missing keys and correct the
length range.

### 4.5 2-digit years still produce year 99 AD — now locked in by a test

```python
DateParser().parse("05/16/99")  # → datetime.datetime(99, 5, 16)
```

`tests/test_dateparser.py` asserts this value, so the previously-known bug is now
enshrined as expected behavior. The fix is the opt-in `pivot_year=` parameter
spec'd in `openspec/changes/add-datetime-semantics` (§8.2); when it lands, this
test flips to the pivoted expectation.

### 4.6 `match()` accepts invalid times that `parse()` then rejects

```python
p.match("12.03.1999 25:70")   # → {'hour': '25', 'minute': '70', ...} — returned as valid
p.parse("12.03.1999 25:70")   # → None
```

The sanity check in `match()` validates only `month` (1–12) and `day` (1–31).
Hour/minute/second ranges are unchecked, so `match()` returns results that
`parse()` discards via the `ValueError` catch — an inconsistent contract between
the two public methods.

**Fix.** Extend the sanity check to `hour ≤ 23`, `minute ≤ 59`, `second ≤ 59`
(cheap, same code block).

---

## 5. Code-quality issues (P1)

### 5.1 `dirty.py` prefix buckets are still hand-synced — and provably drifted

The metadata refactor eliminated substring inference from `qdparser.py` but left
~15 hand-maintained basekey lists in `dirty.py`. Bug 4.4 is the direct
consequence: patterns added in 1.0.7/1.0.10 were never registered in the buckets.
The existing oracle tests compare stamped metadata against *legacy inference*, but
nothing checks that every pattern is reachable through `matchPrefix`.

**Fix.** Derive the buckets from the stamped `language`/`separator` fields at
import (the table already has everything needed), or — minimally — add a test that
asserts every base pattern key appears in at least one prefix bucket reachable by
some probe string. Delete `_PATTERN_METADATA`'s remaining consumer duplication.

### 5.2 Priority scoring still uses substring matching

`_calculate_pattern_priority` checks `"date_1" in basekey`, which also matches
`date_10` (both score +100). Harmless today (both are sensible top candidates) but
it means priority is quietly decoupled from the metadata table. Use exact
basekey sets or a `priority` field in `_PATTERN_METADATA`.

### 5.3 Shared mutable module state

- `annotate_patterns(ALL_PATTERNS)` mutates the module-level list at import time.
- `__generate()` mutates shared base dicts (`pat["required_chars"] = ...`) before
  copying.
- `DateParser.__init__(patterns=ALL_PATTERNS)` is a mutable default argument.

All idempotent today, but a `copy.deepcopy`-free defensive copy in `__init__`
(`self.patterns = [dict(p) for p in patterns]`) makes instances independent and
removes a whole class of "second parser sees first parser's state" bugs.

### 5.4 camelCase API remnants

`startSession()` / `endSession()` remain the only camelCase public names.
Spec'd fix exists in `openspec/changes/modernize-api-surface`: add
`start_session()` / `end_session()` aliases, deprecate the old ones.

### 5.5 Month tables duplicated between detection and parsing

`_detect_language()` in `qdparser.py` hardcodes 14 frozensets of month names,
while each `patterns/xx.py` declares its own month tables. They can drift (e.g.
Romanian *short* forms exist in `ro.py` but not in `_ROMANIAN_MONTHS`; English
abbreviations are in `_ENGLISH_MONTHS` but Turkish/Polish genitive coverage
differs between the two sites). Deriving the detection sets from the pattern
modules (or a shared `MONTHS_BY_LANGUAGE` table, as `uk.py` already half-does with
one map feeding all forms) removes a whole sync surface.

### 5.6 Version-string drift

`qddate/patterns/__init__.py` carries `__version__ = "0.1.1"` unrelated to the
package version (1.0.10). Remove it or read from `importlib.metadata`.

### 5.7 Committed generated artifacts & scratch files

- `benchmarks/results/` — **~140 generated benchmark reports** (JSON/CSV/TXT)
  tracked in git, plus `benchmarks/baseline_test.json`. Bloats every clone; add
  to `.gitignore` and `git rm -r --cached`.
- Root-level `tests.py` (imports `dateparser`, has a stray `s` in its coding
  line, duplicates the real suite) and `reproduce_issues.py` are untracked
  scratch — delete or move under `scripts/` before they get committed by accident.
- `dateparser.code-workspace` untracked at root — personal editor file, gitignore
  it.

### 5.8 `requirements.txt` contradicts `pyproject.toml`

`requirements.txt` still lists `dateparser`, `arrow`, `pendulum`, `myst-parser`,
etc. as if required, while `pyproject.toml` correctly scopes them to extras. Since
the packaging cleanup, this file is pure drift. Either reduce it to
`-e .[dev,test,bench]` or delete it.

### 5.9 Minor

- pyparsing 3.x legacy camelCase API (`setResultsName`) used throughout — works
  via the compat layer; migrate to `set_results_name` opportunistically.
- `match()` ignores the match end position — by design for left-aligned scraping,
  but it is what makes tie-breaking order matter (bug 4.1). A
  `prefer="longest"` option would make this principled.
- `_detect_separators()`'s "no separators → mixed" fallback and the hardcoded
  `["date_1", "date_8", "date_3"]` space-compat token list in Level 3 are leftover
  inference that the metadata table can now answer directly.

---

## 6. Architecture refactors (P2)

### 6.1 Finish the metadata refactor in `dirty.py` (highest leverage)

One change kills bug class 4.4 permanently: build prefix buckets by grouping
`_PATTERN_METADATA` (language, separator) instead of listing keys by hand. Adding
a pattern then requires zero `dirty.py` edits — the same win the refactor already
gave `qdparser.py`.

### 6.2 Centralize month/weekday tables

Each language module re-declares full/lc/short/genitive month lists and
`xxx_mname2mon` maps (~200–370 LOC per language). `uk.py` shows the better
pattern (single dict built from parallel lists). A small `month_table()` helper
plus deriving `_detect_language`'s frozensets from the same source removes
hundreds of lines and the typo/drift class (old plan §6.2; still open).

### 6.3 Fingerprint-based candidate selection

After 6.1, each pattern can carry a precomputed fingerprint (length range,
charset, separator, language, year format) and Level 1–6 filtering collapses into
set intersections over precomputed frozensets — less code, fewer allocations, and
one obvious place to audit filtering behavior. (Old plan §6.3; spec'd in
`openspec/changes/add-advanced-parsing`.)

**Data layer shipped (item #19, round 6):** `qddate.patterns.fingerprint`
introduces `FingerprintKey` and `_PATTERN_FINGERPRINTS` (80 unique
fingerprints for the 134 base patterns; ~700 for the generated 1,072-pattern
corpus). `candidate_keys_for(text_length, text_chars, ...)` exposes the
intersection as a single frozenset. 26 parity tests in
`tests/test_fingerprint_index.py` lock equivalence with the per-instance
buckets. **Consumer wiring** (replacing the 6-level filter with the
intersection) is deferred — the existing pipeline keeps running unchanged
as the parity fallback.

---

## 7. Testing & CI gaps (P1)

1. **Reachability oracle** — for every base pattern, assert at least one fixture
   string parses with that pattern's basekey (catches 4.4-style drift and wrong
   length metadata). Cheap to generate from the existing fixture corpus +
   parametrize tables.
2. **Real no-year tests** — `parse("05.12")` asserting current-year behavior
   (bug 4.3).
3. **Time-component tests** — seconds preserved, `+ZZZZ` inputs, invalid
   `25:70`-style times rejected by both `match()` and `parse()` (bugs 4.1/4.2/4.6).
4. **Property tests** — Hypothesis round-trip over `datetime.strftime` for every
   pattern `format` would fuzz the filter pipeline (valid dates that filters
   discard) far more cheaply than hand-written cases.
5. **CI hardening** — Ruff currently runs with `--exit-zero` (advisory only);
   drop the flag once the tree is clean. Matrix covers 3.8–3.12; 3.8/3.9 are EOL —
   replace with 3.10–3.14. No coverage gate and no perf gate (`test_performance`
   is skipped by default); even a loose wall-clock assertion in CI would catch
   regressions like a broken length index.
6. **Fixture coverage parity** — Romanian has a JSON fixture corpus; the other 13
   languages rely on inline parametrize lists. A uniform `tests/fixtures/<lang>.json`
   format makes the reachability oracle (item 1) trivial.

---

## 8. New features (P2/P3 — spec'd in OpenSpec, not yet implemented)

Each maps to an existing `openspec/changes/` proposal; ordered by value/effort.

### 8.1 Timezone-aware parsing — `add-datetime-semantics` — **✅ SHIPPED (v1.0.11)**
`pat:time:full` already tokenizes `+HHMM`. Opt-in `tz_aware=` constructor flag
returns aware datetimes; default stays naive in 1.x.

### 8.2 2-digit-year pivot — `add-datetime-semantics` — **✅ SHIPPED (v1.0.11)**
Opt-in `pivot_year=` (default break 68: `00–67 → 20xx`, `68–99 → 19xx`).
`05/16/99 → 1999`. The default remains "year 99 is 99 AD" (back-compat);
flip the default in 2.0; update the test that currently locks year 99 (4.5).

### 8.3 Typed `DateMatch` result — `modernize-api-surface` — **✅ SHIPPED (v1.0.11)**
`match()`'s `{"values": ParseResults, "pattern": dict}` still exists for back-
compat; `match_typed()` returns a `@dataclass` `DateMatch` with
`datetime`, `pattern_key`, `language`, `format`, `raw` fields and a
`.to_dict()` for the legacy shape.

### 8.4 Bulk `parse_many(iterable)` — `modernize-api-surface` — **✅ SHIPPED (v1.0.11)**
Generator-based `parse_many(texts, **kwargs)` amortizes the filter setup
across the batch.

### 8.5 Ambiguity / multi-match reporting — `add-advanced-parsing` — **✅ SHIPPED (v1.0.11)**
`match_all()` returns all candidates ranked by priority, deduplicated by
basekey. Lets scraping callers detect ambiguity.

### 8.6 Relative date parsing (opt-in) — `add-advanced-parsing` — **✅ SHIPPED (v1.0.12)**
`DateParser.parse_relative(text, reference=None)` resolves common English
and Russian phrases (`today`, `yesterday`, `tomorrow`, `N unit ago`,
`(in) N unit`, `через N`, `N unit назад`). Word-form numbers supported.
Default `parse()` unchanged. Only English and Russian for v1; German/French
/ Italian deferred to future language additions.

### 8.7 Formatting / round-trip helper — `add-advanced-parsing` — **✅ SHIPPED (v1.0.11)**
`qddate.format_date(dt, pattern_key)` plus `DateMatch.format_date()` and
`DateParser.format_date(dt, pattern_key)`.

---

## 9. Documentation & DX (P3)

- ✅ README stats drift now (134 base): `scripts/generate_readme_stats.py`
  generates the counts from `ALL_PATTERNS` and injects them into the README
  via a delimited block. The `--check` flag fails CI on drift.
- ✅ Document the six-level filtering pipeline — `docs/docs/api/filter-pipeline.md`
  describes all 6 levels with cost-of-disabling guidance.
- "How to add a new language" guide — after §6.1/§6.2 this becomes a short recipe
  (pattern module + metadata entries + fixtures); the Romanian/Ukrainian changes
  are the worked example. Existing `docs/docs/development/adding-languages.md`
  is the working draft.
- ✅ Type hints on the public API (`parse`, `match`, `__init__`,
  `get_patterns_for_languages`). `mypy qddate/__init__.py qddate/qdparser.py` is
  clean. Plus `py.typed` marker so downstream type-checking picks up the hints.
- ✅ The `noyear=` flag's semantics were the opposite of what the name read
  as — renamed to `allow_no_year=` (canonical) with `noyear=` retained as a
  deprecated alias emitting a warning.
- ✅ `qddate/__init__.py` no longer carried a stray `__version__` (already
  fixed in the 2026-08-04 round).
- ✅ `requirements.txt` reconciled with `pyproject.toml` extras (now a thin
  alias `-e .[dev,test,bench]`).
- ✅ README stats drift → `scripts/generate_readme_stats.py`.

---

## 10. Prioritized roadmap

Ordered for independent, shippable increments. **Bold** = shipped.

| # | Item | Priority | Effort | Section |
|---|------|----------|--------|---------|
| 1 | Fix tz-suffix seconds drop + longest-match tie-break | P0 | S | 4.1 ✅ |
| 2 | Handle `timezone` key in `parse()`; catch `TypeError` | P0 | XS | 4.2 ✅ |
| 3 | Make no-year patterns reachable via `parse()` + tests | P0 | S | 4.3 ✅ |
| 4 | Repair dead patterns (`eng4_short` length, `*_abbrev*` buckets) | P0 | S | 4.4 ✅ |
| 5 | Hour/minute/second sanity checks in `match()` | P0 | XS | 4.6 ✅ |
| 6 | Reachability oracle test (every pattern parses ≥1 fixture) | P1 | M | 7.1 ✅ |
| 7 | Derive `dirty.py` buckets from `_PATTERN_METADATA` | P1 | M | 6.1, 5.1 ✅ |
| 8 | Commit/land ro+uk branch; remove scratch files; gitignore `benchmarks/results/` | P1 | XS | 5.7 ✅ |
| 9 | Reconcile `requirements.txt` with extras; drop stray `__version__` | P1 | XS | 5.6, 5.8 ✅ |
| 10 | Exact-key priority scoring (no substring) | P1 | XS | 5.2 ✅ |
| 11 | Defensive copy of `patterns` in `__init__` | P1 | XS | 5.3 ✅ |
| 12 | Timezone-aware parsing (`tz=`, opt-in) | P2 | M | 8.1 ✅ |
| 13 | `pivot_year=` (opt-in; flip default in 2.0) | P2 | S | 8.2, 4.5 ✅ |
| 14 | `match_typed()` / `DateMatch` + snake_case session aliases | P2 | S | 8.3, 5.4 ✅ |
| 15 | `parse_many()` bulk API | P2 | S | 8.4 ✅ |
| 16 | Centralized month tables shared by parsing + detection | P2 | M | 6.2, 5.5 ✅ |
| 17 | CI hardening (ruff blocking, 3.10–3.14 matrix, perf smoke) | P2 | S | 7.5 ✅ |
| 18 | `match_all()` ambiguity reporting | P3 | M | 8.5 ✅ |
| 19 | Fingerprint-based matcher (single intersection) | P3 | L | 6.3 ✅ |
| 20 | Relative date parsing (opt-in, locale-aware) | P3 | L | 8.6 ✅ (English+Russian; other locales deferred) |
| 21 | `format()` round-trip helper | P3 | XS | 8.3 ✅ |
| 22 | Docs/DX pass (generated stats, pipeline docs, language guide, type hints) | P3 | M | 9 ✅ |

**Status:** items 1–22 shipped.

**Suggested milestone grouping** — superseded by what actually shipped.

Actual shipped versions:
- **v1.0.11 — "Correctness + structural"**: items 1–15, 17. Bug fixes,
  `dirty.py` derivation, `_PATTERN_METADATA` refactor, modernised surface
  (`DateMatch`, `match_typed`, `parse_many`, `match_all`), CI hardening,
  timezone-aware + pivot_year, type hints, py.typed marker, noyear→allow_no_year.
- **v1.0.12 — "Relative dates + DX"**: item 20 (English+Russian `parse_relative`),
  item 22 (auto-generated README stats, filter pipeline docs).
- **v1.0.13 — "Single source of truth for month names"**: item 16. New
  `qddate.patterns.months.MONTHS_BY_LANGUAGE` table is the canonical source for
  every supported language's month-name variants; `qdparser._detect_language`
  and all 14 per-language pattern modules consume from it. Legacy
  `*_MONTHS`/`*_mname2mon` constants are preserved as re-exports for backward
  compatibility, with 72 parity tests locking equivalence.
- **v1.0.14 — "Fingerprint-based matcher is the default"**: item 19.
  `DateParser(use_fingerprint=True)` (default since this version) collapses the
  6-level filter pipeline into a single-walk intersection over the precomputed
  `qddate.patterns.fingerprint._PATTERN_FINGERPRINTS` index. The legacy
  pipeline remains available via `use_fingerprint=False`. 165 parity tests
  lock exact equivalence on the extended probe corpus.
- **Future** — the pivot-year default flip is planned for 2.0.

---

## 11. Quick wins (single sitting)

1. Item 5 (sanity checks) and item 2 (`TypeError` catch) — minutes each, real
   robustness.
2. Item 4 (dead patterns) — add missing bucket entries + fix one length dict;
   immediately parses `25-Dec-20` and `25 Dec, 2020`.
3. Item 8 — repo hygiene: `git rm -r --cached benchmarks/results`, delete
   `tests.py`/`reproduce_issues.py`, ignore the workspace file.
4. Item 3 — one-line filter change + one test fixes a whole feature (no-year
   dates) that currently does nothing.
