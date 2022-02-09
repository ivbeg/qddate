======================================================================================
qddate -- quick and dirty python parser dates what could be found during HTML scraping
======================================================================================

.. image:: https://img.shields.io/travis/ivbeg/qddate/master.svg?style=flat-square
    :target: https://travis-ci.org/ivbeg/qddate
    :alt: travis build status

.. image:: https://img.shields.io/pypi/v/qddate.svg?style=flat-square
    :target: https://pypi.python.org/pypi/qddate
    :alt: pypi version

.. image:: https://readthedocs.org/projects/qddate/badge/?version=latest
    :target: http://qddate.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://codecov.io/gh/scrapinghub/dateparser/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/ivbeg/qddate
   :alt: Code Coverage

.. image:: https://badges.gitter.im/scrapinghub/dateparser.svg
   :alt: Join the chat at https://gitter.im/ivbeg/qddate
   :target: https://gitter.im/ivbeg/qddate?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


`qddate` is a Python 3 lib that helps to parse any date strings from html pages extremely fast. This lib was created during long term
news aggregation efforts and analyzing in wild HTML pages with dates. It's not intended to have beautiful code,
support for so much languages as possible and so on. It should help to process millons of strings to identify
and parse dates. qddata was part of proprietary technology of "news reconstruction". It's used to automatically create
RSS feeds from sites without it.



If you are looking for more advanced (and slower) date parsing try `dateparser <https://github.com/scrapinghub/dateparser>`_
and `dateutil <https://launchpad.net/dateutil>`_.




Documentation
=============

Documentation is built automatically and can be found on
`Read the Docs <https://qddate.readthedocs.org/en/latest/>`_.


Features
========

* More than 348 date patterns supported (by the end 2017)
* Generic parsing of dates in English, Russian, Spanish, Portugenese and other languages
* Supports strings with with left aligned dates and supplimental words. Example: "12.03.1999 some text here"
* Extremely fast, uses pyparsing, hard-coded constants and dirty speed optimizations tricks


Limitations
===========

* Not all languages supported, more languages will be added by request and example
* Not so easy to add new language based date patterns as it's in dateparser for example.
* Could miss some rarely used date formats
* Doesn't support relative dates
* Doesn't support calendars


Speed optimization
==================

* All constants are hard encoded, no external settings
* Uses only datetime and pyparsing as external libraries. No more dependencies, all reused code incorporated into the lib code
* No regular expressions, instead pre-generated pyparsing patterns
* Intensive pattern filtering using min/max text length filters and common text patterns
* No one settings/data file loaded from disk


Usage
=====

The easiest way is to use the `qddate.DateParser <#qddate.DateParser>`_ class,
and it's `parse` function.


Popular Formats
---------------

    >>> import qddate
    >>> parser = qddate.DateParser()
    >>> parser.parse('2012-12-15')
    datetime.datetime(2012, 12, 15, 0, 0)
    >>> parser.parse(u'Fri, 12 Dec 2014 10:55:50')
    datetime.datetime(2014, 12, 12, 10, 55, 50)
    >>> parser.parse(u'пятница, июля 17, 2015')  # Russian (17 July 2015)
    datetime.datetime(2015, 1, 13, 13, 34)


This will try to parse a date from the given string, attempting to
detect the language each time.



Dependencies
============

`qddate` relies on following libraries in some ways:

  * pyparsing_ is a module for advanced text processing.


.. _pyparsing: https://pypi.python.org/pypi/pyparsing


Supported languages
===================

* Bulgarian
* Czech
* English
* French
* German
* Portuguese
* Russian
* Spanish

Thanks
======
I wrote this date parsing code at 2008 year and later only updated it several times, migrating from regular expressions
to pyparsing. Looking at `dateparser <https://github.com/scrapinghub/dateparser>` clean code and documentation motivated me
to return to this code and to clean it up and to share it publicly. I've used same documentation and code style approach
and reused build scripts and documentation generation style from dateutil.
Many thanks to ScrapingHub team!


.. image:: https://badges.gitter.im/qddate/Lobby.svg
   :alt: Join the chat at https://gitter.im/qddate/Lobby
   :target: https://gitter.im/qddate/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
