# Changelog

All notable changes to this project are tracked here.

## Unreleased

**Time formats** (Q5–Q8 of `dev/docs/IMPROVEMENT_PLAN_2026-10-21.md`)
- The 12-hour clock after a date: `AM`/`PM`, `am`/`pm`, `a.m.`/`p.m.`,
  with or without minutes and seconds (`May 5, 2022 at 3:45 PM` → 15:45,
  `May 5, 2022 at 3 p.m.` → 15:00, `12:00 AM` → 00:00). Before, the time was
  lost and `parse()` gave midnight. The generated `:time_4` variants read it;
  `match()` stores the hour as a 24-hour number and adds no `ampm` key, so
  callers that `int()` every value keep working. An hour above 12 is not a
  12-hour time, and a word that starts with `am`/`pm` is not a marker.
- The time before the date, followed by `,`, `|`, `-` or a space:
  `12:30, 5 мая 2022`, `12:30 05.05.2022`, `14:30 | 5 May 2022`,
  `3:45 PM, May 5, 2022` (all returned `None`). The generated `:time_left`
  variants accept every clock form below and a zone.
- Zones after the time: `+03:00`, `Z`, `GMT`/`UTC` alone or with an offset
  (`GMT+3`, `UTC-05:30`, `GMT+0300`) and the abbreviations in
  `qddate.patterns.TIMEZONE_ABBREVIATIONS` (`MSK`/`МСК`/`мск`, `CET`/`CEST`,
  `MEZ`/`MESZ`, `EET`/`EEST`, `WET`/`WEST`, `BST`, `EST`/`EDT`, `CST`/`CDT`,
  `MST`/`MDT`, `PST`/`PDT`, `JST`, `AEST`, …). Before, only `+HHMM` after
  `HH:MM:SS` was read: `2022-05-05T10:00:00+03:00` gave a naive 10:00 even
  with `tz_aware=True`. The zone is kept as written in the `timezone` value;
  the new `qddate.qdparser.parse_timezone()` turns it into a
  `datetime.timezone` (named for an abbreviation). `HH:MM` now takes a zone
  too. Latin abbreviations are matched in capitals only (the French `est`
  after a time stays a word); ambiguous ones such as `IST` are not listed.
- `14h30` and `14 h 30` (French, Portuguese) after a date: `05/05/2022 14h30`,
  `le 5 mai 2022 à 14h30` → 14:30 (00:00 before). Minutes are required, so
  `3 h de route` is not read as a time.
- A word between the date and the time in more languages: `at` (en), `à`
  (fr), `um` (de), `a las` (es), `alle` (it), `om` (nl), `às` (pt), as `в`
  already was in Russian. Numeric dates belong to no language and accept all
  of them (`05.05.2022 в 12:30`, `05/05/2022 at 3:45 PM`); a month-name date
  only its own (`16 May 2009 в 14:10` still drops the time).
- `HH:MM` after a date may follow `|` or the ISO `T`, as `HH:MM:SS` could:
  `21 September 1994 | 11:08`, `2022-05-05T10:00` keep their time.

**API** (Q14–Q17)
- `languages=` on `match()`, `match_all()`, `parse()`, `match_typed()` (and
  `parse_many()`): the patterns of these languages and the language-neutral
  numeric ones are tried first, the others only when none of them matches.
  Unlike the constructor's `languages=` it excludes nothing, so one parser
  serves pages in every language. The candidate index for each set of
  languages is built on first use and kept; the parser is not rebuilt.
  `match_all()` lists the hinted languages' matches first.
- `date_order="DMY" | "MDY" | "YMD"` in the constructor and per call. Among
  patterns that consume the same text, those of that order win:
  `parse("05/06/2022", date_order="MDY")` is 6 May (`date_usa`), while
  `13/05/2022` stays 13 May. Dotted and dashed dates have no month-first
  pattern and stay day first. `None` keeps today's preference.
- `reference=` (the moment that counts as "now") and `prefer="past" |
  "future"` on `parse()` and `match_typed()` for dates without a year. The
  year comes from `reference` instead of the clock; `prefer="past"` moves a
  date more than `NOYEAR_ROLLOVER_GRACE` (2 days) after the reference to the
  previous year (`31.12` read on 2 January), as newsworker's own rule does.
- `DateMatch` gains `span` (where the date ends in `raw`, in characters of the
  original text even with tabs), `precision` (`"day"`, `"hour"` for `3 PM`,
  `"minute"`, `"second"`), `tzinfo` (the written zone, set without
  `tz_aware=True` too) and `has_year`. `to_dict()` includes them; the old
  five-argument constructor still works.

