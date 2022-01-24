Using DateParser.match
--------------------


:class:`DateParser <qddate.DateParser>` is the only way to implement fast dates parsing.

The instance of :class:`DateParser <qddate.DateParser>` uses basic date patterns from :mod:`qddate.consts`
and generates extended list of patterns. It helps to reduce number of comparisons of strings significantly.
Right now no language selection implemented but it doesn't slow down date parsing.

This class wraps around the core :mod:`qddate` functionality.

.. autoclass:: qddate.DateParser
   :members: match

.. warning:: It returns raw matched date and raw pattern:

    >>> dp.match('11 August 2017')
    {'values': (['11', 8, '2017'], {'day': ['11'], 'month': [8], 'year': ['2017']}), 'pattern': {'key': 'dt:date:date_eng1', 'name': 'Date with english month', 'pattern': {W:(0123...) Suppress:(["."]) January | February | March | April | May | June | July | August | September | October | November | December Suppress:(["."]) W:(0123...)}, 'length': {'min': 10, 'max': 20}, 'format': '%d.%b.%Y', 'right': True, 'basekey': 'dt:date:date_eng1'}}



Popular Formats
---------------
.. autoclass:: qddate.DateParser
   :members: parse

Function 'parse' mimics default behavior of `dateparser <https://github.com/scrapinghub/dateparser>`_ 'parse' function.
Except that it is part of DateParser class, not standalone function.


    >>> import qddate
    >>> parser = qddate.DateParser()
    >>> parser.parse('2012-12-15')
    datetime.datetime(2012, 12, 12, 0, 0)
    >>> parser.parse(u'Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)
    >>> parser.parse(u'пятница, июля 17, 2015')  # Russian (17 July 2015)
    datetime.datetime(2015, 1, 13, 13, 34)
    >>> dp.parse(u'Le 8 juillet 2015')
    datetime.datetime(2015, 7, 8, 0, 0)

This will try to parse a date from the given string, attempting to detect the language each time automatically.
