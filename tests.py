#!/usr/bin/env python
# -*- coding: utf-8 -*-s
from qddate import DateParser
import dateparser
import datetime
from pprint import pprint
from timeit import timeit

TESTS = ['01.12.2009',
         '2013-01-12',
         '31.05.2001',
         '7/12/2009',
         '6 Jan 2009',
         'Jan 8, 1098',
         'JAN 1, 2001',
         '3 Января 2003 года',
         '05 Января 2003',
         '12.03.1999 Hello people',
         '15 февраля 2007 года',
         '5 August 2001',
         '3 jun 2009',
         '16 May 2009 14:10',
         '01 february 2009',
         '01.03.2009 14:53',
         '01.03.2009 14:53:12',
         '22.12.2009 17:56',
         '05/16/99',
         '11/29/1991',
         'Thursday 4 April 2019',
         'July 01, 2015',
         'Fri, 3 July 2015',
         u'2 Июня 2015',
         u'9 июля 2015 г.',
         u'26 / 06 ‘15',
         u'09.июля.2015',
         u'14th April 2015:',
         u'23 Jul 2015, 09:00 BST',
         u'пятница, июля 17, 2015',
         u'Июль 16, 2015',
         u'Le 8 juillet 2015',
         u'8 juillet 2015',
         u'Fri 24 Jul 2015',
         u'26 de julho de 2015',
         u'17 de Junio de 2015',
         u'28. Juli 2015',
         u'21 Фeвpyapи 2015',
         u'1 нoeмвpи 2013',
         u'23 июня 2015',
         u'3 Июля, 2015',
         u'7 August, 2015',
         u'Wednesday 22 Apr 2015',
         u'12-08-2015 - 09:00',
         u'08 Jul, 2015',
         u'August 10th, 2015',
         u'junio 9, 2015',
         u'Авг 11, 2015',
         u'Вторник, 18 Август 2015 18:51',
         u'Июль 16th, 2012 | 11:08 пп',
         u'19 август в 16:03',
         "18 Июля 2021 [17:48]"]

def run():
    dp = DateParser()
    for t in TESTS:
        res = dp.match(t)
        res2 = dp.parse(t)
        print(t, res, res2)

if __name__ == "__main__":   
    run()
    #compare()
