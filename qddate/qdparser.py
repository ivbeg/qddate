#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"

import datetime
import os
import time

from pyparsing import Optional, lineStart, oneOf, Literal, restOfLine

try:
   import dill
   DILL_ENABLED = True
except:
   DILL_ENABLED = False

# Enable packrat parsing for better performance
try:
    from pyparsing import ParserElement
    ParserElement.enable_packrat()
except:
    pass

from .dirty import matchPrefix
from .patterns import ALL_PATTERNS, BASE_TIME_PATTERNS


class DateParser:
    """Class to use pyparsing-based patterns to parse dates"""

    def __init__(self, generate=True, patterns=ALL_PATTERNS, base_only=False):
        """Inits class DataParser
        :param generate: Boolean value, if true, than automatically generate all patterns from base list self.patterns
        :param patterns: list of patterns to be used. Default ALL_PATTERNS. See qddate.patterns for more info
        :param base_only: Use only base patterns during generation of final list. Filters all patterns with text after datetime.
        """
        self.patterns = patterns
        self._current_year = datetime.datetime.now().year
        self._year_refresh_interval = 3600  # seconds
        self._next_year_refresh = time.monotonic() + self._year_refresh_interval
        if generate:
            self.__generate(base_only)
        self._build_length_index()
        self.cachedpats = None
        self.ind = []

    def __matchPrefix(self, text):
        """
        This is silver bullet, cornerstone and magic wand of speed of this algorithm
        it filters patterns using manually selected rules. Yes, yes, it's "dirty" code and it could be beautified in
        many ways but this library intended to be fast, not beautiful. Without matching is x1.3 slower so let it be.
        :param text: text with date to match
        :return: list of patterns to run against
        """
        return matchPrefix(text)

    def startSession(self, cached_p):
        cached_set = set(cached_p) if not isinstance(cached_p, set) else cached_p
        self.cachedpats = [x for x in self.patterns if x["key"] in cached_set]

    def endSession(self):
        self.cachedpats = None

    def __generate(self, base_only=False):
        """Generates dates patterns"""
        base = []
        texted = []
        for pat in self.patterns:
            data = {**pat}
            data["basekey"] = data["key"]
            data["key"] += ":time_1"
            data["right"] = True
            data["pattern"] = (data["pattern"] +
                               Optional(Literal(",")).suppress() +
                               BASE_TIME_PATTERNS["pat:time:minutes"])
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 5,
                "max": data["length"]["max"] + 8,
            }
            base.append(data)

            data = {**pat}
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_2"
            data["pattern"] = (data["pattern"] +
                               Optional(oneOf([",", "|", "T"])).suppress() +
                               BASE_TIME_PATTERNS["pat:time:full"])
            data["time_format"] = "%H:%M:%S"
            data["length"] = {
                "min": data["length"]["min"] + 9,
                "max": data["length"]["max"] + 9,
            }
            base.append(data)

            data = {**pat}
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_3"
            data["pattern"] = (data["pattern"] +
                               Optional(Literal("[")).suppress() +
                               BASE_TIME_PATTERNS["pat:time:minutes"] +
                               Optional(Literal("]")).suppress())
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 7,
                "max": data["length"]["max"] + 10,
            }
            base.append(data)

            data = {**pat}
            data["pattern"] = data["pattern"]
            data["right"] = True
            data["basekey"] = data["key"]
            base.append(data)

        if not base_only:
            for pat in base:
                # Right
                data = {**pat}
                data["key"] += ":t_right"
                data["pattern"] = (
                    lineStart + data["pattern"] +
                    Optional(oneOf([",", "|", ":", ")"])).suppress() +
                    restOfLine.suppress())
                data["length"] = {
                    "min": data["length"]["min"] + 1,
                    "max": data["length"]["max"] + 90,
                }
                texted.append(data)

            base.extend(texted)
        self.patterns = base

    def _build_length_index(self):
        """Pre-index patterns by length ranges for faster filtering"""
        self._patterns_by_length = {}
        for p in self.patterns:
            min_len = p["length"]["min"]
            max_len = p["length"]["max"]
            for length in range(min_len, max_len + 1):
                if length not in self._patterns_by_length:
                    self._patterns_by_length[length] = []
                self._patterns_by_length[length].append(p)

    def match(self, text, noprefix=False, noyear=True):
        """Matches date/datetime string against date patterns and returns pattern and parsed date if matched.
        It's not indeded for common usage, since if successful it returns date as array of numbers and pattern
        that matched this date

        :param text:
            Any human readable string
        :type date_string: str|unicode
        :param noprefix:
            If set True than doesn't use prefix based date patterns filtering settings
        :type noprefix: bool
        :param noyear:
            If set True than does use patterns with noyear flag (does a lot of false positives) if set False doesn't use patterns with noyear flag
        :type noprefix: bool


        :return: Returns dicts with `values` as array of representing parsed date and 'pattern' with info about matched pattern if successful, else returns None
        :rtype: :class:`dict`."""
        n = len(text)
        if self.cachedpats is not None:
            pats = self.cachedpats
        else:
            # Use length-based indexing if available
            if hasattr(self, '_patterns_by_length'):
                pats = self._patterns_by_length.get(n, [])
            else:
                pats = self.patterns
        if n > 5 and not noprefix:
            basekeys = self.__matchPrefix(text[:6])
        else:
            basekeys = []
        basekeys_len = len(basekeys)
        for p in pats:
            # Cache dictionary lookups
            length_min = p["length"]["min"]
            length_max = p["length"]["max"]
            if n < length_min or n > length_max:
                continue
            p_right = p.get("right", False)
            if p_right and basekeys_len > 0:
                p_basekey = p.get("basekey")
                if p_basekey not in basekeys:
                    continue
            if not noyear:
                p_noyear = p.get("noyear", False)
                if p_noyear:
                    continue
            match_data = next(p["pattern"].scanString(text, maxMatches=1), None)
            if match_data is None:
                continue
            r, start, _ = match_data
            if start != 0:
                continue
            # Do sanity check
            d = r.asDict()
            if "month" in d:
                val = int(d["month"])
                if val > 12 or val < 1:
                    continue
            if "day" in d:
                val = int(d["day"])
                if val > 31 or val < 1:
                    continue
            return {"values": r, "pattern": p}
        return None

    def parse(self, text, noprefix=False):
        """Parse date and time from given date string.

        :param text:
            Any human readable string
        :type date_string: str|unicode
        :param noprefix:
            If set True than doesn't use prefix based date patterns filtering settings
        :type noprefix: bool


        :return: Returns :class:`datetime <datetime.datetime>` representing parsed date if successful, else returns None
        :rtype: :class:`datetime <datetime.datetime>`."""

        res = self.match(text, noprefix)
        if res:
            r = res["values"]
            p = res["pattern"]
            d = {"month": 0, "day": 0, "year": 0}
            if p.get("noyear", False):
                d["year"] = self._get_cached_year()
            for k, v in r.items():
                d[k] = int(v)
            dt = datetime.datetime(**d)
            return dt
        return None

    def _get_cached_year(self):
        """Return cached current year, refreshing periodically."""
        now = time.monotonic()
        if now >= self._next_year_refresh:
            self._current_year = datetime.datetime.now().year
            self._next_year_refresh = now + self._year_refresh_interval
        return self._current_year


