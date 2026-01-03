#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extended benchmarking suite for qddate with detailed timing breakdowns
and memory profiling capabilities.
"""

import sys
import time
import json
import statistics
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qddate import DateParser
from benchmarks.bench import TESTS

try:
    from memory_profiler import profile
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    print("Warning: memory_profiler not available. Install with: pip install memory-profiler")


class TimingBreakdown:
    """Track timing breakdown for different operations."""
    
    def __init__(self):
        self.timings = defaultdict(list)
        self.counts = defaultdict(int)
    
    def add_timing(self, operation, duration):
        """Add a timing measurement."""
        self.timings[operation].append(duration)
        self.counts[operation] += 1
    
    def get_stats(self, operation):
        """Get statistics for an operation."""
        if operation not in self.timings:
            return None
        timings = self.timings[operation]
        return {
            'count': len(timings),
            'total': sum(timings),
            'mean': statistics.mean(timings),
            'median': statistics.median(timings),
            'min': min(timings),
            'max': max(timings),
            'stdev': statistics.stdev(timings) if len(timings) > 1 else 0,
        }
    
    def get_all_stats(self):
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self.timings.keys()}


def time_function(func, *args, **kwargs):
    """Time a function call."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


def benchmark_initialization(iterations=10):
    """Benchmark parser initialization."""
    timings = []
    for _ in range(iterations):
        _, duration = time_function(DateParser)
        timings.append(duration)
    
    return {
        'operation': 'initialization',
        'iterations': iterations,
        'total_time': sum(timings),
        'mean_time': statistics.mean(timings),
        'median_time': statistics.median(timings),
        'min_time': min(timings),
        'max_time': max(timings),
    }


def benchmark_parse_operations(parser, test_cases, iterations=10):
    """Benchmark parse operations with detailed breakdown."""
    breakdown = TimingBreakdown()
    successful_parses = 0
    failed_parses = 0
    
    for iteration in range(iterations):
        for text in test_cases:
            result, duration = time_function(parser.parse, text)
            breakdown.add_timing('parse', duration)
            
            if result is not None:
                successful_parses += 1
                breakdown.add_timing('parse_success', duration)
            else:
                failed_parses += 1
                breakdown.add_timing('parse_failure', duration)
    
    stats = breakdown.get_all_stats()
    return {
        'operation': 'parse',
        'iterations': iterations,
        'test_cases': len(test_cases),
        'total_operations': iterations * len(test_cases),
        'successful': successful_parses,
        'failed': failed_parses,
        'success_rate': successful_parses / (iterations * len(test_cases)) if iterations * len(test_cases) > 0 else 0,
        'stats': stats,
    }


def benchmark_match_operations(parser, test_cases, iterations=10):
    """Benchmark match operations with detailed breakdown."""
    breakdown = TimingBreakdown()
    successful_matches = 0
    failed_matches = 0
    
    for iteration in range(iterations):
        for text in test_cases:
            result, duration = time_function(parser.match, text)
            breakdown.add_timing('match', duration)
            
            if result is not None:
                successful_matches += 1
                breakdown.add_timing('match_success', duration)
            else:
                failed_matches += 1
                breakdown.add_timing('match_failure', duration)
    
    stats = breakdown.get_all_stats()
    return {
        'operation': 'match',
        'iterations': iterations,
        'test_cases': len(test_cases),
        'total_operations': iterations * len(test_cases),
        'successful': successful_matches,
        'failed': failed_matches,
        'success_rate': successful_matches / (iterations * len(test_cases)) if iterations * len(test_cases) > 0 else 0,
        'stats': stats,
    }


def benchmark_match_prefix(test_cases, iterations=100):
    """Benchmark matchPrefix function."""
    from qddate.dirty import matchPrefix
    
    breakdown = TimingBreakdown()
    
    for iteration in range(iterations):
        for text in test_cases:
            prefix = text[:6] if len(text) > 6 else text
            _, duration = time_function(matchPrefix, prefix)
            breakdown.add_timing('match_prefix', duration)
    
    stats = breakdown.get_all_stats()
    return {
        'operation': 'match_prefix',
        'iterations': iterations,
        'test_cases': len(test_cases),
        'total_operations': iterations * len(test_cases),
        'stats': stats,
    }


def benchmark_with_prefix_vs_without(parser, test_cases, iterations=10):
    """Compare performance with and without prefix matching."""
    breakdown = TimingBreakdown()
    
    # With prefix
    for iteration in range(iterations):
        for text in test_cases:
            _, duration = time_function(parser.parse, text, noprefix=False)
            breakdown.add_timing('with_prefix', duration)
    
    # Without prefix
    for iteration in range(iterations):
        for text in test_cases:
            _, duration = time_function(parser.parse, text, noprefix=True)
            breakdown.add_timing('without_prefix', duration)
    
    stats = breakdown.get_all_stats()
    
    with_prefix_mean = stats.get('with_prefix', {}).get('mean', 0)
    without_prefix_mean = stats.get('without_prefix', {}).get('mean', 0)
    
    speedup = without_prefix_mean / with_prefix_mean if with_prefix_mean > 0 else 0
    
    return {
        'operation': 'prefix_comparison',
        'iterations': iterations,
        'test_cases': len(test_cases),
        'with_prefix': stats.get('with_prefix'),
        'without_prefix': stats.get('without_prefix'),
        'speedup_factor': speedup,
        'prefix_improvement': f"{(speedup - 1) * 100:.1f}%" if speedup > 1 else "N/A",
    }