**Benchmark rows that change** (54,565 rows of `benchmarks/test_data.csv` and
`benchmarks/webpage_test_data.csv`, compared with `master` for `match()`,
`parse()` with and without `tz_aware`, `match_all()` with and without
`allow_no_year`, the legacy filter and `DateParser(languages=["en", "ru"])`)
- 48 rows, all because `HH:MM` may now follow `|`: 42 rows of
  `test_data.csv` such as `21 September 1994 | 11:08`
  (`dt:date:date_eng1:t_right` → `dt:date:date_eng1:time_1`) and 6 rows of
  `webpage_test_data.csv` such as `17-12-2025 | 13:40`
  (`dt:date:date_iso8601:t_right` → `dt:date:date_iso8601:time_1`). They now
  keep their time instead of midnight. No other row changes.
- newsworker's test suite (457 tests) and 232-page corpus (F1 and
  `date_accuracy` 1.0) give the same results against this branch.

**Performance**
- A default parser has 1,656 generated patterns instead of 1,104 (the
  `:time_4` and `:time_left` variants). The fingerprint walk that selects
  candidates now keeps its result per text fingerprint (length, character
  sets, separators, detected language, year format), so the larger catalog
  costs little: on an Apple M-series machine the 54,565 benchmark rows take
  7.5 s instead of 8.3 s on `master`; text without a date 0.32 ms per call
  instead of 0.43 ms, and the `tests/test_performance_smoke.py` dates
  0.27 ms instead of 0.25 ms. A `:time_4` variant needs an AM/PM marker in
  the text, so the pre-grammar checks skip it on other text.
- `match()` / `match_all()` / `parse()` parse each candidate grammar at the
  start of the text only. They used `scan_string`, which tried every later
  position of a text that does not start with a date, and then discarded the
  match because it did not start at position 0.
- Before running a grammar, the parser checks two facts read from it once:
  the characters its match can start with, and the month or weekday names it
  requires. A candidate the text cannot satisfy is skipped. Text without a
  date (`Comments (12)`, `Price: 1 200 руб.`) used to run up to 745 grammars
  and now usually runs none. The checks only skip grammars that cannot
  match.
- Measured on an Apple M-series machine against `1.0.17`: `match()` on text
  without a date drops from 5–50 ms to 0.1–0.7 ms, on dates by about 4×. On
  `benchmarks/test_data.csv` and `benchmarks/webpage_test_data.csv` (54,565
  rows) a full comparison takes 3.5 s instead of 52 s per shard. No row
  changes its `match()`, `parse()` or `match_all()` result, with any filter
  flag, on the legacy filter, with `languages=` or in a session.
  newsworker's 232-page extraction corpus runs in 1.3 s instead of 21.2 s.

**Fixes**
- `match()` and `parse()` no longer raise `IndexError` on a text with a tab
  after the date's first character (`5\tMay 2022`, `01.12.2009\t10:20`).
  pyparsing matches the text with tabs expanded, and the match end was used
  as an index into the original text.
- Disabling a filter on the default (fingerprint) parser widens the
  candidate set again, as it does on the legacy path. Since `1.0.14`,
  `nocharsetfilter=True` made every parse return `None`, and
  `noseparatorfilter=True` dropped every pattern with a concrete separator
  (`DateParser().parse("01.12.2009", nocharsetfilter=True)` returned
  `None`). Each toggle now skips its dimension; `noprefix=True` also skips
  the character-set filter, as in the legacy pipeline.
- `tests/test_fingerprint_parity.py` checks the fingerprint path against
  the legacy path under the filter toggles: the fingerprint filter keeps
  every legacy candidate under all 64 combinations, and `match_all()` /
  `parse()` agree with each toggle flipped alone and with all flipped.
- The default parser honours `start_session()`. Since 1.0.14 the default
  fingerprint filter ignored the session's pattern list, so a session
  neither restricted matching nor sped it up:
  `start_session(['dt:date:date_eng1'])` still parsed `01.12.2009`. The
  fingerprint filter now walks an index over the session's patterns only,
  as the legacy filter (`use_fingerprint=False`) does.
- A month name shared by several languages no longer hides the right
  language's patterns. Language detection narrowed to the first language
  claiming the name, so `Montag, 18 Juni 1953` (German, detected as Dutch),
  `30. Mai 1953` (detected as French) and `11 Август 2009` (Bulgarian,
  detected as Russian) did not parse. A weekday name now picks the language
  when the month name is shared, and when the first language's patterns
  find nothing the parser tries every language. Dates that parsed before
  keep their pattern.
