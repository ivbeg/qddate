#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark packrat parsing impact on qddate performance.
"""

import sys
import time
import statistics
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from qddate import DateParser

# Test cases
TESTS = [
    '01.12.2009',
    '2013-01-12',
    '31.05.2001',
    '7/12/2009',
    '6 Jan 2009',
    'Jan 8, 1098',
    '16 May 2009 14:10',
    '01.03.2009 14:53:12',
    'Thursday 4 April 2019',
    'July 01, 2015',
    'Fri, 3 July 2015',
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


def benchmark_parse(parser, test_cases, iterations=10):
    """Benchmark parse operations."""
    timings = []
    for iteration in range(iterations):
        start = time.perf_counter()
        for text in test_cases:
            parser.parse(text)
        duration = time.perf_counter() - start
        timings.append(duration / len(test_cases))
    return timings


def main():
    """Main benchmark function."""
    print("=" * 80)
    print("Packrat Parsing Benchmark")
    print("=" * 80)
    
    # Test with packrat (default)
    print("\n1. Testing WITH packrat parsing (default)...")
    try:
        from pyparsing import ParserElement
        ParserElement.enable_packrat()
        print("   Packrat enabled")
    except Exception as e:
        print(f"   Warning: Could not enable packrat: {e}")
    
    parser_with = DateParser()
    timings_with = benchmark_parse(parser_with, TESTS, iterations=20)
    mean_with = statistics.mean(timings_with)
    print(f"   Mean time per parse: {mean_with*1000:.4f}ms")
    print(f"   Median: {statistics.median(timings_with)*1000:.4f}ms")
    print(f"   Min: {min(timings_with)*1000:.4f}ms")
    print(f"   Max: {max(timings_with)*1000:.4f}ms")
    
    # Test without packrat (if possible)
    print("\n2. Testing WITHOUT packrat parsing...")
    packrat_can_disable = False
    try:
        from pyparsing import ParserElement
        if hasattr(ParserElement, 'disable_packrat'):
            ParserElement.disable_packrat()
            packrat_can_disable = True
            print("   Packrat disabled")
        else:
            print("   Note: This version of pyparsing does not support disabling packrat")
            print("   Packrat is permanently enabled once activated")
            packrat_can_disable = False
    except Exception as e:
        print(f"   Warning: Could not disable packrat: {e}")
        packrat_can_disable = False
    
    if not packrat_can_disable:
        print("\n   Packrat parsing is enabled and cannot be disabled in this pyparsing version.")
        print("   This is expected behavior - packrat provides memoization for better performance.")
        print("   The benchmark above shows performance WITH packrat enabled.")
        return
    
    # Clear any caches by creating new parser
    parser_without = DateParser()
    timings_without = benchmark_parse(parser_without, TESTS, iterations=20)
    mean_without = statistics.mean(timings_without)
    print(f"   Mean time per parse: {mean_without*1000:.4f}ms")
    print(f"   Median: {statistics.median(timings_without)*1000:.4f}ms")
    print(f"   Min: {min(timings_without)*1000:.4f}ms")
    print(f"   Max: {max(timings_without)*1000:.4f}ms")
    
    # Compare
    print("\n3. Comparison:")
    if mean_without > 0:
        speedup = mean_without / mean_with
        improvement = ((mean_without - mean_with) / mean_without) * 100
        print(f"   Speedup factor: {speedup:.3f}x")
        print(f"   Improvement: {improvement:.1f}%")
        
        if speedup > 1:
            print(f"   ✓ Packrat provides {speedup:.1f}x speedup")
        elif speedup < 1:
            print(f"   ⚠ Packrat is {1/speedup:.1f}x slower (may vary by pattern complexity)")
        else:
            print(f"   ≈ Packrat has minimal impact")
    else:
        print("   Could not calculate comparison")
    
    # Re-enable packrat for future use
    try:
        from pyparsing import ParserElement
        ParserElement.enable_packrat()
    except:
        pass
    
    print("\n" + "=" * 80)
    print("Benchmark complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

