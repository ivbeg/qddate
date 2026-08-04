# qddate — Code Review & Improvement Plan

> Review date: 2026-08-04 · Reviewed against `master` @ `50eb2f3` (v1.0.10)

This document records the findings of a full code-quality and feature review of the
`qddate` codebase, and proposes a prioritized, actionable improvement plan. It is
organized from **must-fix correctness bugs** down to **new features** and
**long-term architecture** work.

---

## 1. Executive summary

`qddate` is a mature, fast, pragmatic date parser. Its core idea — pre-generated
pyparsing patterns combined with multi-level candidate filtering — works well and
the performance engineering is serious. However, the review uncovered:

- **4 currently-failing tests** (`pytest` exits non-zero on `master`), one of which
  exposes a **real functional regression** in the `languages=` feature shipped in 1.0.6.
- A **broken `__main__` block** that raises `NameError` on first use.
- A **fragile language model** where a language is inferred from pattern *key
  substrings* instead of being a first-class field — the root cause of the regression
  above and of several latent bugs.
- **Duplicated logic** (the same 12-branch language inference is copy-pasted 3×).
- **Hygiene issues**: bare `except:`, an unnecessary heavy runtime dependency
  (`dateparser`), duplicate dict keys, typos in month/weekday tables, inaccurate
  README claims, and committed build artifacts.
- **Missing capabilities** users likely expect: timezone handling, relative dates
  ("yesterday"), 2-digit-year pivot, and a typed result object.

None of the structural problems are hard to fix incrementally without breaking the
public API. The plan below is ordered so each phase is independently shippable.

---

## 2. Current state (measured)

| Metric | Value |
|---|---|
| Base patterns (`ALL_PATTERNS`) | **124** |
| Generated patterns (after `__generate`) | **992** |
| README claim | "712+ from 89 base" ← **stale / inaccurate** |
| Languages | 12 (bg, cz, de, en, es, fr, it, nl, pl, pt, ru, tr) |
| `pytest` result on `master` | **4 failed, 128 passed, 1 skipped** |
| Core source LOC | ~5,865 (incl. per-language pattern tables) |
| Runtime deps in `pyproject.toml` | `pyparsing>=3.1.0`, **`dateparser>=1.2.0`** |

---

## 3. Correctness bugs (P0 — fix immediately)

These are shipped behavior that is wrong. Each has a concrete reproduction.

### 3.1 `languages=["en","de"]` drops German dates → failing test

**Repro**
```python
from qddate import DateParser
DateParser(languages=["en", "de"]).parse("28. Juli 2015")  # → None (should be 2015-07-28)
```
`tests/test_dateparser.py::test_language_filtering_multiple_languages` fails on this.

**Root cause.** `_detect_language()` is consulted by `_filter_patterns_hierarchical()`
(Level 4). The month name "Juli" is shared between German and Dutch, and the detector
checks Dutch before German, so it returns `['nl']`. Because the filter only narrows
when *exactly one* language is detected, all non-Dutch patterns — including every
German pattern — are discarded, even though the user explicitly requested `de`.

**Fix direction.** The language filter must respect the user-supplied `languages=`
allow-list and never narrow below it. Concretely: when `languages=` is set, skip
auto-detection narrowing entirely (the pattern set is already constrained at
construction time), or intersect detected languages with the allow-list. See §6.1
for the structural fix that prevents this class of bug.

### 3.2 Three "should return None" tests now return dates

`test_parse_returns_none_for_unsupported_text` fails for:
- `14th April 2015:` → returns `2015-04-14`
- `15. Jul 2023` → returns `2023-07-15`
- `5. jan 2020` → returns `2020-01-05`

**Root cause.** 1.0.7 added German short-month patterns (`de_short`, `de_short_lc`)
and English ordinal/abbreviation patterns. The tests were written when those formats
were unsupported and were never reconciled.

**Decision required.** These are *correct* parses by today's grammar; the tests are
wrong, not the code. Recommended resolution: move these cases into the
`test_parse_supported_text` parametrization with their expected `datetime` values
(i.e. accept the new behavior), rather than weakening the grammar. The trailing
`:` in `14th April 2015:` is already handled by left-aligned matching, which is
desirable.

### 3.3 Broken `__main__` block in `qdparser.py`

`qdparser.py:1063-1076`:
```python
for text in tests:
    res = ind.match(text)
    print(r)          # <-- NameError: 'r' is undefined on first iteration
    if r:
        r = res["values"]
```
`r` is referenced before assignment, and `dateparser` is used without import. Running
`python qddate/qdparser.py` crashes immediately.