- Russian `dt:date:weekday_rus` / `weekday_rus_lc1` now return a date:
  they captured no day or month, so `parse()` returned `None` even when they
  matched. Their length limit was below any input with the required
  `года`/`г.` (`Понедельник, 25 Сентября 1979 года`); it is now 35.
- Sunday is spelled `Воскресенье`; the old `Воскресение` still matches.
- Short inputs rejected by length limits now parse: `9 Мая 1998`
  (`date_rus`), `1.мая.1945` (`rus_rare_3`), `Май 6, 2020` (`rus_rare_5`),
  `7 Юли 1918` (`bg_base`, `bg_base_lc`) and `9 Maj 1997` (`pl_base`,
  `pl_base_lc`).
- `17/апреля/1908` parses: `dt:date:date_rus_lc1` accepts slashes, but its
  metadata said space-separated, so the separator filter dropped it.
- Russian dates without a year parse. `dt:date:date_rus` had an optional
  year but no `noyear` flag, so `4 Сентября в 04:06:33` matched with a day
  and month only and `parse()` returned `None` (`4 сентября в 04:06:33`
  matched nothing). The new `dt:date:date_rus_noyear` pattern (capitalised
  or lowercase month) takes the current year like `05.12`, and does not
  match with `allow_no_year=False`. `date_rus` requires the year again.
- The time after a Russian date is kept. `date_rus` also swallowed a
  trailing `HH:MM(:SS)` without naming it, so `4 Сентября 2020 в 04:06:33`
  and `4 Сентября 2020 04:06:33` parsed to midnight. The generated time
  variants of every Russian pattern now accept `в` before the time
  (`2 Января 1981 года в 21:04` → 21:04); other languages do not.
- The default (fingerprint) filter applies the character-set and language
  filters only to texts longer than five characters, as the legacy filter
  and the filter pipeline docs do. On `05.12` it dropped the five-character
  Russian `date_rus_noyear` pattern that the legacy filter keeps; results
  do not change.
- `DateParser(pivot_year=True)` raises `TypeError`. `True` is the integer 1,
  so it mapped only `00` to 2000 and `05` to 1905. `pivot_year` takes a
  4-digit year such as `1968` or `None`; other non-integers (`"1968"`,
  `1968.0`) raise too.
- A date followed by a time keeps the time. `match()` now picks the
  candidate that consumes the most input and uses the priority score only to
  break ties. Before, a pattern matching just the date outranked its time
  variant on the exact-length bonus: `14 Avril 1995 20:16:12` and
  `29 de Agosto de 1925 07:30` parsed as midnight, and
  `9 Июня 1927 15:18:03` / `22 August 2005 08:47:19` lost their seconds.
  On `benchmarks/test_data.csv` 141 rows gain their time. On it and
  `benchmarks/webpage_test_data.csv` no row loses a match or a time, and
  no date changes.
- Length limits narrower than their grammar are widened, so these parse:
  `Mon 1/1/2020` (`weekday_short_eng_iso`), `Sábado 1 Maio 2020`
  (`pt_weekday`, `pt_weekday_lc`). Also widened: `date_eng1_short`,
  `date_eng2_short`, `weekday_eng(_lc)`, `weekday_eng_wshort`,
  `weekday_eng_mshort_wshort`, `de_base(_lc)`, `fr_base(_lc)`,
  `nl_base(_lc)`, `pt_weekday_short(_lc)`, `date_rus2`, `date_rus3`,
  `date_rus_lc2`, `rus_rare_2`, `rus_rare_6`.

**Behaviour changes**
- `:t_right` variants no longer consume the text after the date, and get no
  exact-length bonus (their limits include that text). A clean date now
  matches the plain variant (`25 Jan 1936` gives `dt:date:date_eng1_short`,
  not `...:t_right`). Equal-priority candidates are tried in pattern
  generation order, so both filters pick the same one. With the widened
  limits, the matched pattern key changes on 1,288 rows of
  `benchmarks/test_data.csv` and 9 rows of
  `benchmarks/webpage_test_data.csv` with the same datetime; the base
  pattern now equals the one the generator used on 8,357 of 10,383 rows
  (was 8,120).
- `match_all()` ranks results the way `match()` picks, most input consumed
  first, so its first result is the `match()` result.