if __name__ == "__main__":

    tests = [
        "01.12.2009",
        "2013-01-12",
        "31.05.2001",
        "7/12/2009",
        "6 Jan 2009",
        "Jan 8, 1098",
        "JAN 1, 2001",
        "3 Января 2003 года",
        "05 Января 2003",
        "12.03.1999 Hello people",
        "15 февраля 2007 года",
        "5 August 2001",
        "3 jun 2009",
        "16 May 2009 14:10",
        "01 february 2009",
        "01.03.2009 14:53",
        "01.03.2009 14:53:12",
        "22.12.2009 17:56",
        "05/16/99",
        "11/29/1991",
        "Thursday 4 April 2019",
        "July 01, 2015",
        "Fri, 3 July 2015",
        "2 Июня 2015",
        "9 июля 2015 г.",
        "26 / 06 ‘15",
        "09.июля.2015",
        "14th April 2015:",
        "23 Jul 2015, 09:00 BST",
        "пятница, июля 17, 2015",
        "Июль 16, 2015",
        "Le 8 juillet 2015",
        "8 juillet 2015",
        "Fri 24 Jul 2015",
        "26 de julho de 2015",
        "17 de Junio de 2015",
        "28. Juli 2015",
        "21 Фeвpyapи 2015",
        "1 нoeмвpи 2013",
        "23 июня 2015",
        "3 Июля, 2015",
        "7 August, 2015",
        "Wednesday 22 Apr 2015",
        "12-08-2015 - 09:00",
        "08 Jul, 2015",
        "August 10th, 2015",
        "junio 9, 2015",
        "Авг 11, 2015",
        "Вторник, 18 Август 2015 18:51",
        "Июль 16th, 2012 | 11:08 пп",
        "19 август в 16:03",
        "7 August, 2015",
        "9 Июля 2015 [11:23]",
    ]

    #    print list(calendar.month_abbr)[1:]
    ind = DateParser(generate=True)
    #    for i in ind.patterns:
    #        print i
    print(len(ind.patterns))
    for text in tests:
        res = ind.match(text)
        print(r)
        if r:
            r = res["values"]
            p = res["pattern"]
            d = {"month": 0, "day": 0, "year": 0}
            if "noyear" in p and p["noyear"] == True:
                d["year"] = datetime.datetime.now().year
            for k, v in list(r.items()):
                d[k] = int(v)
            dt = datetime.datetime(**d)
        else:
            pass

    #    for p in ind.patterns:
    #        pprint(p)

    for text in tests:
        pass
        # print(dateparser.parse(text))
#    ind.patterns = DATE_DATA_TYPES_RAW
