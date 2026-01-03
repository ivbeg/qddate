#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Performance profiling script for qddate library.

This script profiles the date parsing pipeline using cProfile and generates
detailed reports showing where time is spent in the codebase.
"""

import cProfile
import pstats
import io
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

# Add parent directory to path to import qddate
sys.path.insert(0, str(Path(__file__).parent.parent))

from qddate import DateParser
from qddate.dirty import matchPrefix

# Test data from benchmarks
TESTS = [
    '01.12.2009',
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
    '2 Июня 2015',
    '9 июля 2015 г.',
    'Fri 24 Jul 2015',
    '26 de julho de 2015',
    '17 de Junio de 2015',
    '28. Juli 2015',
    '23 июня 2015',
    '3 Июля, 2015',
    '7 August, 2015',
    'Wednesday 22 Apr 2015',
    '12-08-2015 - 09:00',
    '08 Jul, 2015',
    'August 10th, 2015',
    'junio 9, 2015',
    '9 Июля 2015 [11:23]',
]


def profile_function(func, *args, **kwargs):
    """Profile a single function call."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    return profiler, result


def profile_parse_operations(parser, test_cases, iterations=10):
    """Profile parse operations."""
    def run_parses():
        for _ in range(iterations):
            for text in test_cases:
                try:
                    parser.parse(text)
                except Exception:
                    # Continue profiling even if some parses fail
                    pass
    
    profiler = cProfile.Profile()
    profiler.enable()
    run_parses()
    profiler.disable()
    return profiler


def profile_match_operations(parser, test_cases, iterations=10):
    """Profile match operations."""
    def run_matches():
        for _ in range(iterations):
            for text in test_cases:
                try:
                    parser.match(text)
                except Exception:
                    # Continue profiling even if some matches fail
                    pass
    
    profiler = cProfile.Profile()
    profiler.enable()
    run_matches()
    profiler.disable()
    return profiler


def profile_match_prefix(test_cases, iterations=100):
    """Profile matchPrefix function."""
    def run_match_prefix():
        for _ in range(iterations):
            for text in test_cases:
                matchPrefix(text[:6] if len(text) > 6 else text)
    
    profiler = cProfile.Profile()
    profiler.enable()
    run_match_prefix()
    profiler.disable()
    return profiler


def profile_initialization(iterations=10):
    """Profile parser initialization."""
    def run_init():
        for _ in range(iterations):
            DateParser()
    
    profiler = cProfile.Profile()
    profiler.enable()
    run_init()
    profiler.disable()
    return profiler


def analyze_profile(profiler, top_n=20):
    """Analyze profile and return statistics."""
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    
    # Capture stats output
    output = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = output
    try:
        stats.print_stats(top_n)
    finally:
        sys.stdout = old_stdout
    stats_output = output.getvalue()
    
    # Get function statistics
    func_stats = []
    for func_name, (cc, nc, tt, ct, callers) in stats.stats.items():
        func_stats.append({
            'file': func_name[0],
            'line': func_name[1],
            'function': func_name[2],
            'calls': nc,
            'total_time': tt,
            'cumulative_time': ct,
            'per_call': tt / nc if nc > 0 else 0,
        })
    
    # Sort by cumulative time
    func_stats.sort(key=lambda x: x['cumulative_time'], reverse=True)
    
    return {
        'stats_text': stats_output,
        'top_functions': func_stats[:top_n],
        'total_calls': sum(f['calls'] for f in func_stats),
    }


def generate_report(profiles, output_dir='profile_results'):
    """Generate comprehensive profiling report."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate individual reports
    reports = {}
    for profile_name, profiler in profiles.items():
        analysis = analyze_profile(profiler, top_n=30)
        reports[profile_name] = analysis
        
        # Write text report
        report_file = output_path / f'{profile_name}_{timestamp}.txt'
        with open(report_file, 'w') as f:
            f.write(f"Profile Report: {profile_name}\n")
            f.write("=" * 80 + "\n\n")
            f.write(analysis['stats_text'])
        
        print(f"Generated report: {report_file}")
    
    # Generate JSON summary
    summary = {
        'timestamp': timestamp,
        'profiles': {}
    }
    
    for profile_name, analysis in reports.items():
        summary['profiles'][profile_name] = {
            'top_functions': analysis['top_functions'][:10],
            'total_calls': analysis['total_calls'],
        }
    
    summary_file = output_path / f'summary_{timestamp}.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Generated summary: {summary_file}")
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("PROFILING SUMMARY")
    print("=" * 80)
    for profile_name, analysis in reports.items():
        print(f"\n{profile_name}:")
        print(f"  Total calls: {analysis['total_calls']}")
        print(f"  Top 5 functions by cumulative time:")
        for i, func in enumerate(analysis['top_functions'][:5], 1):
            print(f"    {i}. {func['function']} ({func['file']}:{func['line']})")
            print(f"       Calls: {func['calls']}, Total: {func['total_time']:.4f}s, "
                  f"Cumulative: {func['cumulative_time']:.4f}s")
    
    return reports


def main():
    """Main profiling function."""
    print("Starting performance profiling...")
    print(f"Python version: {sys.version}")
    print(f"Test cases: {len(TESTS)}")
    
    profiles = {}
    
    # Profile initialization
    print("\n1. Profiling parser initialization...")
    profiles['initialization'] = profile_initialization(iterations=5)
    
    # Create parser once for other profiles
    print("2. Creating parser instance...")
    parser = DateParser()
    
    # Profile matchPrefix
    print("3. Profiling matchPrefix...")
    profiles['match_prefix'] = profile_match_prefix(TESTS, iterations=50)
    
    # Profile match operations
    print("4. Profiling match operations...")
    profiles['match'] = profile_match_operations(parser, TESTS, iterations=5)
    
    # Profile parse operations
    print("5. Profiling parse operations...")
    profiles['parse'] = profile_parse_operations(parser, TESTS, iterations=5)
    
    # Generate reports
    print("\n6. Generating reports...")
    reports = generate_report(profiles)
    
    # Analyze pyparsing vs Python code
    print("\n7. Analyzing pyparsing vs Python code split...")
    parse_analysis = reports['parse']
    pyparsing_time = 0
    python_time = 0
    
    for func in parse_analysis['top_functions']:
        if 'pyparsing' in func['file'].lower() or 'pyparsing' in func['function'].lower():
            pyparsing_time += func['cumulative_time']
        else:
            python_time += func['cumulative_time']
    
    total_time = pyparsing_time + python_time
    if total_time > 0:
        pyparsing_pct = (pyparsing_time / total_time) * 100
        python_pct = (python_time / total_time) * 100
        print(f"  Pyparsing: {pyparsing_pct:.1f}% ({pyparsing_time:.4f}s)")
        print(f"  Python code: {python_pct:.1f}% ({python_time:.4f}s)")
    
    print("\nProfiling complete!")


if __name__ == '__main__':
    main()