**Tests**
- `tests/test_pattern_lengths.py` renders every pattern's grammar and fails
  when a declared length limit rejects a rendered date. Every pattern
  passes it now except `date_5`/`date_6`, whose grammar also accepts
  space-separated digit groups.
- `tests/test_match_prefilter.py` renders every generated grammar (347,476
  distinct texts with the 1.1.0 time variants) and checks that each text it
  matches passes its pre-grammar checks, compares `match_all()` with the
  checks switched off, and asserts that text without a date runs no grammar.
- The renderer in `tests/test_pattern_lengths.py` knows the new grammar
  elements: a `Combine` (a zone such as `GMT+03:00`) renders as one token in
  its shortest and longest form, a character class (`[,|T]`) as its
  characters, a lookahead (no letter after `PM`) as nothing. A sequence whose
  parts combine to more than 512 renderings keeps every rendering of each
  part at least once, plus the shortest and longest texts, instead of the
  full product (a long date times a 12-hour time times a zone).
- `tests/test_pattern_lengths.py` also checks the declared lengths of the
  generated time variants (`:time_1`, `:time_2`, `:time_4`, `:time_left`)
  against their renderings; `:time_1` and `:time_2` limits grew to fit the
  zone, `14 h 30` and the word before the time.
- `tests/test_time_formats.py` (Q5–Q8) and `tests/test_call_options.py`
  (Q14–Q17) cover the new forms and options.
- `tests/test_performance_smoke.py` (`QDDATE_PERF=1`) also bounds the mean
  `match()` latency on text without a date (5 ms; under 1 ms locally).

**Benchmarks**
- `benchmarks/generate_test_data.py` uses a fixed seed and no longer emits
  inputs no pattern accepts (`2 / 7 '36`, Spanish weekday dates with `de`,
  Russian weekday dates without `года`). `benchmarks/test_data.csv` is
  regenerated: 10,383 rows, 9 fail (`19 de May de 2016`: the English month
  `May` narrows detection to English).
- The 81 yearless Russian rows (`4 Сентября в 04:06:33`) are labelled
  `dt:date:date_rus_noyear`.
- `benchmarks/comprehensive_performance_test.py` no longer stops at the batch
  step when `tqdm` is missing (`AttributeError: 'tqdm' object has no attribute
  'set_description'`); the `bench` extra now installs `tqdm`.
- `benchmarks/bench.py` `compare()` no longer fails with `NameError` on
  `DateParser`.

**CI and tooling**
- CI lints `benchmarks/` too, type-checks `qddate` with mypy, and fails when the
  README stats block differs from the pattern table
  (`scripts/generate_readme_stats.py --check`, which now prints the stale and
  the expected block). `mypy` is in the `dev` extra.
- The test suite turns a `DeprecationWarning` raised from qddate's own code
  into an error.
- `make lint` and `tox -e lint` run Ruff; the unused `flake8` config and the
  Sphinx `tox -e docs` environment are removed.

**Specs and docs**
- `openspec/specs/date-parsing` specifies the 12-hour clock, the time before
  the date, `14h30`, the words before the time, zones, `date_order=`,
  `reference=`/`prefer=` and the new `DateMatch` fields;
  `openspec/specs/language-support` the per-call `languages=` hint. The API
  pages (`docs/docs/api/dateparser.md`, `parse.md`, `match.md`,
  `languages.md`, `filter-pipeline.md`) document them.
- The canonical OpenSpec specs match the code: `parse_relative()` keeps the
  reference's time of day and has no `relative=True` switch; `allow_no_year=`
  replaces `noyear=`; time-of-day validation, `pivot_year`, `tz_aware`,
  `match_all()`, `match_typed()`, `parse_many()` and sessions are specified;
  the fingerprint filter is specified as keeping every legacy candidate with
  identical results. The eight shipped changes under `openspec/changes/` are
  archived, with what shipped differently recorded in each `tasks.md`.
- The API docs cover every public method, `DateMatch`, `pivot_year`,
  `tz_aware` and `use_fingerprint`; Python versions read 3.10–3.14; the filter
  pipeline page describes the fingerprint default and the real level order.
- `CHANGELOG.md`: 1.0.12 is listed before 1.0.11, and the stray "Unreleased"
  section that held 1.0.11 changes is merged into 1.0.11.
- The date-parsing spec states that the longest match wins and how
  `match_all()` is ordered; the `match()` and filter pipeline docs say so too.

## 1.0.17 (2026-10-17)

