---
title: "parse()"
description: "Turn a left-aligned date string into datetime.datetime or None"
---
# parse()

`DateParser.parse()` is the method most applications should call.

```python
parser.parse(text) -> datetime.datetime | None
```

## Signature

```python
parse(
    text,
    noprefix=False,
    nocharsetfilter=False,
    noseparatorfilter=False,
    noyearformatfilter=False,
    nolanguagefilter=False,
)
```

| Argument | Default | Meaning |
|----------|---------|---------|
| `text` | required | Input string |
| `noprefix` | `False` | Skip prefix-based candidate filtering |
| `nocharsetfilter` | `False` | Skip character-set filtering |
| `noseparatorfilter` | `False` | Skip separator filtering |
| `noyearformatfilter` | `False` | Skip 2-digit vs 4-digit year filtering |
| `nolanguagefilter` | `False` | Skip automatic language narrowing |

Leave the `no*` flags at `False` unless you are debugging a miss. See
[troubleshooting](/getting-started/troubleshooting).

## Return value

- A naive `datetime.datetime` when a supported pattern matches at index 0 and the components form a valid calendar date.
- `None` when nothing matches, the string is empty/whitespace, or `datetime.datetime(**components)` would raise `ValueError`.

`parse()` never raises for ordinary bad input.

## Behavior notes

- Matching is **left-aligned**. Trailing text after the date is ignored.
- Optional `HH:MM` / `HH:MM:SS` suffixes populate hour, minute, and second.
- Patterns flagged `noyear` substitute the current year (via `match(..., noyear=True)`, which `parse()` uses).
- Timezone abbreviations are not applied.

## Examples

```python
import datetime
import qddate

parser = qddate.DateParser()
assert parser.parse("01.12.2009") == datetime.datetime(2009, 12, 1)
assert parser.parse("12.03.1999 Hello people") == datetime.datetime(1999, 3, 12)
assert parser.parse("16 May 2009 14:10") == datetime.datetime(2009, 5, 16, 14, 10)
assert parser.parse("totally invalid date") is None
```

## Related

- [match()](/api/match)
- [Basic usage](/getting-started/basic-usage)