@profile
def benchmark_memory_usage(parser, test_cases, iterations=5):
    """Benchmark memory usage (requires memory_profiler)."""
    if not MEMORY_PROFILER_AVAILABLE:
        return None
    
    results = []
    for iteration in range(iterations):
        for text in test_cases:
            result = parser.parse(text)
            results.append(result)
    return results


def run_all_benchmarks(iterations=10, prefix_iterations=50):
    """Run all benchmarks and return results."""
    print("=" * 80)
    print("QDDate Performance Benchmark Suite")
    print("=" * 80)
    print(f"Python version: {sys.version}")
    print(f"Test cases: {len(TESTS)}")
    print(f"Iterations: {iterations}")
    print()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'test_cases_count': len(TESTS),
        'iterations': iterations,
    }
    
    # Benchmark initialization
    print("1. Benchmarking parser initialization...")
    init_results = benchmark_initialization(iterations=5)
    results['initialization'] = init_results
    print(f"   Mean initialization time: {init_results['mean_time']*1000:.2f}ms")
    print()
    
    # Create parser
    print("2. Creating parser instance...")
    parser = DateParser()
    print("   Parser created successfully")
    print()
    
    # Benchmark matchPrefix
    print("3. Benchmarking matchPrefix...")
    prefix_results = benchmark_match_prefix(TESTS, iterations=prefix_iterations)
    results['match_prefix'] = prefix_results
    prefix_stats = prefix_results['stats'].get('match_prefix', {})
    print(f"   Mean time per call: {prefix_stats.get('mean', 0)*1000000:.2f}μs")
    print(f"   Total operations: {prefix_results['total_operations']}")
    print()
    
    # Benchmark match operations
    print("4. Benchmarking match operations...")
    match_results = benchmark_match_operations(parser, TESTS, iterations=iterations)
    results['match'] = match_results
    match_stats = match_results['stats'].get('match', {})
    print(f"   Mean time per match: {match_stats.get('mean', 0)*1000:.2f}ms")
    print(f"   Success rate: {match_results['success_rate']*100:.1f}%")
    print(f"   Successful: {match_results['successful']}, Failed: {match_results['failed']}")
    print()
    
    # Benchmark parse operations
    print("5. Benchmarking parse operations...")
    parse_results = benchmark_parse_operations(parser, TESTS, iterations=iterations)
    results['parse'] = parse_results
    parse_stats = parse_results['stats'].get('parse', {})
    print(f"   Mean time per parse: {parse_stats.get('mean', 0)*1000:.2f}ms")
    print(f"   Success rate: {parse_results['success_rate']*100:.1f}%")
    print(f"   Successful: {parse_results['successful']}, Failed: {parse_results['failed']}")
    print()
    
    # Compare with/without prefix
    print("6. Comparing with/without prefix matching...")
    prefix_comp = benchmark_with_prefix_vs_without(parser, TESTS, iterations=iterations)
    results['prefix_comparison'] = prefix_comp
    print(f"   With prefix mean: {prefix_comp['with_prefix']['mean']*1000:.2f}ms")
    print(f"   Without prefix mean: {prefix_comp['without_prefix']['mean']*1000:.2f}ms")
    print(f"   Speedup factor: {prefix_comp['speedup_factor']:.2f}x")
    print()
    
    return results


def save_results(results, output_dir='benchmark_results'):
    """Save benchmark results to JSON and CSV."""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON
    json_file = output_path / f'benchmark_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {json_file}")
    
    # Generate CSV summary
    csv_file = output_path / f'benchmark_summary_{timestamp}.csv'
    with open(csv_file, 'w') as f:
        f.write("Operation,Metric,Value\n")
        
        if 'initialization' in results:
            init = results['initialization']
            f.write(f"initialization,mean_time_ms,{init['mean_time']*1000:.4f}\n")
        
        if 'parse' in results:
            parse = results['parse']
            parse_stats = parse['stats'].get('parse', {})
            f.write(f"parse,mean_time_ms,{parse_stats.get('mean', 0)*1000:.4f}\n")
            f.write(f"parse,success_rate,{parse['success_rate']:.4f}\n")
        
        if 'match' in results:
            match = results['match']
            match_stats = match['stats'].get('match', {})
            f.write(f"match,mean_time_ms,{match_stats.get('mean', 0)*1000:.4f}\n")
            f.write(f"match,success_rate,{match['success_rate']:.4f}\n")
        
        if 'prefix_comparison' in results:
            pc = results['prefix_comparison']
            f.write(f"prefix_comparison,speedup_factor,{pc['speedup_factor']:.4f}\n")
    
    print(f"Summary saved to: {csv_file}")
    
    return json_file, csv_file


def main():
    """Main benchmark function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run qddate performance benchmarks')
    parser.add_argument('--iterations', type=int, default=10,
                       help='Number of iterations for parse/match benchmarks')
    parser.add_argument('--prefix-iterations', type=int, default=50,
                       help='Number of iterations for prefix benchmark')
    parser.add_argument('--output-dir', type=str, default='benchmark_results',
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    results = run_all_benchmarks(
        iterations=args.iterations,
        prefix_iterations=args.prefix_iterations
    )
    
    save_results(results, output_dir=args.output_dir)
    
    print("\n" + "=" * 80)
    print("Benchmarking complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

