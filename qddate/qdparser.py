#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Ivan Begtin (ivan@begtin.tech)"
__license__ = "BSD"


from .patterns import ALL_PATTERNS, BASE_TIME_PATTERNS
from pyparsing import Optional, lineStart, oneOf, Literal, restOfLine, ParseException
import datetime
from .dirty import matchPrefix


class DateParser:
    """Class to use pyparsing-based patterns to parse dates"""

    def __init__(self, generate=True, patterns=ALL_PATTERNS, base_only=False):
        """Inits class DataParser
        :param generate: Boolean value, if true, than automatically generate all patterns from base list self.patterns
        :param patterns: list of patterns to be used. Default ALL_PATTERNS. See qddate.patterns for more info
        :param base_only: Use only base patterns during generation of final list. Filters all patterns with text after datetime.
        """
        self.patterns = patterns
        if generate:
            self.__generate(base_only)
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
        self.cachedpats = [x for x in self.patterns if x["key"] in cached_p]

    def endSession(self):
        self.cachedpats = None

    def __generate(self, base_only=False):
        """Generates dates patterns"""
        base = []
        texted = []
        for pat in self.patterns:
            data = pat.copy()
            data["basekey"] = data["key"]
            data["key"] += ":time_1"
            data["right"] = True
            data["pattern"] = (
                data["pattern"]
                + Optional(Literal(",")).suppress()
                + BASE_TIME_PATTERNS["pat:time:minutes"]
            )
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 5,
                "max": data["length"]["max"] + 8,
            }
            base.append(data)

            data = pat.copy()
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_2"
            data["pattern"] = (
                data["pattern"]
                + Optional(oneOf([",", "|", 'T'])).suppress()
                + BASE_TIME_PATTERNS["pat:time:full"]
            )
            data["time_format"] = "%H:%M:%S"
            data["length"] = {
                "min": data["length"]["min"] + 9,
                "max": data["length"]["max"] + 9,
            }
            base.append(data)

            data = pat.copy()
            data["basekey"] = data["key"]
            data["right"] = True
            data["key"] += ":time_3"
            data["pattern"] = (
                data["pattern"]
                + Optional(Literal("[")).suppress()
                + BASE_TIME_PATTERNS["pat:time:minutes"]
                + Optional(Literal("]")).suppress()
            )
            data["time_format"] = "%H:%M"
            data["length"] = {
                "min": data["length"]["min"] + 7,
                "max": data["length"]["max"] + 10,
            }
            base.append(data)

            data = pat.copy()
            data["pattern"] = data["pattern"]
            data["right"] = True
            data["basekey"] = data["key"]
            base.append(data)

        if not base_only:
            for pat in base:
                # Right
                data = pat.copy()
                data["key"] += ":t_right"
                data["pattern"] = (
                    lineStart
                    + data["pattern"]
                    + Optional(oneOf([",", "|", ":", ")"])).suppress()
                    + restOfLine.suppress()
                )
                data["length"] = {
                    "min": data["length"]["min"] + 1,
                    "max": data["length"]["max"] + 90,
                }
                texted.append(data)

            base.extend(texted)
        self.patterns = base

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
            pats = self.patterns
        if n > 5 and not noprefix:
            basekeys = self.__matchPrefix(text[:6])
        else:
            basekeys = []
        for p in pats:
            if n < p["length"]["min"] or n > p["length"]["max"]:
                continue
            if p["right"] and len(basekeys) > 0 and p["basekey"] not in basekeys:
                continue
            if not noyear and 'noyear' in p.keys() and p['noyear']:
                continue
            try:
                r = p["pattern"].parseString(text)
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
            except ParseException as e:
                #                print p['key'], text.encode('utf-8'), e
                pass
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
            if "noyear" in p and p["noyear"] == True:
                d["year"] = datetime.datetime.now().year
            for k, v in list(r.items()):
                d[k] = int(v)
            dt = datetime.datetime(**d)
            return dt
        return None


if __name__ == "__main__":
    from pprint import pprint

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
        u"2 Июня 2015",
        u"9 июля 2015 г.",
        u"26 / 06 ‘15",
        u"09.июля.2015",
        u"14th April 2015:",
        u"23 Jul 2015, 09:00 BST",
        u"пятница, июля 17, 2015",
        u"Июль 16, 2015",
        u"Le 8 juillet 2015",
        u"8 juillet 2015",
        u"Fri 24 Jul 2015",
        u"26 de julho de 2015",
        u"17 de Junio de 2015",
        u"28. Juli 2015",
        u"21 Фeвpyapи 2015",
        u"1 нoeмвpи 2013",
        u"23 июня 2015",
        u"3 Июля, 2015",
        u"7 August, 2015",
        u"Wednesday 22 Apr 2015",
        u"12-08-2015 - 09:00",
        u"08 Jul, 2015",
        u"August 10th, 2015",
        u"junio 9, 2015",
        u"Авг 11, 2015",
        u"Вторник, 18 Август 2015 18:51",
        u"Июль 16th, 2012 | 11:08 пп",
        u"19 август в 16:03",
        u"7 August, 2015",
        u"9 Июля 2015 [11:23]",
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
    import dateparser

    for text in tests:
        pass
        # print(dateparser.parse(text))
#    ind.patterns = DATE_DATA_TYPES_RAW
