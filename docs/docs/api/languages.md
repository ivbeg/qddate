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
| `None` (default) | All 15 languages |
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

`bg`, `cz`, `de`, `en`, `es`, `fr`, `it`, `nl`, `pl`, `pt`, `ro`, `ru`, `sk`, `tr`, `uk`.

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

## Per-call hint

`match()`, `match_all()`, `parse()` and `match_typed()` also take
`languages=`. There it is a preference, not a filter: the patterns of those
languages and the language-neutral ones run first, and the others only when
none of them matches. A scraper can keep one parser and pass each page's
language:

```python
parser = qddate.DateParser()
parser.match("18 Juni 1953", languages="de")  # de_base; nl_base without the hint
parser.parse("5 мая 2022", languages="en")    # still parses: the hint is soft
```

The candidate index for each set of hinted languages is built on first use
and kept; the parser is not rebuilt.

## Related

- [DateParser](/api/dateparser)
- [Languages and patterns](/languages/)
- [When to use](/getting-started/when-to-use)