**Fix.** Rewrite to match the `parse()` path (use `ind.parse(text)`), or delete the
block entirely — the test suite is the canonical runner. A stale, broken demo block
misleads contributors.

### 3.4 2-digit years produce year 99 AD

```python
DateParser().parse("05/16/99")  # → datetime.datetime(99, 5, 16)
```
This is technically what `datetime` does with `%y`, but for a scraping tool a
year-99 AD result is almost never what the user wants. See §7.2 (pivot year).

---

## 4. Code-quality issues (P1)

### 4.1 Language is inferred from key substrings — three times

The same 12-branch chain
```python
if "_rus" in basekey or "rus_" in basekey: lang = 'ru'
elif "_bg" in basekey ...:                 lang = 'bg'
... (×12)
```
is duplicated verbatim in `_infer_char_sets`, `_build_language_index`, and (in a
variant form) `_calculate_pattern_priority`. It is:

- **Fragile** — adding a language or renaming a key requires touching 3+ places.
- **Ambiguous** — `"_de" in basekey` also matches keys containing `..._de...` for
  unrelated reasons; substring tests on free-form strings are the source of the
  Dutch/German misclassification.
- **Unnecessary** — every pattern dict already knows its language at definition time.

**Fix (structural, §6.1):** add a `"language"` field to each pattern dict at
definition, and replace all three copies with a single dict lookup. This is the
single highest-leverage refactor in the codebase.

### 4.2 `dirty.py` basekey lists must be hand-synced

`matchPrefix()` relies on ~15 hardcoded lists (`_DE_BASEKEYS`, `_ES_BASEKEYS`, …)
that must be manually kept in sync with the pattern definitions. If a pattern key is
renamed or added without updating these lists, filtering silently excludes it.
There is no test guarding this invariant.

**Fix.** Derive these groupings from pattern metadata (the `"language"` and a new
`"separator"` field) at import time, or add a test that asserts every pattern key is
covered by exactly one prefix bucket.

### 4.3 Bare `except:` clauses

`qdparser.py:16` and `:23` swallow *all* exceptions (including `KeyboardInterrupt`):
```python
try:
   import dill
   DILL_ENABLED = True
except:
   DILL_ENABLED = False
```
**Fix.** `except ImportError:`. Also: `dill` is imported but **never used** anywhere
in the library — drop it entirely (see §4.5).

### 4.4 Mutable shared default / tuple reassignment

`__init__(self, ..., patterns=ALL_PATTERNS)` is fine because `ALL_PATTERNS` is a
tuple, but `__generate()` then does `self.patterns = base` (a list) and mutates the
shallow-copied dicts' `pattern`/`length`/`key` fields in place across calls. A second
`DateParser()` constructed from a previously-generated `patterns` list can see
mutated state. Low severity today (constructors always start from the module tuple),
but worth a comment or a defensive copy.

### 4.5 `dateparser` is an unnecessary runtime dependency

`pyproject.toml` declares `dateparser>=1.2.0` as a hard runtime dependency, but it
is **only imported by `benchmarks/`**. The library itself never imports it. This
forces every installer to pull in a large, slow package — directly contradicting the
project's "minimal deps / fast install" positioning.

**Fix.** Move `dateparser` (and `dateutil`, `arrow`, `pendulum`) to an optional
`[project.optional-dependencies] bench = [...]` extra.

### 4.6 Duplicate keys in `BASE_DATE_PATTERNS`

`patterns/base.py` defines `pat:date:ddmmyyyy` twice (lines 67 and 74) and
`pat:date:mmyyyy` twice (lines 71 and 78). The second definitions silently overwrite
the first. Harmless today (identical), but a latent trap.

### 4.7 Typos in English tables

- `ENG_WEEKDAYS`: `"Satuday"` → `"Saturday"`
- `ENG_MONTHS_LC`: `"jule"` → `"july"`

`"Satuday"` means the full weekday `"Saturday"` will never match (only the short
form `"sat"` works). This is a real parsing bug for `Saturday 4 April 2019`-style
strings.

### 4.8 Inconsistent API naming

`startSession()` / `endSession()` use camelCase, contrary to PEP 8 and the rest of
the API (`parse`, `match`, `_build_length_index`). Provide snake_case aliases
(`start_session`, `end_session`) and deprecate the old names.

### 4.9 Committed artifacts & stale files

Tracked in git (should be in `.gitignore` or removed):
- `profile_results/` (profiling output)
- `reproduce_issues.py`, `tests.py` (root-level ad-hoc scripts, duplicate the
  `tests/` package)
- `build/`, `dist/`, `.venv*/`, `.pytest_cache/`, `qddate.egg-info/` exist on disk
  (verify they are gitignored).

