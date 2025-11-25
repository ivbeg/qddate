# Using `DateParser.match`

`DateParser` (`qddate.DateParser`) is the entry point for fast date parsing. It uses the base date patterns from `qddate.consts` and generates an extended list of patterns, which greatly reduces the number of string comparisons. Language selection is not yet implemented, but it does not slow down parsing.

This class wraps the core `qddate` functionality.

```{eval-rst}
.. autoclass:: qddate.DateParser
   :members: match
```

> **Warning:** `match` returns the raw matched date and the raw pattern.

```python
>>> dp.match("11 August 2017")
{'values': (['11', 8, '2017'], {'day': ['11'], 'month': [8], 'year': ['2017']}), 'pattern': {'key': 'dt:date:date_eng1', 'name': 'Date with english month', 'pattern': {W:(0123...) Suppress:(["."]) January | February | March | April | May | June | July | August | September | October | November | December Suppress:(["."]) W:(0123...)}, 'length': {'min': 10, 'max': 20}, 'format': '%d.%b.%Y', 'right': True, 'basekey': 'dt:date:date_eng1'}}
```

## Popular formats

```{eval-rst}
.. autoclass:: qddate.DateParser
   :members: parse
```

The `parse` method mimics the default behavior of [`dateparser`](https://github.com/scrapinghub/dateparser)'s `parse` function, except that it is part of the `DateParser` class (not a standalone function).

```python
>>> import qddate
>>> parser = qddate.DateParser()
>>> parser.parse("2012-12-15")
datetime.datetime(2012, 12, 12, 0, 0)
>>> parser.parse("Fri, 12 Dec 2014 10:55:50")
datetime.datetime(2014, 12, 12, 10, 55, 50)
>>> parser.parse("пятница, июля 17, 2015")  # Russian (17 July 2015)
datetime.datetime(2015, 1, 13, 13, 34)
>>> parser.parse("Le 8 juillet 2015")
datetime.datetime(2015, 7, 8, 0, 0)
```

`parse` attempts to detect the language for each string automatically.

