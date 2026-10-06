# OpenSpec Change: Expand reachability probe corpus

The reachability oracle test (`test_every_pattern_matches_some_probe`) currently
fails on master with ~75 shadowed basekeys flagged as "never win any probe". This
change extends the probe corpus so every base pattern is the winning match for at
least one input string, turning the oracle from advisory into an effective
regression net.

## Why

`tests/test_regressions_2026_09.py::test_every_pattern_matches_some_probe` is the
strongest single regression net in the suite: it asserts that every base pattern
in `ALL_PATTERNS` is the *winning* match for some input, so dead or shadowed
patterns are caught immediately. But the probe corpus was bootstrapped from the
existing parametrize tables in `test_dateparser.py`, which only exercise
high-priority patterns. Many lower-priority equivalents (`it_base_lc`,
`fr_base_lc_article`, `de_short_lc`, `ro_short`, `uk_gen`, etc.) are shadowed in
practice and never win.

The test ships broken in master. Anyone reading CI output sees `1 failed` and
the failure is the regression net itself — that defeats the purpose. Either we
make the corpus rich enough that every basekey wins something, or the assertion
becomes aspirational.

## What changes

**Probe corpus expansion**
- From: 70 probe strings; ~75 basekeys never win; the oracle test fails.
- To: A probe corpus covering every base pattern, including the lower-priority
  variants. Every basekey in `ALL_PATTERNS` wins at least one probe; the oracle
  test passes.
- Reason: The oracle test is the safety net that catches future dead-pattern
  bugs (the same class as 4.4 in `IMPROVEMENT_PLAN.md`); it must be reliable.
- Impact: Non-breaking. Test-only.

**Knowledge-capture comment for each new probe**
- From: The existing comment "Patterns known to be shadowed by higher-priority
  equivalents" leaves `known_shadowed` empty.
- To: Each new probe string carries a one-line `# basekey=X` comment mapping it
  to the base pattern it is designed to exercise, so future readers understand
  the probe.
- Reason: Make probe coverage reviewable instead of mysterious.
- Impact: Non-breaking. Documentation only.

## Impact

- **Breaking?** No. Test-only change; externally observable behavior is
  unchanged.
- **Affected:** Contributors adding patterns (will know which probes exercise
  their additions); CI (passes).
- **Risk:** A future bug could let a previously-shadowing pattern lose and
  silently cause a probe to fail for a different basekey. The oracle test will
  catch this with a clear "patterns never win" diff.
- **Rollback:** Revert the commit; the test will revert to its previous state.