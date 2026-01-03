#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
# Ensure we use the local qddate, not an installed version
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import importlib
import dateparser
import datetime
from pprint import pprint
import pyparsing
from timeit import timeit

try:
    from dateutil import parser as dateutil_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False

try:
    import arrow
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

try:
    import pendulum
    PENDULUM_AVAILABLE = True
except ImportError:
    PENDULUM_AVAILABLE = False

# Import DateParser - will be reloaded in functions that need fresh imports

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
         u'19 август в 16:03'
         u"9 Июля 2015 [11:23]",
         ]

def _run_dateparser():
    dates = []
    start = datetime.datetime.now()
    for text in TESTS:
        dates.append(dateparser.parse(text))
    fin = datetime.datetime.now() - start
    print('_run_dateparser elapsed: ' + str(fin))
    return fin

def _run_dateutil():
    if not DATEUTIL_AVAILABLE:
        return datetime.timedelta(0)
    dates = []
    start = datetime.datetime.now()
    for text in TESTS:
        try:
            dates.append(dateutil_parser.parse(text))
        except (ValueError, TypeError, AttributeError):
            dates.append(None)
    fin = datetime.datetime.now() - start
    print('_run_dateutil elapsed: ' + str(fin))
    return fin

def _run_arrow():
    if not ARROW_AVAILABLE:
        return datetime.timedelta(0)
    dates = []
    start = datetime.datetime.now()
    for text in TESTS:
        try:
            dates.append(arrow.get(text).datetime)
        except (ValueError, TypeError, AttributeError, arrow.parser.ParserError):
            dates.append(None)
    fin = datetime.datetime.now() - start
    print('_run_arrow elapsed: ' + str(fin))
    return fin

def _run_pendulum():
    if not PENDULUM_AVAILABLE:
        return datetime.timedelta(0)
    dates = []
    start = datetime.datetime.now()
    for text in TESTS:
        try:
            dates.append(pendulum.parse(text))
        except (ValueError, TypeError, AttributeError):
            dates.append(None)
    fin = datetime.datetime.now() - start
    print('_run_pendulum elapsed: ' + str(fin))
    return fin

def _run_qddate():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text))
    fin = datetime.datetime.now() - start
    print('_run_qddate elapsed: ' + str(fin))
    return fin

def _run_qddate_nopref():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, noprefix=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_nopref elapsed: ' + str(fin))
    return fin

def _run_qddate_nocharset():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, nocharsetfilter=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_nocharset elapsed: ' + str(fin))
    return fin

def _run_qddate_noseparator():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, noseparatorfilter=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_noseparator elapsed: ' + str(fin))
    return fin

def _run_qddate_noyearformat():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, noyearformatfilter=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_noyearformat elapsed: ' + str(fin))
    return fin

def _run_qddate_nolanguage():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, nolanguagefilter=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_nolanguage elapsed: ' + str(fin))
    return fin

def _run_qddate_all_filters_off():
    from qddate import DateParser
    dates = []
    start = datetime.datetime.now()
    ind = DateParser()
    for text in TESTS:
        dates.append(ind.parse(text, noprefix=True, nocharsetfilter=True, 
                              noseparatorfilter=True, noyearformatfilter=True, 
                              nolanguagefilter=True))
    fin = datetime.datetime.now() - start
    print('_run_qddate_all_filters_off elapsed: ' + str(fin))
    return fin


def compare():
    """Compare against dateparser"""
    for text in TESTS:
        ind = DateParser()
        d1 = ind.parse(text)
        d2 = ind.parse(text, noprefix=True)
        d3 = dateparser.parse(text)
        t = '%s | %s | %s | %s' % (str(d1), str(d2), str(d3), text)
        print(t)


