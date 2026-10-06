# OpenSpec Change: Add type hints to the public API

The public `DateParser` API is currently untyped. Adding parameter and return
type hints makes the library usable from mypy, pyright, and IDEs without
forcing contributors to read source to understand the contracts.

## Why

`qddate` is consumed by downstream libraries that increasingly enforce strict
typing in CI. Type hints on the public surface (`parse`, `match`, `match_all`,
`match_typed`, `parse_many`, `__init__`, `format_date`) let those callers
adopt `qddate` without `# type: ignore` comments. The hints also document the
contracts in a way the docstrings can't (return type of `match_all` is "list of
dicts", for example, which a hint spells out exactly).

## What changes

**Type hints on `DateParser.__init__`**
- New: parameter hints for `generate: bool`, `patterns: list[dict]`,
  `base_only: bool`, `languages: str|list[str]|None`,
  `pivot_year: int|None`, `tz_aware: bool`.
- Impact: Non-breaking.

**Type hints on `parse`, `match`, `match_all`, `match_typed`, `parse_many`**
- New: parameter hints (mostly `str` / `list[str]`) and return type hints
  (`datetime | None`, `dict | None`, `list[dict]`, `DateMatch | None`,
  `Iterator[datetime|None]`).
- Impact: Non-breaking.

**Type hints on `DateMatch`**
- New: field hints on the dataclass (`datetime`, `pattern_key`, `language`,
  `format`, `raw`).
- Impact: Non-breaking.

**Type hints on `format_date()`**
- New: parameter and return hints.
- Impact: Non-breaking.

## Out of scope

- Strict `mypy --strict` mode (the project does not enable it).
- Type hints on internal modules (`_filter_patterns_hierarchical`, etc.).
- Adding a `py.typed` marker to the wheel (a follow-up; needs packaging
  change).

## Impact

- **Breaking?** No — all hints are additive.
- **Affected:** IDE autocomplete, mypy/pyright in user projects, downstream
  type-checking CI.
- **Risk:** A wrong hint blocks consumers at type-check time. Mitigation: run
  mypy in CI before merging.
- **Rollback:** Self-contained revert.