# OpenSpec Change: Migrate pyparsing 3 legacy API names

Pattern files call `setResultsName(...)` 127 times across 14 modules. Pyparsing
3 deprecated the camelCase alias in favour of the snake_case `set_results_name(...)`.
This change migrates every call site in one pass to remove the deprecation
warning and make the codebase ready for pyparsing 4.

## Why

`pyparsing` 3.0 deprecated `setResultsName` and `oneOf`, providing
`set_results_name` and `one_of` as snake_case alternatives. Pyparsing 3 emits
a `DeprecationWarning` for the legacy names. Pyparsing 4 (planned) will
remove the legacy aliases entirely.

`qddate` is one of the few libraries still using the camelCase form
consistently — every pattern file imports from `pyparsing` and the codebase
has 127 call sites. Migrating in one pass keeps the codebase clean and
ready for the next pyparsing release.

## What changes

**Replace `setResultsName` with `set_results_name` everywhere**
- From: `Word(nums).setResultsName("year")`.
- To: `Word(nums).set_results_name("year")`.
- Reason: Future-proof; silences deprecation warning.
- Impact: Behaviour identical.

**Replace `oneOf` with `one_of` everywhere**
- From: `oneOf(["a", "b", "c"])`.
- To: `one_of(["a", "b", "c"])`.
- Reason: Same.
- Impact: Already snake_case in most places; migrate stragglers.

**Replace `setParseAction` with `set_parse_action`**
- From: `pat.setParseAction(fn)`.
- To: `pat.set_parse_action(fn)`.
- Reason: Same.
- Impact: Identical behaviour.

**Replace `suppress` (still snake_case) and `parseOnlyAs` etc.**
- Audit-only: most are already snake_case in this codebase.
- Impact: No change expected.

## Out of scope

- Rewriting patterns to use pyparsing's regex helpers (different shape; a
  separate proposal).
- Upgrading the minimum supported pyparsing from 3.1.

## Impact

- **Breaking?** No — pure rename; semantics identical.
- **Affected:** All `qddate/patterns/*.py` files.
- **Risk:** A wrong migration breaks every pattern in that file. Mitigation:
  run the full test suite after each batch; the 247-test suite covers every
  language.
- **Rollback:** Trivial revert.