**Patterns**
- A weekday before a month-first date is recognised:
  `Monday, January 31, 2022` (`weekday_eng_us`), `Mon, January 31, 2022`
  (`weekday_eng_wshort_us`) and `Mon, Jan 31, 2022` / `Tue Feb 1, 2022`
  (`weekday_eng_abbrev_wshort_us`). Previously only day-first dates and
  `Monday, Jan 31, 2022` matched after a weekday; EU INSPIRE and many US
  sites print the long form (ivbeg/newsworker#18).

## 1.0.16 (2026-10-16)

First PyPI release since 1.0.10: it also ships the changes listed under
1.0.11–1.0.15 below, which were tagged but not published.

**Compatibility**
- Use pyparsing's snake_case API (`scan_string`, `max_matches`,
  `parse_string`, `as_dict`). pyparsing 3.3 deprecates the camelCase names
  and pyparsing 4 removes them; downstream test suites saw tens of thousands
  of `PyparsingDeprecationWarning`s per run.

**Fixes**
- `HH:MM:SS` timestamps accept signed offsets: `-0500` now produces a
  negative UTC offset with `tz_aware=True` (previously only `+HHMM` was
  recognised). The `timezone` match value now includes its sign
  (`"+0300"`, `"-0500"`).
- An offset separated from the time by a space (`10:55:50 +0530`) no longer
  falls back to the `HH:MM` variant and drops the seconds.
- `parse_relative("N months/years ago")` uses calendar months on every
  install. It used `python-dateutil` when present (it is not a dependency)
  and a 30-day approximation otherwise, so results differed between
  environments.
- Timing tests run in their own CI step without coverage tracing and
  measure the best of several runs, so shared-runner noise no longer turns
  the build red. Thresholds are unchanged.
- Wheels are tagged `py3` (the legacy `setup.cfg` marked them `py2.py3`).
- Packaging: the wheel contains only the `qddate` package. Package
  discovery treated every directory as a namespace package, so a build from
  a working copy shipped `docs/` (including `node_modules`), `openspec/` and
  `benchmarks/` (3.8 MB instead of 65 KB). The sdist now carries the
  sources, tests with their fixtures, README, LICENSE and CHANGELOG. A CI job
  builds both and checks their contents.
- Language detection matches month names as whole words. French "mai" no
  longer claims Portuguese "maio", which made every `... de maio de ...` date
  unparseable.

## 1.0.15 (2026-10-06)

**Deprecations**
- `DateParser(use_fingerprint=False)` is **deprecated**. The legacy
  6-level filter (`_filter_patterns_hierarchical`) is superseded by
  the fingerprint-based path that became the default in `1.0.14`.
  Constructing a parser with `use_fingerprint=False` emits a
  `DeprecationWarning`; the legacy path will be **removed in v2.0.0**.
  Omit the parameter (or pass `True`) to silence the warning.

**No user-visible API changes.**

## 1.0.14 (2026-10-06)

**Performance — single-walk fingerprint filter is now the default**
- `DateParser.__init__` accepts `use_fingerprint: bool = True` (default
  flipped from `False` in this release). When `True` (the default),
  `match()` / `match_all()` / `parse()` route through the new
  `_filter_patterns_fingerprint` — a single-walk intersection over the
  precomputed `qddate.patterns.fingerprint._PATTERN_FINGERPRINTS` index
  — instead of the 6-level `_filter_patterns_hierarchical` filter.
- The fingerprint path is **exactly equivalent** to the legacy path on
  the extended probe corpus (165 strings covering every shipped
  language, every separator, every year-format bucket, weekday + short +
  compact + edge cases). The equivalence is locked by
  `tests/test_fingerprint_parity.py`.
- Three pipeline simplifications fall out of the new path:
  1. Length filter is implicit (the index doesn't contain patterns
     with a mismatched length range at all).
  2. Charset filter is a single index walk over `<= text_char_sets`
     buckets (vs. a per-pattern loop).
  3. Separator, language, and year-format filters collapse into one
     per-dimension intersection.
- Set `DateParser(use_fingerprint=False)` to opt back into the legacy
  6-level filter; useful when debugging the matcher itself.

**No user-visible API changes.**

## 1.0.13 (2026-10-05)

**Internal — single source of truth for month names**
- New `qddate.patterns.months.MONTHS_BY_LANGUAGE` table is the canonical
  source for every supported language's month-name variants (full, lowercase,
  abbreviated, genitive where the language distinguishes case, plus a
  `detect_excludes` allow-list for cross-language collisions like Romanian
  *mai* / *august*).
- `qddate.qdparser._detect_language` now derives its per-language detection
  sets from the same table (intentionally skipping abbreviations to avoid
  false-positive language detection on shared 3-letter forms like *Jan*).
