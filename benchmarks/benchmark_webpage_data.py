#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark script for comparing qddate with other datetime parsing libraries
using real-world webpage text data.

This script:
1. Reads text snippets from webpage_test_data.csv
2. Tests each library (qddate, dateparser, dateutil) on all texts
3. Measures success rate and performance (timing)
4. Outputs results in JSON and text formats
"""

import sys
import os
import csv
import json
import time
import statistics
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any


# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qddate import DateParser

# External library imports
try:
    import dateparser
    DATEPARSER_AVAILABLE = True
except ImportError:
    DATEPARSER_AVAILABLE = False

try:
    from dateutil import parser as dateutil_parser
    DATEUTIL_AVAILABLE = True
except ImportError:
    DATEUTIL_AVAILABLE = False


try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback: create a no-op tqdm-like class
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None, unit=None, disable=False):
            self.iterable = iterable if iterable is not None else []
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            return False
        
        def __iter__(self):
            return iter(self.iterable)


def time_function(func, *args, **kwargs) -> Tuple[Any, float]:
    """Time a function call and return result and duration."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


def load_csv_data(csv_path: str) -> Tuple[List[str], Dict[str, bool]]:
    """
    Load text snippets from CSV file along with qddate match information.
    
    :param csv_path: Path to CSV file
    :return: Tuple of (list of text strings, dict mapping text to whether qddate matched it)
    """
    texts = []
    qddate_matched = {}  # Track which texts qddate originally matched
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row.get('text', '').strip()
            if text:  # Only include non-empty texts
                texts.append(text)
                # Check if qddate matched this text (pattern_key is not empty)
                pattern_key = row.get('pattern_key', '').strip()
                qddate_matched[text] = bool(pattern_key)
    
    return texts, qddate_matched


def benchmark_qddate(texts: List[str], qddate_matched: Dict[str, bool], show_progress: bool = False) -> Dict[str, Any]:
    """Benchmark qddate library."""
    parser = DateParser()
    timings = []
    successful = 0
    failed = 0
    errors = 0
    matched_texts = []  # Store all successfully matched texts
    
    total_start = time.perf_counter()
    
    iterable = tqdm(texts, desc="qddate", disable=not show_progress) if TQDM_AVAILABLE and show_progress else texts
    
    for text in iterable:
        try:
            result, duration = time_function(parser.parse, text)
            timings.append(duration)
            if result is not None:
                successful += 1
                matched_texts.append(text)
            else:
                failed += 1
        except Exception:
            errors += 1
            timings.append(0.0)
            failed += 1
    
    total_time = time.perf_counter() - total_start
    total_operations = len(texts)
    
    # For qddate, false positives are texts that matched but weren't in original CSV matches
    # False negatives are texts that were in CSV matches but didn't match in this run
    matched_texts_set = set(matched_texts)
    false_positives = sum(1 for text in matched_texts if not qddate_matched.get(text, False))
    false_negatives = sum(1 for text in texts if qddate_matched.get(text, False) and text not in matched_texts_set)
    true_positives = successful - false_positives
    not_matched = total_operations - successful
    
    # FAR (False Acceptance Rate): rate of false positives
    far = false_positives / total_operations if total_operations > 0 else 0
    # FRR (False Rejection Rate): rate of false negatives
    frr = false_negatives / total_operations if total_operations > 0 else 0
    
    return {
        'library': 'qddate',
        'total_time': total_time,
        'total_operations': total_operations,
        'successful': successful,
        'not_matched': not_matched,
        'errors': errors,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'true_positives': true_positives,
        'far': far,
        'frr': frr,
        'success_rate': successful / total_operations if total_operations > 0 else 0,
        'mean_time': statistics.mean(timings) if timings else 0,
        'median_time': statistics.median(timings) if timings else 0,
        'min_time': min(timings) if timings else 0,
        'max_time': max(timings) if timings else 0,
        'p95_time': _percentile(timings, 0.95) if timings else 0,
        'p99_time': _percentile(timings, 0.99) if timings else 0,
        'throughput': total_operations / total_time if total_time > 0 else 0,
        'matched_texts': matched_texts,
    }


