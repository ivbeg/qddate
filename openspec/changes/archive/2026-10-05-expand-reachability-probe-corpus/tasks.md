# Tasks: Expand reachability probe corpus

## Probe corpus coverage

For each of the ~75 currently-failing basekeys, identify an input string that
the parser will match with *that exact* basekey as the winner (highest-priority
among matching patterns), then add it to `_PROBE_STRINGS` in
`tests/test_regressions_2026_09.py`.

- [ ] Italian patterns: `it_base`, `it_base_lc`, `it_base_article`,
      `it_base_lc_article`, `it_rare_1`, `it_rare_2`, `it_short`,
      `it_short_lc`, `it_short_monthfirst`, `it_short_lc_monthfirst`,
      `it_weekday`, `it_weekday_lc`.
- [ ] Spanish patterns: `es_base`, `es_base_lc`, `es_short`, `es_short_lc`,
      `es_short_monthfirst`, `es_short_lc_monthfirst`, `es_weekday`,
      `es_weekday_lc`, `es_rare_1`, `es_rare_2`.
- [ ] French patterns: `fr_base`, `fr_base_lc`, `fr_short`, `fr_short_lc`,
      `fr_short_monthfirst`, `fr_short_lc_monthfirst`, `fr_weekday`,
      `fr_weekday_lc`.
- [ ] Portuguese patterns: `pt_base`, `pt_base_lc`, `pt_short`, `pt_short_lc`,
      `pt_short_monthfirst`, `pt_short_lc_monthfirst`, `pt_weekday`,
      `pt_weekday_lc`, `pt_weekday_short`, `pt_weekday_short_lc`.
- [ ] German patterns: `de_base`, `de_base_lc`, `de_short`, `de_short_lc`,
      `de_rare_1`, `de_rare_2`, `de_weekday`, `de_weekday_lc`.
- [ ] Dutch patterns: `nl_rare_1`, `nl_rare_2`, `nl_short`, `nl_short_lc`,
      `nl_weekday_lc`.
- [ ] Polish patterns: `pl_base`, `pl_base_lc`.
- [ ] Czech pattern: `cz_base_lc`.
- [ ] Romanian patterns: `ro_base`, `ro_base_lc`, `ro_short`, `ro_short_lc`.
- [ ] Ukrainian patterns: `uk_base`, `uk_base_lc`, `uk_gen`, `uk_gen_lc`,
      `uk_short`, `uk_short_lc`.
- [ ] Russian: `date_rus3`, `rus_rare_2`.
- [ ] English: `date_eng1_lc`, `date_eng1x`, `date_eng2_lc`, `date_eng3`,
      `date_eng_abbrev1`, `weekday_eng_abbrev1`, `weekday_eng_lc`,
      `weekday_eng_iso`.
- [ ] Numeric: `date_8`.

## Documentation

- [ ] Add an inline `# basekey=<key>` comment next to each new probe in
      `_PROBE_STRINGS`, indicating which base pattern it is intended to win.
- [ ] Update the `known_shadowed` block comment to describe the strategy if
      the list ever needs entries (it should not).

## Verification

- [ ] `pytest tests/test_regressions_2026_09.py::test_every_pattern_matches_some_probe`
      passes.
- [ ] `pytest tests/` still passes 100%.
- [ ] `pytest tests/test_regressions_2026_09.py::test_probe_corpus_all_parse`
      still passes (every probe string must produce a non-None parse result).
- [ ] `pytest tests/test_regressions_2026_09.py::test_every_pattern_key_in_some_prefix_bucket`
      still passes (bucket coverage unchanged).