- All 14 per-language pattern modules (`base`, `bg`, `cz`, `de`, `es`, `fr`,
  `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`, `uk`) now source their `*_MONTHS`
  lists and `*_mname2mon` dicts from the table. The legacy constants are
  preserved as re-exports so existing tests and downstream consumers keep
  working unchanged.
- 72 parity tests in `tests/test_months_table.py` lock equivalence: every
  legacy `*_mname2mon` pair (across all variants) is either present in
  `MONTHS_BY_LANGUAGE` or, for the Bulgarian mixed-script legacy forms,
  maps cleanly to a canonical Cyrillic entry.

No user-visible API changes.

## 1.0.12 (2026-10-05)

**New features**
- Added `DateParser.parse_relative(text, reference=None)` that resolves
  common English and Russian relative-date phrases:
  - English: `today`, `yesterday`, `tomorrow`, `N day(s) ago`, `(in) N day(s)`
    (and the same for weeks/months/years); both digit-form and word-form
    numbers (`three days ago`).
  - Russian: `сегодня`, `вчера`, `завтра`, `N <unit> назад`, `через N <unit>`.
  - `reference` defaults to `datetime.now()`; pass an explicit value for
    deterministic tests.
- README pattern counts are now generated by
  `scripts/generate_readme_stats.py` from the canonical pattern table —
  they cannot drift again.

**Quality**
- Migrated pattern files off pyparsing 3 camelCase aliases (`oneOf`) onto
  `one_of`. `python -W error::DeprecationWarning -c "import qddate"` is
  now silent.
- Renamed `noyear=` keyword argument on `parse`/`match`/`match_all` to
  `allow_no_year=` (the old name was the opposite of the semantic
  intent). `noyear=` continues to work as a deprecated alias emitting
  `DeprecationWarning`.

## 1.0.11 (2026-10-05)

**API additions**
- Added `qddate.format_date(dt, pattern_key)` and `DateMatch.format_date()` for
  locale-aware round-trip of a parsed `datetime` back to a string the parser
  accepts again. `DateParser.format_date(dt, pattern_key)` is exposed as an
  instance method.
- Added type hints on the public surface (`DateParser.__init__`, `parse`,
  `match`, `match_all`, `match_typed`, `parse_many`, `start_session`,
  `end_session`, `format_date`; `DateMatch.format_date`, `to_dict`). `mypy
  qddate/__init__.py qddate/qdparser.py` is now clean.

**Internal hardening**
- `qddate.dirty.matchPrefix` prefix-bucket lists are now derived from
  `_PATTERN_METADATA` at import time. Adding a pattern no longer requires
  editing `dirty.py` (closes bug class 4.4 from `IMPROVEMENT_PLAN.md`).
- `qddate.qdparser._DateParser__generate` is now strictly read-only against
  `ALL_PATTERNS`. The `required_chars` stamping was moved into
  `annotate_patterns()` so constructing any number of `DateParser()` instances
  leaves `ALL_PATTERNS` byte-identical (new `tests/test_pattern_immutability.py`
  regression net).
- Reachability oracle `test_every_pattern_matches_some_probe` now uses
  `match_all()` (set membership) instead of `match()` (winner only). The
  probe corpus was extended from 70 to ~150 strings, each carrying an inline
  `# basekey=…` comment. Patterns that are intentionally shadowed (rare-X
  variants that always lose to a higher-priority equivalent) live in
  `_KNOWN_SHADOWED` with one-line reasons.

**Repository hygiene**
- `benchmarks/results/` and `benchmarks/baseline_test.json` are git-ignored
  (105 regenerable benchmark outputs removed from the index).
- `requirements.txt` reduced to `-e .[dev,test,bench]` plus a header pointing
  to `pyproject.toml` as the canonical dependency declaration.
- `README.md` pattern counts updated to `1,072 generated date patterns (from
  134 base patterns)` (matching current `ALL_PATTERNS`).
- Root-level scratch files (`tests.py`, `dateparser.code-workspace`,
  `reproduce_issues.py`) removed or moved to `scripts/repro_2026_09_weekday_bug.py`.

**CI / lint**
- GitHub Actions CI: Ruff is now a gate (`ruff check qddate tests scripts`),
  refresh Python matrix `[3.10, 3.11, 3.12, 3.13, 3.14]`, coverage gate at
  `--cov-fail-under=85`, `QDDATE_PERF=1` so the new
  `tests/test_performance_smoke.py` runs on every CI invocation.
