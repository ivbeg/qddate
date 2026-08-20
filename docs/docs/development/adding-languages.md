---
title: "Adding languages"
description: "How to add a language catalog and keep metadata in sync"
---
# Adding languages

Languages in qddate are **hand-written pattern tables**, not runtime locale
data. That is the speed tradeoff: new coverage is a code change plus tests.

English and Russian are the historical cores. Other languages follow the same
shape.

## Checklist

1. Add `qddate/patterns/<code>.py` with month/weekday constants and `PATTERNS_<CODE>` dicts (`key`, `name`, `pattern`, `length`, `format`, flags).
2. Export the list from `qddate/patterns/__init__.py` and append it to `ALL_PATTERNS`.
3. Add the code to `SUPPORTED_LANGUAGES` and `PATTERNS_BY_LANGUAGE`.
4. Stamp each base key in `_PATTERN_METADATA` as `(language, separator)`.
5. Teach prefix matching in `qddate/dirty.py` if the language needs distinct prefixes.
6. Add month tokens to the detection sets in `qddate/qdparser.py` when automatic narrowing should see them. Skip tokens that collide with other languages (see Romanian `mai` / `august`).
7. Add tests (`tests/test_<language>.py` and/or JSON fixtures under `tests/fixtures/`).
8. Regenerate docs: `python scripts/generate_pattern_docs.py`.
9. Mention the language in the README supported-languages list.

## Pattern dict fields

Typical keys:

- `key` — stable id, e.g. `dt:date:de_base`
- `name` — human description
- `pattern` — pyparsing grammar
- `length` — `{"min": ..., "max": ...}`
- `format` — `strftime`-like hint for docs
- `yearshort`, `noyear`, `filter` — optional flags

Copy an existing language module (`de.py`, `ro.py`, `uk.py`) rather than inventing a new layout.

## Metadata table

`_PATTERN_METADATA` in `qddate/patterns/__init__.py` is the source of truth for
language and separator. Adding a pattern without an entry there will fail the
oracle tests in `tests/test_pattern_metadata.py`.

Numeric, language-neutral keys use `language=None`.

## What not to do

- Do not add runtime I/O or CLDR JSON loading on the parse path.
- Do not put new languages in a removed `consts.py` / `DATE_DATA_TYPES_RAW` (older docs mentioned that; patterns now live per-module under `qddate/patterns/`).
- Do not rely on automatic detection to substitute for `languages=` in tests — pin the code.

## Related

- [languages=](/api/languages)
- [Contributing](/development/contributing)
- [Language overview](/languages/)
