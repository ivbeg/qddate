# Tasks

## 1. Extend parity corpus

- [ ] Pull ``_PROBE_STRINGS`` from ``tests/test_regressions_2026_09.py`` into the parity test
- [ ] Change every ``assert superset`` to ``assert equal`` in ``tests/test_fingerprint_parity.py``
- [ ] Add an exact-equality helper that compares pattern-key sets

## 2. Run parity + investigate divergences

- [ ] ``pytest tests/test_fingerprint_parity.py -v`` — capture every divergence
- [ ] For each divergence, identify whether the fingerprint path includes an extra pattern or excludes a legacy pattern
- [ ] Close the divergences in the fingerprint path (NOT by re-introducing extras in the legacy path)

## 3. Flip the default

- [ ] Change ``DateParser.__init__`` default: ``use_fingerprint: bool = False`` → ``use_fingerprint: bool = True``
- [ ] Update docstring on the parameter
- [ ] Verify the legacy pipeline still runs correctly when ``use_fingerprint=False`` (regression net)

## 4. Tests + benchmarks

- [ ] Existing 438 tests pass with the new default
- [ ] Performance smoke test still passes (no regression in pipeline throughput)

## 5. Documentation + changelog

- [ ] ``IMPROVEMENT_PLAN.md`` §6.3: mark item #19 as shipped; update §3a status
- [ ] ``CHANGELOG.md``: add ``## 1.0.14 (date)`` section
- [ ] ``qddate/__init__.py``: bump ``__version__`` to ``1.0.14``
- [ ] ``pyproject.toml``: bump ``version`` to ``1.0.14``
- [ ] Update ``docs/docs/development/deprecation-policy.md`` ("as of 1.0.14")

## 6. Verification

- [ ] ``pytest tests/ --cov=qddate --cov-fail-under=85 -q``: all pass
- [ ] ``ruff check qddate tests scripts openspec``: clean
- [ ] ``mypy qddate/__init__.py qddate/qdparser.py``: clean
- [ ] ``python -c "import qddate; print(qddate.__version__)"`` → ``1.0.14``

## 7. Archive

- [ ] ``openspec validate flip-fingerprint-default``
- [ ] ``openspec archive flip-fingerprint-default -y``