**Fix.** Clean `.gitignore`, `git rm --cached` the artifacts, and delete the
root-level `tests.py` / `reproduce_issues.py` or move them under `scripts/`.

### 4.10 README is stale

- Claims "712+ patterns from 89 base" — actual is **992 from 124**.
- "Supported Languages" section in README differs from `SUPPORTED_LANGUAGES`.
- Usage examples should include the new `languages=` parameter.

---

## 5. Testing gaps (P1)

- **No regression test for `languages=` + auto-detection interaction** — this is
  exactly what let §3.1 ship.
- **No test that every pattern is reachable** through `matchPrefix` / the length
  index (guards §4.2).
- **`test_performance.py` asserts loose thresholds** (10 ms/parse) and is skipped by
  default; there is no CI gate on perf regressions.
- **No tests for the `match()` return contract** across all languages (only EN/RU
  are exercised in depth).
- **Fuzzing/property tests** would catch the "valid date that filters discard" class
  of bug cheaply (e.g. Hypothesis over `datetime.strftime` round-trips).

---

## 6. Architecture refactor (P2 — high leverage)

### 6.1 Make `language` (and `separator`) first-class pattern fields

Today a pattern dict looks like:
```python
{"key": "dt:date:de_base", "pattern": ..., "length": {...}, "format": "%d %m %Y"}
```
and the language is *re-derived* from the string `"de_base"` in three places.

Proposed:
```python
{"key": "dt:date:de_base", "language": "de", "separator": "space",
 "pattern": ..., "length": {...}, "format": "%d %m %Y"}
```
Then:
- `_build_language_index`, `_infer_char_sets`, `_build_separator_index`, and the
  `dirty.py` prefix buckets all become a single group-by over a real field.
- `_detect_language`'s narrowing is intersected with the user's `languages=`
  allow-list (fixes §3.1 structurally).
- Adding a language = adding a `patterns/xx.py` + one import; zero changes to
  `qdparser.py` or `dirty.py`.

This is a mechanical, low-risk change because all current languages have unambiguous
definitions; it mostly *deletes* code.

### 6.2 Centralize month/weekday tables

Each `patterns/xx.py` re-declares month lists, LC variants, short variants, weekday
lists, and the `xxx_mname2mon` dicts by hand. A tiny helper:
```python
def month_table(full, *, lc=None, short=None, genitive=None):
    """Returns (oneOf_pattern, name_to_number_map)."""
```
would remove hundreds of lines of boilerplate and eliminate the `jule`/`Satuday`
class of typo (§4.7) by construction.

### 6.3 Replace ad-hoc filtering with a single compiled matcher

The six filter levels (length → charset → separator → language → year-format →
prefix) are individually reasonable but are stitched together with many temporary
list comprehensions and `set` round-trips in `_filter_patterns_hierarchical`. After
§6.1, each pattern can carry a cheap `fingerprint` (length-range, charset, separator,
language, year-format) and the candidate set becomes a single set-intersection over
precomputed frozensets — dramatically less code and fewer allocations.

---

## 7. New features (P2/P3)

These extend capability without changing the existing API contract.

### 7.1 Timezone awareness

`pat:time:full` already parses a `+HHMM` offset but discards it. Return
`timezone-aware` datetimes (or attach the offset) and add a `tz=` / `to_utc=`
option. High value for scraped news timestamps.

### 7.2 2-digit-year pivot

Add `pivot_year` / `century_break` (default 1968/68, matching common conventions) so
`05/16/99` → 1999, not 0099. Backward-compatible via an opt-in parameter, with the
eventual default flipped in 2.0.

### 7.3 Relative date parsing (optional, opt-in)

"yesterday", "2 days ago", "today" are extremely common in scraped HTML and are
explicitly listed as a *limitation* in the README. A small, locale-aware relative
module (gated behind `DateParser(relative=True)` or a separate function) would close
the biggest feature gap vs. `dateparser`, the very library qddate is positioned
against.

### 7.4 Typed result object

`match()` returns `{"values": ParseResults, "pattern": dict}`, which is awkward
(`values` must be iterated and `int()`-ed by hand). A small dataclass:
```python
@dataclass
class DateMatch:
    datetime: datetime.datetime
    pattern_key: str
    language: str
    format: str
    raw: str
```
improves ergonomics and enables future fields (timezone, confidence) without breaking
callers (keep returning the dict shape too, or add `.to_dict()`).

### 7.5 Bulk / streaming API

The library is built for "millions of strings at scale" but offers only a single-
string `parse()`. A `parse_many(iterable)` that reuses the length/charset caches and
avoids per-call filter setup would multiply throughput with no API cost.