def benchmark_dateparser(texts: List[str], qddate_matched: Dict[str, bool], show_progress: bool = False) -> Dict[str, Any]:
    """Benchmark dateparser library."""
    if not DATEPARSER_AVAILABLE:
        return {'error': 'dateparser not available'}
    
    timings = []
    successful = 0
    failed = 0
    errors = 0
    matched_texts = []  # Store all successfully matched texts
    
    total_start = time.perf_counter()
    
    iterable = tqdm(texts, desc="dateparser", disable=not show_progress) if TQDM_AVAILABLE and show_progress else texts
    
    for text in iterable:
        try:
            result, duration = time_function(dateparser.parse, text)
            timings.append(duration)
            if result is not None:
                successful += 1
                matched_texts.append(text)
            else:
                failed += 1
        except Exception:
            errors += 1
            timings.append(0.0)
            failed += 1
    
    total_time = time.perf_counter() - total_start
    total_operations = len(texts)
    
    # False positives: texts that matched but qddate didn't match (likely not dates)
    # False negatives: texts that qddate matched but this library didn't match
    matched_texts_set = set(matched_texts)
    false_positives = sum(1 for text in matched_texts if not qddate_matched.get(text, False))
    false_negatives = sum(1 for text in texts if qddate_matched.get(text, False) and text not in matched_texts_set)
    true_positives = successful - false_positives
    not_matched = total_operations - successful
    
    # FAR (False Acceptance Rate): rate of false positives
    far = false_positives / total_operations if total_operations > 0 else 0
    # FRR (False Rejection Rate): rate of false negatives
    frr = false_negatives / total_operations if total_operations > 0 else 0
    
    return {
        'library': 'dateparser',
        'total_time': total_time,
        'total_operations': total_operations,
        'successful': successful,
        'not_matched': not_matched,
        'errors': errors,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'true_positives': true_positives,
        'far': far,
        'frr': frr,
        'success_rate': successful / total_operations if total_operations > 0 else 0,
        'mean_time': statistics.mean(timings) if timings else 0,
        'median_time': statistics.median(timings) if timings else 0,
        'min_time': min(timings) if timings else 0,
        'max_time': max(timings) if timings else 0,
        'p95_time': _percentile(timings, 0.95) if timings else 0,
        'p99_time': _percentile(timings, 0.99) if timings else 0,
        'throughput': total_operations / total_time if total_time > 0 else 0,
        'matched_texts': matched_texts,
    }


def benchmark_dateutil(texts: List[str], qddate_matched: Dict[str, bool], show_progress: bool = False) -> Dict[str, Any]:
    """Benchmark dateutil library."""
    if not DATEUTIL_AVAILABLE:
        return {'error': 'dateutil not available'}
    
    timings = []
    successful = 0
    failed = 0
    errors = 0
    matched_texts = []  # Store all successfully matched texts
    
    total_start = time.perf_counter()
    
    iterable = tqdm(texts, desc="dateutil", disable=not show_progress) if TQDM_AVAILABLE and show_progress else texts
    
    for text in iterable:
        try:
            result, duration = time_function(dateutil_parser.parse, text)
            timings.append(duration)
            if result is not None:
                successful += 1
                matched_texts.append(text)
            else:
                failed += 1
        except (ValueError, TypeError, AttributeError):
            errors += 1
            timings.append(0.0)
            failed += 1
        except Exception:
            errors += 1
            timings.append(0.0)
            failed += 1
    
    total_time = time.perf_counter() - total_start
    total_operations = len(texts)
    
    # False positives: texts that matched but qddate didn't match (likely not dates)
    # False negatives: texts that qddate matched but this library didn't match
    matched_texts_set = set(matched_texts)
    false_positives = sum(1 for text in matched_texts if not qddate_matched.get(text, False))
    false_negatives = sum(1 for text in texts if qddate_matched.get(text, False) and text not in matched_texts_set)
    true_positives = successful - false_positives
    not_matched = total_operations - successful
    
    # FAR (False Acceptance Rate): rate of false positives
    far = false_positives / total_operations if total_operations > 0 else 0
    # FRR (False Rejection Rate): rate of false negatives
    frr = false_negatives / total_operations if total_operations > 0 else 0
    
    return {
        'library': 'dateutil',
        'total_time': total_time,
        'total_operations': total_operations,
        'successful': successful,
        'not_matched': not_matched,
        'errors': errors,
        'false_positives': false_positives,
        'false_negatives': false_negatives,
        'true_positives': true_positives,
        'far': far,
        'frr': frr,
        'success_rate': successful / total_operations if total_operations > 0 else 0,
        'mean_time': statistics.mean(timings) if timings else 0,
        'median_time': statistics.median(timings) if timings else 0,
        'min_time': min(timings) if timings else 0,
        'max_time': max(timings) if timings else 0,
        'p95_time': _percentile(timings, 0.95) if timings else 0,
        'p99_time': _percentile(timings, 0.99) if timings else 0,
        'throughput': total_operations / total_time if total_time > 0 else 0,
        'matched_texts': matched_texts,
    }


def _percentile(data: List[float], p: float) -> float:
    """Calculate percentile."""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * p
    f = int(k)
    c = k - f
    if f + 1 < len(sorted_data):
        return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
    return sorted_data[f]