def run():
    NUM_PASS = 5
    
    print('=' * 80)
    print('Pattern Filtering Performance Benchmark')
    print('=' * 80)
    print('Running %d passes for each configuration...' % NUM_PASS)
    print()
    
    # Time with all filters enabled (default)
    print('Testing: All filters enabled (default)...')
    total_qd = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd += _run_qddate()
    qd = total_qd.total_seconds() / NUM_PASS
    
    # Time without prefix filtering
    print('Testing: No prefix filter...')
    total_qd_nopref = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_nopref += _run_qddate_nopref()
    qd_nopref = total_qd_nopref.total_seconds() / NUM_PASS
    
    # Time without character set filtering
    print('Testing: No character set filter...')
    total_qd_nocharset = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_nocharset += _run_qddate_nocharset()
    qd_nocharset = total_qd_nocharset.total_seconds() / NUM_PASS
    
    # Time without separator filtering
    print('Testing: No separator filter...')
    total_qd_noseparator = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_noseparator += _run_qddate_noseparator()
    qd_noseparator = total_qd_noseparator.total_seconds() / NUM_PASS
    
    # Time without year format filtering
    print('Testing: No year format filter...')
    total_qd_noyearformat = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_noyearformat += _run_qddate_noyearformat()
    qd_noyearformat = total_qd_noyearformat.total_seconds() / NUM_PASS
    
    # Time without language filtering
    print('Testing: No language filter...')
    total_qd_nolanguage = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_nolanguage += _run_qddate_nolanguage()
    qd_nolanguage = total_qd_nolanguage.total_seconds() / NUM_PASS
    
    # Time with all filters disabled (baseline)
    print('Testing: All filters disabled (baseline)...')
    total_qd_all_off = datetime.timedelta()
    for _ in range(NUM_PASS):
        total_qd_all_off += _run_qddate_all_filters_off()
    qd_all_off = total_qd_all_off.total_seconds() / NUM_PASS
    
    # Time dateparser (for comparison)
    print('Testing: dateparser library...')
    dt = timeit("_run_dateparser()", setup="from __main__ import _run_dateparser", number=NUM_PASS)
    
    # Time dateutil (for comparison)
    if DATEUTIL_AVAILABLE:
        print('Testing: dateutil library...')
        dt_dateutil = timeit("_run_dateutil()", setup="from __main__ import _run_dateutil", number=NUM_PASS)
    else:
        dt_dateutil = None
        print('Testing: dateutil library... (not available)')
    
    # Time arrow (for comparison)
    if ARROW_AVAILABLE:
        print('Testing: arrow library...')
        dt_arrow = timeit("_run_arrow()", setup="from __main__ import _run_arrow", number=NUM_PASS)
    else:
        dt_arrow = None
        print('Testing: arrow library... (not available)')
    
    # Time pendulum (for comparison)
    if PENDULUM_AVAILABLE:
        print('Testing: pendulum library...')
        dt_pendulum = timeit("_run_pendulum()", setup="from __main__ import _run_pendulum", number=NUM_PASS)
    else:
        dt_pendulum = None
        print('Testing: pendulum library... (not available)')
    
    print()
    print('=' * 80)
    print('Performance Comparison Results')
    print('=' * 80)
    print()
    
    # Comparison with external libraries
    print('External Library Comparison (sorted by performance):')
    print('-' * 80)
    
    # Build list of libraries with their times
    libraries = [('qddate (all filters)', qd)]
    if dt_dateutil is not None:
        libraries.append(('dateutil', dt_dateutil))
    if dt_arrow is not None:
        libraries.append(('arrow', dt_arrow))
    if dt_pendulum is not None:
        libraries.append(('pendulum', dt_pendulum))
    libraries.append(('dateparser', dt))
    
    # Sort by time (fastest first)
    libraries.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
    
    # Find qddate position for comparison
    qddate_time = qd
    fastest_time = libraries[0][1] if libraries else qd
    
    for name, time_val in libraries:
        if time_val is None:
            continue
        time_diff = time_val - qddate_time
        if time_val < qddate_time:
            # This library is faster than qddate
            speedup = qddate_time / time_val
            pct_faster = ((qddate_time - time_val) / qddate_time) * 100
            print('  %-25s: %.6f sec (%.2fX FASTER than qddate, %.1f%% faster)' % 
                  (name, time_val, speedup, pct_faster))
        elif time_val > qddate_time:
            # This library is slower than qddate
            speedup = time_val / qddate_time
            pct_slower = ((time_val - qddate_time) / qddate_time) * 100
            print('  %-25s: %.6f sec (%.2fX SLOWER than qddate, %.1f%% slower)' % 
                  (name, time_val, speedup, pct_slower))
        else:
            # Same time (unlikely but handle it)
            print('  %-25s: %.6f sec (same as qddate)' % (name, time_val))
    print()
    
    # Summary explanation
    print('Performance Summary:')
    print('-' * 80)
    faster_than_qddate = [lib for lib in libraries if lib[1] is not None and lib[1] < qddate_time]
    slower_than_qddate = [lib for lib in libraries if lib[1] is not None and lib[1] > qddate_time]
    
    if faster_than_qddate:
        print('  Libraries FASTER than qddate:')
        for name, time_val in faster_than_qddate:
            speedup = qddate_time / time_val
            print('    - %s: %.2fX faster (%.6f sec vs %.6f sec)' % 
                  (name, speedup, time_val, qddate_time))
    
    if slower_than_qddate:
        print('  Libraries SLOWER than qddate:')
        for name, time_val in slower_than_qddate:
            speedup = time_val / qddate_time
            print('    - %s: %.2fX slower (%.6f sec vs %.6f sec)' % 
                  (name, speedup, time_val, qddate_time))
    
    print('  qddate performance: %.6f seconds' % qddate_time)
    if fastest_time and fastest_time < qddate_time:
        relative_speed = qddate_time / fastest_time
        print('  Fastest library is %.2fX faster than qddate' % relative_speed)
    elif fastest_time == qddate_time:
        print('  qddate is the fastest library!')
    print()
    
    # Individual filter impact
    print('Individual Filter Impact (vs all filters enabled):')
    print('-' * 80)
    
    def print_filter_comparison(name, time_without_filter, time_with_all_filters):
        if time_without_filter > time_with_all_filters:
            improvement = ((time_without_filter - time_with_all_filters) / time_without_filter) * 100
            speedup = time_without_filter / time_with_all_filters
            print('  %-25s: %.6f sec (%.2f%% faster with filter, %.2fX speedup)' % 
                  (name, time_without_filter, improvement, speedup))
        else:
            overhead = ((time_with_all_filters - time_without_filter) / time_with_all_filters) * 100
            slowdown = time_with_all_filters / time_without_filter
            print('  %-25s: %.6f sec (%.2f%% overhead, %.2fX slower)' % 
                  (name, time_without_filter, overhead, slowdown))
    
    print_filter_comparison('No prefix filter', qd_nopref, qd)
    print_filter_comparison('No charset filter', qd_nocharset, qd)
    print_filter_comparison('No separator filter', qd_noseparator, qd)
    print_filter_comparison('No year format filter', qd_noyearformat, qd)
    print_filter_comparison('No language filter', qd_nolanguage, qd)
    print()
    
    # Overall impact
    print('Overall Filter Impact:')
    print('-' * 80)
    if qd_all_off > qd:
        total_improvement = ((qd_all_off - qd) / qd_all_off) * 100
        total_speedup = qd_all_off / qd
        print('  All filters enabled:      %.6f sec' % qd)
        print('  All filters disabled:    %.6f sec' % qd_all_off)
        print('  Total improvement:       %.2f%% faster (%.2fX speedup)' % (total_improvement, total_speedup))
    else:
        total_overhead = ((qd - qd_all_off) / qd) * 100
        total_slowdown = qd / qd_all_off
        print('  All filters enabled:      %.6f sec' % qd)
        print('  All filters disabled:    %.6f sec' % qd_all_off)
        print('  Total overhead:          %.2f%% slower (%.2fX slowdown)' % (total_overhead, total_slowdown))
    print()
    
    # Summary table
    print('Summary Table:')
    print('-' * 80)
    print('  Configuration                    | Time (sec) | Speedup vs Baseline')
    print('  ' + '-' * 76)
    print('  All filters enabled (default)   | %10.6f | %.2fX' % (qd, qd_all_off / qd))
    print('  No prefix filter                 | %10.6f | %.2fX' % (qd_nopref, qd_all_off / qd_nopref))
    print('  No charset filter                | %10.6f | %.2fX' % (qd_nocharset, qd_all_off / qd_nocharset))
    print('  No separator filter              | %10.6f | %.2fX' % (qd_noseparator, qd_all_off / qd_noseparator))
    print('  No year format filter            | %10.6f | %.2fX' % (qd_noyearformat, qd_all_off / qd_noyearformat))
    print('  No language filter               | %10.6f | %.2fX' % (qd_nolanguage, qd_all_off / qd_nolanguage))
    print('  All filters disabled (baseline)  | %10.6f | 1.00X' % qd_all_off)
    print()
    
    # Library comparison table (sorted by time)
    print('Detailed Performance Comparison Table:')
    print('-' * 80)
    print('  Rank | Library              | Time (sec) | vs qddate        | Time difference')
    print('  ' + '-' * 76)
    
    # Rebuild sorted list for table
    libs_for_table = [('qddate (all filters)', qd)]
    if dt_dateutil is not None:
        libs_for_table.append(('dateutil', dt_dateutil))
    if dt_arrow is not None:
        libs_for_table.append(('arrow', dt_arrow))
    if dt_pendulum is not None:
        libs_for_table.append(('pendulum', dt_pendulum))
    libs_for_table.append(('dateparser', dt))
    libs_for_table.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
    
    for rank, (name, time_val) in enumerate(libs_for_table, 1):
        if time_val is None:
            continue
        time_diff = time_val - qddate_time
        if time_val < qddate_time:
            comparison = '%.2fX faster' % (qddate_time / time_val)
        elif time_val > qddate_time:
            comparison = '%.2fX slower' % (time_val / qddate_time)
        else:
            comparison = 'same speed'
        
        if time_diff > 0:
            diff_str = '+%.6f sec' % time_diff
        elif time_diff < 0:
            diff_str = '%.6f sec' % time_diff
        else:
            diff_str = '0.000000 sec'
        
        marker = ' <-- qddate' if name == 'qddate (all filters)' else ''
        print('  %4d | %-20s | %10.6f | %-15s | %s%s' % 
              (rank, name, time_val, comparison, diff_str, marker))
    
    print('=' * 80)
    print()
    print('Note: Lower time is better. Comparisons show speed relative to qddate.')


if __name__ == "__main__":
    run()
    #compare()

