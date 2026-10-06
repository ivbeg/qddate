# Flip `use_fingerprint` default to True

## Why

The fingerprint-based matcher shipped across two prior rounds (data layer
in `fingerprint-based-matcher`, consumer wiring in `wire-fingerprint-filter`).
Both rounds kept the new path **opt-in** (`use_fingerprint=False` default)
because the parity test only asserted `fingerprint ⊇ legacy` — i.e. the
fingerprint path produces a *superset* of the legacy candidate set, but
might also include extra candidates that the legacy path would have
filtered.

This change flips the default and tightens the parity test to **exact
equivalence**: ``fingerprint == legacy`` on every probe string. Any
divergence is investigated, fixed, and the test is re-run until clean.

## Scope

**In scope (this change):**
- `DateParser.__init__`: change ``use_fingerprint: bool = False`` → ``use_fingerprint: bool = True``.
- `tests/test_fingerprint_parity.py`: change every ``assert superset`` into
  ``assert equal``. Add the larger probe corpus from
  ``tests/test_regressions_2026_09.py::_PROBE_STRINGS`` so the equality
  check covers every reachable input.
- Investigate and close any failure paths the equality check exposes.
- Bump version to **1.0.14** in ``qddate/__init__.py`` and ``pyproject.toml``.
- Update ``IMPROVEMENT_PLAN.md`` §6.3 marking item #19 as shipped.
- Add a ``CHANGELOG.md`` entry under ``## 1.0.14`` summarizing the
  default flip + parity equivalence.

**Out of scope (future round):**
- Removing the legacy ``_filter_patterns_hierarchical`` pipeline entirely.
  After this round the legacy path still works via ``use_fingerprint=False``
  as a belt-and-braces fallback; deleting it is a separate change that
  requires running the legacy path against the next major release cycle.
- Adding benchmark comparisons (the existing ``tests/test_performance_smoke.py``
  is unchanged; we don't add a benchmark for the fingerprint path in this
  round).

## Acceptance criteria

- ``pytest tests/ --cov=qddate --cov-fail-under=85 -q``: all 438+ tests
  pass with the new default (``use_fingerprint=True``).
- ``pytest tests/test_fingerprint_parity.py -v``: equality assertion holds
  for every probe string in the extended corpus.
- ``ruff check qddate tests scripts openspec``: clean.
- ``mypy qddate/__init__.py qddate/qdparser.py``: clean.
- Coverage of the new default path is at least 90%.

## Rollback plan

If exact equivalence fails on a non-trivial case, the simplest rollback is
to revert the default flag to ``False`` (one-line change) and ship a
follow-up change that fixes the divergence. The legacy pipeline keeps
working unchanged through the entire round.