---
title: "Troubleshooting"
description: "Why parse returns None, and how to diagnose misses"
---
# Troubleshooting

qddate fails closed: unsupported or malformed input returns `None` instead of
raising. This page covers the usual reasons and how to inspect a miss.

## `parse()` returns `None`

Check these in order:

1. **The date is not at the start of the string.** `published 12.03.1999` does not match; `12.03.1999 published` does.
2. **The format is not in the catalog.** Rare layouts need a new pattern. See [adding languages](/development/adding-languages).
3. **The language was excluded.** `DateParser(languages="en")` will not parse Russian month names.
4. **The calendar date is invalid.** Month 13, day 0, or a non-existent day becomes `None`.
5. **The string is too short or empty.** `""`, whitespace, and `"1"` return `None`.

## Inspect the matched pattern

When a parse succeeds but looks wrong, inspect `match()`:

```python
result = parser.match(text)
if result is None:
    print("no pattern matched")
else:
    print(result["pattern"]["key"])
    print(result["pattern"].get("name"))
    print(dict(result["values"]))
```

## A language you requested is missing

`languages=` is an allow-list. Automatic language detection is only a candidate
filter and must not drop a language you passed in. If a German or Dutch shared
month name (`Juli`) fails under `languages=["de"]`, that is a bug — please
[open an issue](https://github.com/ivbeg/qddate/issues).

Unsupported codes raise at construction:

```python
qddate.DateParser(languages="xx")
# ValueError: Unsupported language(s): ['xx']
```

## Ambiguous numeric dates

`01.02.2003` is day-month-year in the numeric catalog, not US month-day-year.
US-style `mm/dd/yyyy` lives on English patterns (`date_usa`). Restrict
`languages="en"` if you need that reading, or prefer unambiguous ISO strings.

## Import or dependency errors

- Runtime: `pyparsing>=3.1.0` only.
- `ModuleNotFoundError: dateparser` means a **benchmark** script is running without the `bench` extra: `pip install -e ".[bench]"`.
- Python older than 3.8 is not supported.

## Disable filters while debugging

If you believe a pattern exists but is filtered out, turn filters off one at a
time:

```python
parser.parse(text, noprefix=True, nocharsetfilter=True, nolanguagefilter=True)
```

If it then matches, the miss is a filter issue rather than a missing pattern.
Leave filters on in production.

## Still stuck

- Reproduce with a short script and the exact input string.
- Include OS, Python version, and `qddate.__version__`.
- Open an issue at [github.com/ivbeg/qddate/issues](https://github.com/ivbeg/qddate/issues).
