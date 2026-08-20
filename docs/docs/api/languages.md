---
title: "languages="
description: "Restrict DateParser to one or more language catalogs"
---
# languages=

`DateParser(languages=...)` limits which month-name catalogs are loaded. Numeric
ISO-like patterns still participate for the languages you select.

## Accepted values

| Value | Effect |
|-------|--------|
| `None` (default) | All 14 languages |
| `[]` | Same as all languages (backward compatible) |
| `"ru"` | Russian month-name patterns plus numeric patterns associated with that filter |
| `["en", "de"]` | Union of those catalogs |

Unsupported codes raise `ValueError` whose message contains `Unsupported language`.

```python
DateParser(languages="ru")
DateParser(languages=["en", "de"])
DateParser(languages="invalid")  # ValueError
```

## Supported codes

`bg`, `cz`, `de`, `en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `tr`, `uk`.

The live list is `qddate.patterns.SUPPORTED_LANGUAGES`. See the
[language overview](/languages/).

## Exclusive parsing

A parser restricted to English will not parse a Russian month-name date:

```python
en = qddate.DateParser(languages="en")
en.parse("3 Января 2003 года")  # None
```

The same string succeeds with `languages="ru"` or the default constructor.

## Detection vs allow-list

Automatic language detection (character sets and month tokens) only **narrows
candidates**. It must not drop a language you passed in `languages=`. Shared
tokens such as German/Dutch `Juli` remain parseable for every language you
requested.

Romanian `mai` and `august` overlap other languages; unrestricted parsing may
leave those tokens ambiguous, while `languages="ro"` selects Romanian metadata
deterministically.

## Related

- [DateParser](/api/dateparser)
- [Languages and patterns](/languages/)
- [When to use](/getting-started/when-to-use)
