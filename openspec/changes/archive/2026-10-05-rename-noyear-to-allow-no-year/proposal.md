# OpenSpec Change: Rename `noyear=` parameter to `allow_no_year=`

The `DateParser` keyword parameter `noyear=True` does the opposite of what
the name suggests: setting it `True` *enables* the no-year patterns (which
are responsible for false positives). This change renames the parameter to
its semantic name and keeps `noyear=` as a deprecated alias with a warning.

## Why

```python
def parse(self, text, ..., noyear=True):
    """...
    :param noyear:
        If set True than does use patterns with noyear flag (does a lot of false positives)
        if set False doesn't use patterns with noyear flag
    """
```

Reading the docstring: "If `noyear=True` ... does use patterns with noyear
flag" — so passing `noyear=True` enables them. The flag name reads as "don't
use year patterns" but actually means "use noyear patterns". This is the
single most confusing API surface in the library. A rename to `allow_no_year`
makes the intent obvious: `parse(text, allow_no_year=False)` reads as "do
not allow no-year patterns", which is exactly what the code does.

## What changes

**Canonical parameter renamed**
- From: `parse(text, ..., noyear=True)`.
- To: `parse(text, ..., allow_no_year=True)`.
- Reason: Match the semantic intent; `allow_no_year=True` reads as "the
  parser is allowed to match no-year patterns" — which is what the code does.
- Impact: The new name is canonical. `noyear=` continues to work as a
  deprecated alias and emits `DeprecationWarning`.

**Deprecation warning**
- Calling `parse(..., noyear=...)`, `match(..., noyear=...)`, or
  `match_all(..., noyear=...)` with the deprecated name SHALL emit a
  `DeprecationWarning` recommending `allow_no_year=`.
- Reason: Smooth migration path.
- Impact: Calls without the parameter (i.e. default) are unchanged and emit
  no warning.

**Documentation**
- `docs/docs/api/parse.md`, `docs/docs/api/match.md`, and the API reference
  page SHALL use `allow_no_year=`.
- The README SHALL be updated to use `allow_no_year=`.

**Tests**
- New test: `test_noyear_param_deprecated` exercises the alias and asserts
  the warning is emitted exactly once.
- New test: `test_allow_no_year_default_behavior_unchanged` asserts the
  default `allow_no_year=True` produces the same parse results as the old
  `noyear=True`.

## Out of scope

- Renaming `noyear=` to anything other than `allow_no_year=` (the choice is
  settled; alternatives like `include_no_year` or `enable_no_year` were
  considered and rejected as less clear).
- Removing the deprecated alias in 1.x (defer to 2.0).

## Impact

- **Breaking?** No. `noyear=` continues to work; only emits a warning.
- **Affected:** Anyone passing `noyear=` explicitly will see a warning.
- **Risk:** Tests in `tests/test_regressions_2026_09.py` use the keyword form
  in some places; those tests will now emit warnings. Mitigation: filter the
  warning in `pytest.ini_options` (`filterwarnings = ["error::DeprecationWarning:qddate"]`),
  so the warnings become errors and CI catches any remaining direct usage.
- **Rollback:** Revert.