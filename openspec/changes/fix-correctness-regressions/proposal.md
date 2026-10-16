# OpenSpec Change: Fix correctness regressions

Restore a green test suite and fix the shipped-but-broken `languages=` behavior. This
is the P0 slice from `IMPROVEMENT_PLAN.md` §3 (items 1–4).

## Why

`pytest` currently exits non-zero on `master` (4 failed, 128 passed). One failure is
a real functional regression shipped in 1.0.6; the others are tests that drifted out
of sync with grammar additions. There is also a typo that silently breaks full-weekday
matching, and a `__main__` block that crashes on first use. None of these are caught
by CI gating today.

## What changes

**Languages filter honors the allow-list (functional regression)**
- From: When `languages=` is set, automatic language detection can still narrow the
  candidate set to a single detected language and discard patterns of a language the
  user explicitly requested. Concretely, `DateParser(languages=["en","de"]).parse("28. Juli 2015")` returns `None`.
- To: When `languages=` is set, the detected-language narrowing SHALL intersect its
  result with the user's allow-list and SHALL never narrow below the allow-list.
  `28. Juli 2015` parses to `2015-07-28`.
- Reason: The current behavior directly contradicts the documented purpose of
  `languages=`. Root cause: "Juli" is shared between German and Dutch and Dutch is
  checked first, so detection returns `['nl']`, which then drops all German patterns.
- Impact: Non-breaking (bug fix). Adds cases that previously returned `None`.

**Reconcile drifted "should-be-None" tests**
- From: Three inputs are asserted to return `None`: `14th April 2015:`,
  `15. Jul 2023`, `5. jan 2020`.
- To: These inputs are accepted as valid and asserted with their expected
  `datetime` values, because the German short-month and English ordinal patterns
  added in 1.0.7 intentionally match them.
- Reason: The grammar is correct; the tests were written before the patterns existed.
  Suppressing the matches would remove useful, intentionally-added coverage.
- Impact: Non-breaking. Test-only change.

**Fix full-weekday typo**
- From: `ENG_WEEKDAYS` contains `"Satuday"`, so `"Saturday"` never matches as a full
  weekday.
- To: The table contains `"Saturday"`, so `Saturday <day> <month> <year>` matches.
- Reason: Current spelling is a bug; no user intends "Satuday".
- Impact: Non-breaking (adds matches, fixes a latent parsing failure).

**Remove broken `__main__` block**
- From: `qdparser.py`'s `if __name__ == "__main__"` block references `r` before
  assignment and imports `dateparser` without a guard, raising `NameError`/
  `ImportError` on first run.
- To: The block is either rewritten to use the `parse()` path with no unguarded
  imports, or deleted entirely (the test suite is the canonical runner).
- Reason: A stale, broken demo misleads contributors and cannot serve as a smoke test.
- Impact: Non-breaking. Developer-facing only.

## Impact

- **Breaking?** No. All changes are bug fixes or test reconciliation.
- **Affected:** Users of `languages=` (gain correct behavior); contributors (green
  tests, runnable module).
- **Rollback:** Trivial — revert the commit.

## Open questions

None. Decisions are made above; alternatives are noted in the relevant tasks.