- `pyproject.toml`: `requires-python = ">=3.10"`; classifiers refreshed;
  Ruff `line-length = 120` with per-file ignores for pattern-table scripts.
- `tox.ini` envlist updated to `py310,py311,py312,py313,py314`.
- Lint baseline: 0 ruff errors (down from 355).

The following changes landed before 1.0.11 and were previously listed under a
stray "Unreleased" heading:

- Replaced the Sphinx/Read the Docs pages with a Docusaurus site in `docs/`, organized like undatum (getting started, use cases, API, languages, development) and ready for GitHub Pages.

- Added Ukrainian (`uk`) month-name and abbreviated date patterns, including genitive forms.

**Romanian language support**
- Added full and CLDR-abbreviated Romanian month-name patterns in lowercase and
  title case, including generated time and trailing-text variants.
- Added `ro` to `SUPPORTED_LANGUAGES` and the `languages=` filter, with explicit
  metadata, prefix, character-set, and automatic-detection integration.
- Kept shared `Mai` and `August` tokens ambiguous for unrestricted parsing while
  making their Romanian pattern identity deterministic under `languages="ro"`.
- Added fixture-backed regression coverage for the data.gov.ro date corpus.

**Refactor (behavior-preserving)**
- Replaced the three duplicated copies of substring-based language/separator
  inference in `qdparser.py` (`_infer_char_sets`, `_build_language_index`,
  `_build_separator_index`) with reads from a single authoritative
  `_PATTERN_METADATA` table in `qddate.patterns`. Net ~120 lines removed from
  `qdparser.py`. Adding or renaming a pattern no longer requires editing multiple
  inference sites.
- Simplified `_calculate_pattern_priority` to use the stamped `language` field
  instead of substring matching.
- `_infer_char_sets` now distinguishes numeric-only patterns (including the
  language-tagged but numerically-formatted `date_usa`/`date_usa_1`) via an
  explicit `_NUMERIC_PATTERN_KEYS` set, eliminating the old `has_month_names`
  heuristic.
- Added `tests/test_pattern_metadata.py`: safety-net tests proving the stamped
  fields reproduce the pre-refactor inference bit-for-bit (language, separator,
  and charset oracles), plus reachability tests ensuring every generated pattern
  is findable through each filter index.

**Correctness**
- Fixed `languages=` regression: automatic language detection no longer drops a
  language the caller explicitly requested. Previously, a shared month name (e.g.
  German/Dutch "Juli") could cause `DateParser(languages=["en","de"]).parse("28. Juli 2015")`
  to return `None`; it now correctly returns `2015-07-28`.
- Fixed `ENG_WEEKDAYS` typo: `"Satuday"` → `"Saturday"`, so full-weekday strings
  like `Saturday 6 May 2023` now match.
- Fixed `ENG_MONTHS_LC` typo: `"jule"` → `"july"`.
- Replaced the broken `__main__` block in `qdparser.py` (it referenced an undefined
  `r` and imported an optional dependency unguarded) with a working smoke demo.

**Testing**
- Reconciled three "should return None" tests that drifted after 1.0.7 added German
  short-month and English ordinal patterns (`14th April 2015:`, `15. Jul 2023`,
  `5. jan 2020` now asserted as valid).
- Added regression test for the `languages=` allow-list vs. auto-detection.
- Added `Saturday` full-weekday test.

**Packaging & hygiene**
- Moved `dateparser` from a hard runtime dependency to an optional `bench` extra
  (`pip install -e ".[bench]"`). The library never imported it at runtime; it is only
  used by `benchmarks/`. Runtime deps are now `pyparsing` only.
- Guarded the unguarded `import dateparser` in `benchmarks/bench.py`.
- Removed unused `dill` import and `DILL_ENABLED` flag from `qdparser.py`.
- Narrowed bare `except:` clauses to `except Exception:`.
- Removed unused `os` import from `qdparser.py`.
- Deduplicated `BASE_DATE_PATTERNS` entries (`pat:date:ddmmyyyy`, `pat:date:mmyyyy`
  were each defined twice).
- Stopped tracking build artifacts in git (`profile_results/`, root `tests.py`,
  `reproduce_issues.py`); extended `.gitignore` (`.venv-*/`, `profile_results/`).

**Documentation**
- README: corrected pattern counts (124 base → 992 generated, previously "712+ / 89"),
  added the missing Dutch language to the supported-languages list, and documented
  the `languages=` parameter with a usage example.

## 1.0.10 (2026-07-05)

