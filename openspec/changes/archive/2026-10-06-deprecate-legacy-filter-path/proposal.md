# Deprecate `use_fingerprint=False` legacy filter path

## What Changes

- `DateParser(use_fingerprint=False)` emits a `DeprecationWarning`. The
  legacy 6-level filter stays reachable for one release cycle and is
  removed in `v2.0.0`.
- The docstring on `use_fingerprint` gains a `.. deprecated::` directive
  pointing to `v2.0.0`.
- `tests/test_fingerprint_parity.py` wraps the legacy fixture in
  `pytest.warns(DeprecationWarning)` so the new warning is expected.
- `CHANGELOG.md`, `IMPROVEMENT_PLAN.md`, and
  `docs/docs/development/deprecation-policy.md` are updated.
- Bump to `v1.0.15`.

## Why

The legacy 6-level filter (``_filter_patterns_hierarchical``) was the
default match path through ``v1.0.13``. ``v1.0.14`` flipped the default to
the fingerprint-based path (``use_fingerprint=True``) after 165
exact-equality parity tests passed on the extended probe corpus. With the
default flipped, the only consumer of the legacy path is the explicit
``DateParser(use_fingerprint=False)`` opt-in (used by the parity test
itself and by anyone debugging the matcher).

This change marks ``use_fingerprint=False`` **deprecated** with a
``DeprecationWarning`` and plans its removal in ``v2.0.0``. The
fingerprint path becomes the only supported code path; the legacy path
stays reachable for one release cycle so the warning has time to surface
in downstream code.

## Scope

**In scope (this change):**
- ``DateParser.__init__`` parameter ``use_fingerprint``: emit
  ``DeprecationWarning`` when the caller passes ``False``. Passing
  ``True`` (or omitting the argument) is silent.
- Update docstring to mark the parameter deprecated and to point to
  ``v2.0.0`` as the removal milestone.
- ``tests/test_fingerprint_parity.py`` flips its legacy fixture to use
  ``pytest.warns(DeprecationWarning)`` so the deprecation warning is
  expected.
- ``CHANGELOG.md`` ``## 1.0.15 (date)`` section describing the
  deprecation.
- ``IMPROVEMENT_PLAN.md`` §6.3 marks the removal-planned state.

**Out of scope (future change, v2.0.0):**
- Removing ``_filter_patterns_hierarchical`` and the ``use_fingerprint``
  parameter entirely. After this change the legacy path is reachable
  but warns; after v2.0 it is gone.
- Switching the default ``pivot_year`` to a non-``None`` value (the
  long-standing 2.0 milestone in the plan). That's a separate,
  user-facing change.

## Acceptance criteria

- ``pytest tests/ --cov=qddate --cov-fail-under=85 -q``: all tests pass.
- ``python -W error::DeprecationWarning -m pytest tests/test_fingerprint_parity.py``:
  the parity test passes with the explicit ``DeprecationWarning``
  expectation.
- ``ruff check qddate tests scripts openspec``: clean.
- ``mypy qddate/__init__.py qddate/qdparser.py``: clean.
- Bump ``qddate.__version__`` and ``pyproject.toml`` version to
  ``1.0.15``.
- ``CHANGELOG.md`` ``## 1.0.15`` section present.

## Rollback plan

One-line revert of the ``warnings.warn(...)`` call. The fingerprint path
stays the default; nothing else changes.