def run_all_benchmarks(csv_path: str, show_progress: bool = False) -> Dict[str, Any]:
    """Run benchmarks for all libraries."""
    print(f"Loading text data from {csv_path}...")
    texts, qddate_matched = load_csv_data(csv_path)
    print(f"Loaded {len(texts)} text snippets")
    print(f"qddate matched {sum(1 for v in qddate_matched.values() if v)} texts in original CSV")
    print()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'test_cases_count': len(texts),
        'libraries': {}
    }
    
    # Benchmark each library
    print("Running benchmarks...")
    print("=" * 80)
    
    # qddate
    print("Benchmarking qddate...")
    results['libraries']['qddate'] = benchmark_qddate(texts, qddate_matched, show_progress)
    
    # dateparser
    print("Benchmarking dateparser...")
    results['libraries']['dateparser'] = benchmark_dateparser(texts, qddate_matched, show_progress)
    
    # dateutil
    print("Benchmarking dateutil...")
    results['libraries']['dateutil'] = benchmark_dateutil(texts, qddate_matched, show_progress)
    
    print("=" * 80)
    print()
    
    return results


def print_results(results: Dict[str, Any]):
    """Print results in human-readable format."""
    print("=" * 80)
    print("WEBPAGE DATA BENCHMARK RESULTS")
    print("=" * 80)
    print(f"Test cases: {results['test_cases_count']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Python: {results['python_version'].split()[0]}")
    print()
    
    # Prepare table data
    table_data = []
    for lib_name, lib_results in results['libraries'].items():
        if 'error' in lib_results:
            continue
        table_data.append({
            'library': lib_name,
            'far': lib_results.get('far', 0),
            'frr': lib_results.get('frr', 0),
            'successful': lib_results['successful'],
            'not_matched': lib_results.get('not_matched', lib_results.get('failed', 0)),
            'false_positives': lib_results.get('false_positives', 0),
            'false_negatives': lib_results.get('false_negatives', 0),
            'total_time': lib_results['total_time'],
            'mean_time': lib_results['mean_time'],
            'median_time': lib_results['median_time'],
            'p95_time': lib_results['p95_time'],
            'throughput': lib_results['throughput'],
        })
    
    # Sort by FAR (ascending) - lower is better, then by FRR (ascending)
    table_data.sort(key=lambda x: (x['far'], x['frr']))
    
    # Print header
    print(f"{'Library':<15} {'FAR':<12} {'FRR':<12} {'False Pos.':<12} {'False Neg.':<12} "
          f"{'Matched':<12} {'Not Matched':<12} {'Total Time (s)':<15} {'Mean (ms)':<12} {'Median (ms)':<12} {'P95 (ms)':<12} "
          f"{'Throughput (ops/s)':<18}")
    print("-" * 160)
    
    # Print rows
    for row in table_data:
        print(f"{row['library']:<15} "
              f"{row['far']*100:>6.3f}%     "
              f"{row['frr']*100:>6.3f}%     "
              f"{row.get('false_positives', 0):<12} "
              f"{row.get('false_negatives', 0):<12} "
              f"{row['successful']:<12} "
              f"{row['not_matched']:<12} "
              f"{row['total_time']:>12.3f}     "
              f"{row['mean_time']*1000:>9.3f}   "
              f"{row['median_time']*1000:>9.3f}   "
              f"{row['p95_time']*1000:>9.3f}   "
              f"{row['throughput']:>15.1f}")
    
    print()
    
    # Print detailed error information
    print("Library Availability:")
    for lib_name, lib_results in results['libraries'].items():
        if 'error' in lib_results:
            print(f"  {lib_name}: {lib_results['error']}")
        else:
            print(f"  {lib_name}: available")
    
    print()


def save_results_json(results: Dict[str, Any], output_path: str):
    """Save results to JSON file."""
    # Convert to JSON-serializable format
    json_results = json.loads(json.dumps(results, default=str))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to {output_path}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Benchmark qddate against other datetime parsing libraries using webpage data'
    )
    parser.add_argument(
        '--csv',
        default='webpage_test_data.csv',
        help='Path to CSV file with test data (default: benchmarks/webpage_test_data.csv)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output JSON file path (default: benchmarks/results/webpage_benchmark_<timestamp>.json)'
    )
    parser.add_argument(
        '--progress',
        action='store_true',
        help='Show progress bars (requires tqdm)'
    )
    
    args = parser.parse_args()
    
    # Resolve CSV path
    csv_path = Path(args.csv)
    if not csv_path.is_absolute():
        csv_path = Path(__file__).parent / csv_path
    
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    # Run benchmarks
    results = run_all_benchmarks(str(csv_path), show_progress=args.progress)
    
    # Print results
    print_results(results)
    
    # Save JSON results
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = Path(__file__).parent / 'results'
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f'webpage_benchmark_{timestamp}.json'
    
    save_results_json(results, str(output_path))


if __name__ == '__main__':
    main()