**English date patterns**
- Added `dt:date:weekday_eng_abbrev3` for full weekday with abbreviated month-first dates, e.g. `Thursday, Jun 25, 2026 - 09:08`
- Registered the new pattern in prefix matching for faster candidate filtering

**Testing**
- Added test cases for weekday + abbreviated month formats with optional trailing time

## 1.0.9 (2026-07-05)

**Spanish date patterns**
- Extended `dt:date:es_base_article` and `dt:date:es_base_lc_article` to accept a comma before the year, e.g. `03 de Julio, 2026` (common on Latin American government sites)
- Updated Spanish benchmark data generator to cover comma-before-year variants

**Testing**
- Added test cases for Spanish article dates with comma before the year

## 1.0.8 (2026-01-03)

**Benchmarking Tools**
- Added `scripts/generate_webpage_test_data.py` for generating test data from real-world webpages
  - Fetches HTML content from government and international organization websites
  - Extracts text snippets and tests them with qddate's match() method
  - Generates CSV files with text snippets and pattern matches for benchmarking
- Added `benchmarks/benchmark_webpage_data.py` for comparing qddate with other libraries using webpage data
  - Benchmarks qddate against dateparser and dateutil using real-world text snippets
  - Measures success rates and performance metrics
  - Outputs results in JSON and text formats
- Updated README with documentation for new benchmark tools

## 1.0.7 (2026-01-01)

**Language Coverage - Phase 1 Enhancements**
- **CRITICAL**: Completed Czech language patterns (was broken with 0 patterns)
  - Added 4 patterns with genitive month support similar to Polish
  - Czech dates like "15 Leden 2015", "5 ledna 2020" now supported
  - Fixed "Incomplete" status - Czech is now fully functional
- **Enhanced German** patterns from 2 to 8 (+6 patterns)
  - Added weekday patterns: "Montag, 28. Juli 2015"
  - Added abbreviated months: "15. Jul 2023", "5. jan 2020"
  - Added rare month-first formats
- **Enhanced English** patterns (+6 patterns)
  - Added abbreviated month support: "24 Jul 2015", "Jan 15, 2020"
  - Added weekday with abbreviations: "Fri, 24 Jul 2015"
  - Added ordinal suffix patterns: "8th Jul 2015"

**Testing**
- Added 16 new test cases covering all new patterns
- 4 Czech tests, 6 German tests, 6 English abbreviation tests
- All tests passing

**Pattern Count**: 16 new patterns added (Czech: 4, German: 6, English: 6)

## 1.0.6 (2026-01-01)

**Infrastructure**
- Migrated CI/CD from Travis CI to GitHub Actions with Python 3.8-3.12 matrix testing
- Modernized `pyproject.toml` to PEP 621 standard with optional dependencies
- Added Ruff linter configuration for code quality

**Performance**
- **Critical**: Eliminated expensive list copying in `matchPrefix()` hot path (~15-25% faster)
- Pre-computed combined basekey lists to avoid runtime allocations
- All Phase 1 optimizations from `PERFORMANCE_ANALYSIS.md` now implemented

**Robustness**
- Fixed missing Turkish and Polish pattern keys in prefix matching
- Added support for comma-separated dates: `7 August, 2015`
- Added `dt:date:weekday_eng_mixed` pattern for `Wednesday 22 Apr 2015` format
- Updated `dt:date:date_eng1` to allow optional comma after month

**Testing**
- Added 3 new test cases for previously unsupported date formats
- All 69 tests passing

## 1.0.5 (2025-11-25)
- Updated README and benchmark documentation with current performance guidance and references to `benchmarks/bench.py` and `PERFORMANCE_ANALYSIS.md`.
- Added explicit instructions for running the benchmark and inviting community-reported numbers.

## 1.0.3 (2022-02-09)

No changelog entry was recorded for this release (tagged `v1.0.3` in git).
Git has no `v1.0.4` tag.

## 1.0.2 (2022-01-27)
- Added pattern `dt:date:date_eng4_short` to cover `17-Oct-21` style dates common in UK open data.

## 1.0.1 (2022-01-15)
- Added the `noyear` flag to the `match` function to disable patterns without year data.
- Added `patterns` and `base_only` parameters to `DateParser.__init__` to make pattern selection configurable.
- Disabled pattern `dt:date:date_7` (dates like `09.2019`) due to excessive false positives.

## 0.1.1 (2018-07-20)
- Code cleanup and moved date patterns into `qddate.patterns`.

## 0.1.0 (2018-01-14)
- First public release on PyPI and GitHub.
