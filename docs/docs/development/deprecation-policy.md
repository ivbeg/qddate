---
title: "Deprecation policy"
description: "How qddate handles API deprecations, and the schedule for removing deprecated names."
---

# Deprecation policy

`qddate` follows a **two-releases-before-removal** deprecation schedule for
any public API change that is not strictly additive.

## Process

When a public name is renamed or its semantics change:

1. The new canonical name is added immediately; the old name continues to
   work and emits `DeprecationWarning` (Python's standard warning class).
2. The old name stays for at least one minor release (e.g. 1.0.x → 1.1.x).
   After at least two minor releases it may be removed in a major release
   (2.0.x). The `CHANGELOG.md` entry for the major release will list every
   removal.
3. The deprecation warning message names the canonical replacement. CI
   runs with `-W error::DeprecationWarning` for the `qddate` module so
   new regressions are caught at PR time.

## Active deprecations (as of 1.0.15)

### `noyear=` → `allow_no_year=`

The old name did the opposite of what the name suggested: passing
`noyear=True` *enabled* the no-year patterns (which cause many false
positives). It is now `allow_no_year=`.

```python
# from
parser.parse("5.12", noyear=False)        # None (deprecated)
# ↓
parser.parse("5.12", allow_no_year=False) # None (canonical)
```

Removal target: **2.0**.

### `startSession()` / `endSession()` → snake_case

The camelCase session-control methods were replaced with snake_case
equivalents in 1.0.11.

```python
# from
parser.startSession(["dt:date:date_1"])   # deprecated
parser.endSession()
# ↓
parser.start_session(["dt:date:date_1"])
parser.end_session()
```

Removal target: **2.0**.

### `use_fingerprint=False` → omit the parameter

The legacy 6-level filter (`_filter_patterns_hierarchical`) was
superseded by the fingerprint-based matcher (`_filter_patterns_fingerprint`)
in `1.0.14`. The fingerprint path is the default and is exactly equivalent
on the extended probe corpus. Passing `False` is deprecated and emits
a `DeprecationWarning`.

```python
# from
DateParser(use_fingerprint=False)   # DeprecationWarning
# ↓
DateParser()                         # canonical; uses fingerprint path
```

Removal target: **2.0**.

## For contributors

If you're adding a new feature that obsoletes an existing API:

- Land the new API first (additive change).
- Update the old API to delegate to the new one and emit
  `DeprecationWarning(stacklevel=2)`.
- Update the relevant `tests/` to assert both code paths work and that the
  warning is emitted.
- Add the deprecation to this page and `CHANGELOG.md`.
- Tag the removal version in the deprecation message
  (`"...removed in 2.0"`).

## For downstream consumers

If you see a `DeprecationWarning` from `qddate`:

- The message names the canonical replacement.
- The old API will work until the next major bump (2.0).
- Run `python -W error::DeprecationWarning` in CI to catch new warnings.

## Past deprecations

- `dateparser` runtime dependency — moved to the `[bench]` optional extra
  (1.0.x).
- `dill` import — removed from `dirty.py` (1.0.x).
- `__version__` in `qddate/patterns/__init__.py` — removed (canonical
  location is `qddate.__version__`).