### 7.6 Confidence / ambiguity reporting

When multiple patterns match (e.g. `01/02/2020` is valid as both D/M/Y and M/D/Y),
return *all* candidates ranked by `_calculate_pattern_priority` and let the caller
decide. Currently the first match wins silently; for scraping, surfacing ambiguity is
valuable.

### 7.7 Formatting / round-trip

Expose the `"format"` field that already lives on every pattern as a
`format(date, pattern_key=...)` helper — useful for normalizing scraped dates to a
single canonical representation.

---

## 8. Documentation & DX (P3)

- Fix README stats (§4.10) and add a "pattern coverage" table per language.
- Document the filtering pipeline (the 6 levels) — currently only discoverable by
  reading `qdparser.py`.
- Add a CONTRIBUTING section on "how to add a new language" (after §6.1 this becomes
  a 5-minute task).
- Generate API docs from docstrings (Read the Docs is already wired up); many public
  methods lack docstrings or have parameter docs that diverge from signatures.
- Add type hints to the public API (`parse`, `match`, `__init__`); `target-version =
  "py38"` already permits modern annotation syntax.

---

## 9. Prioritized roadmap

Ordered for independent, shippable increments. Each item is a candidate PR.

| # | Item | Priority | Effort | Section |
|---|------|----------|--------|---------|
| 1 | Fix `languages=` + auto-detect intersection (§3.1) | P0 | S | 3.1, 6.1 |
| 2 | Reconcile the 3 "should-be-None" tests (§3.2) | P0 | XS | 3.2 |
| 3 | Fix/delete broken `__main__` block (§3.3) | P0 | XS | 3.3 |
| 4 | Fix `Satuday`/`jule` typos (§4.7) | P0 | XS | 4.7 |
| 5 | Narrow bare `except:`; drop unused `dill` (§4.3) | P1 | XS | 4.3 |
| 6 | Move `dateparser` to optional `bench` extra (§4.5) | P1 | XS | 4.5 |
| 7 | Dedup `BASE_DATE_PATTERNS` keys (§4.6) | P1 | XS | 4.6 |
| 8 | Add `language`/`separator` pattern fields; delete 3× inference (§6.1) | P1 | M | 6.1, 4.1 |
| 9 | Derive `dirty.py` buckets from metadata + coverage test (§4.2) | P1 | M | 4.2, 5 |
| 10 | Clean `.gitignore`, remove committed artifacts (§4.9) | P1 | XS | 4.9 |
| 11 | Update README stats & language list (§4.10) | P1 | XS | 4.10 |
| 12 | Add regression & property tests (§5) | P1 | M | 5 |
| 13 | snake_case `start_session`/`end_session` aliases (§4.8) | P2 | XS | 4.8 |
| 14 | Typed `DateMatch` result object (§7.4) | P2 | S | 7.4 |
| 15 | Timezone-aware returns (§7.1) | P2 | M | 7.1 |
| 16 | 2-digit-year pivot (§7.2) | P2 | S | 7.2 |
| 17 | Centralize month/weekday table helper (§6.2) | P2 | M | 6.2 |
| 18 | `parse_many` bulk API (§7.5) | P3 | S | 7.5 |
| 19 | Ambiguity / multi-match reporting (§7.6) | P3 | M | 7.6 |
| 20 | Relative date parsing (§7.3) | P3 | L | 7.3 |
| 21 | Single compiled matcher refactor (§6.3) | P3 | L | 6.3 |
| 22 | Docs/DX pass + type hints (§8) | P3 | M | 8 |

**Suggested milestone grouping**

- **v1.0.11 — "Stabilize"**: items 1–7 + 10–11. All P0/P1 correctness & hygiene, no
  API change. Restores green tests and honest docs.
- **v1.1.0 — "Refactor"**: items 8–9, 12–13. Internal cleanup behind the existing
  API; sets up feature work.
- **v1.2.0 — "Capabilities"**: items 14–17. Timezone, pivot year, typed results.
- **v2.0.0 — "Scale & coverage"**: items 18–21 + relative dates; flip the 2-digit-
  year default; consider the single-matcher rewrite.

---

## 10. Quick wins doable in a single sitting

If only a few hours are available, these give the most benefit per minute:

1. Items 2, 3, 4, 5, 6, 7, 10, 11 (all XS) — green tests, honest deps & docs.
2. Item 1 (the `languages=` fix) — the only currently-shipped broken feature.
3. Add the `language` field to pattern dicts (start of item 8) even before deleting
   the old inference — it immediately makes item 1 robust.
