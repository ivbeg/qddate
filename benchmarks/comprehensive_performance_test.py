#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive performance test suite for qddate using test data from CSV.

This script loads all test cases from test_data.csv (~10,360 cases) and performs
extensive performance testing including:
- Timing metrics with percentiles
- Success rate analysis
- Pattern-specific performance breakdown
- Memory usage tracking
- Regression detection
- Statistical analysis
"""

import sys
import csv
import json
import time
import statistics
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from qddate import DateParser
from qddate.dirty import matchPrefix

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
    import arrow
    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

try:
    import pendulum
    PENDULUM_AVAILABLE = True
except ImportError:
    PENDULUM_AVAILABLE = False

try:
    import tracemalloc
    TRACEMALLOC_AVAILABLE = True
except ImportError:
    TRACEMALLOC_AVAILABLE = False

try:
    from memory_profiler import profile
    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    # Fallback: create a no-op tqdm-like class
    class tqdm:
        def __init__(self, iterable=None, desc=None, total=None, unit=None, disable=False):
            self.iterable = iterable if iterable is not None else []
            self.desc = desc or ""
            self.total = total
            self.unit = unit
            self.disable = disable
        
        def __enter__(self):
            return self
        
        def __exit__(self, *args):
            return False
        
        def __iter__(self):
            return iter(self.iterable)
        
        def update(self, n=1):
            pass
        
        def close(self):
            pass


class EnhancedTimingBreakdown:
    """Enhanced timing breakdown with percentiles and statistical analysis."""
    
    def __init__(self):
        self.timings = defaultdict(list)
        self.counts = defaultdict(int)
        self.metadata = defaultdict(dict)  # Store additional metadata per operation
    
    def add_timing(self, operation: str, duration: float, metadata: Optional[Dict] = None):
        """Add a timing measurement with optional metadata."""
        self.timings[operation].append(duration)
        self.counts[operation] += 1
        if metadata:
            idx = len(self.timings[operation]) - 1
            self.metadata[operation][idx] = metadata
    
    def _percentile(self, data: List[float], p: float) -> float:
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
    
    def get_stats(self, operation: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive statistics for an operation."""
        if operation not in self.timings or not self.timings[operation]:
            return None
        
        timings = self.timings[operation]
        sorted_timings = sorted(timings)
        
        return {
            'count': len(timings),
            'total': sum(timings),
            'mean': statistics.mean(timings),
            'median': statistics.median(timings),
            'min': min(timings),
            'max': max(timings),
            'stdev': statistics.stdev(timings) if len(timings) > 1 else 0,
            'p50': self._percentile(sorted_timings, 0.50),
            'p90': self._percentile(sorted_timings, 0.90),
            'p95': self._percentile(sorted_timings, 0.95),
            'p99': self._percentile(sorted_timings, 0.99),
            'coefficient_of_variation': (statistics.stdev(timings) / statistics.mean(timings)) 
                                        if len(timings) > 1 and statistics.mean(timings) > 0 else 0,
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all operations."""
        return {op: self.get_stats(op) for op in self.timings.keys()}
    
    def get_outliers(self, operation: str, threshold: float = 2.0) -> List[Tuple[int, float]]:
        """Identify outliers using z-score method."""
        if operation not in self.timings or len(self.timings[operation]) < 2:
            return []
        
        timings = self.timings[operation]
        mean = statistics.mean(timings)
        stdev = statistics.stdev(timings)
        
        if stdev == 0:
            return []
        
        outliers = []
        for idx, timing in enumerate(timings):
            z_score = abs((timing - mean) / stdev)
            if z_score > threshold:
                outliers.append((idx, timing))
        
        return outliers


def time_function(func, *args, **kwargs):
    """Time a function call."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


def load_test_data(csv_path: Path) -> List[Tuple[str, str]]:
    """Load test data from CSV file."""
    test_cases = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            date_string = row['date_string'].strip()
            pattern_key = row['pattern_key'].strip()
            # Handle quoted strings in CSV
            if date_string.startswith('"') and date_string.endswith('"'):
                date_string = date_string[1:-1]
            test_cases.append((date_string, pattern_key))
    
    return test_cases


def group_by_pattern(test_cases: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Group test cases by pattern_key."""
    grouped = defaultdict(list)
    for date_string, pattern_key in test_cases:
        grouped[pattern_key].append(date_string)
    return dict(grouped)


class InitializationPerformance:
    """Test parser initialization performance."""
    
    @staticmethod
    def benchmark(iterations: int = 10) -> Dict[str, Any]:
        """Benchmark parser initialization."""
        timings = []
        iter_range = tqdm(range(iterations), desc="Initialization", unit="iter", disable=not TQDM_AVAILABLE)
        for _ in iter_range:
            _, duration = time_function(DateParser)
            timings.append(duration)
        
        sorted_timings = sorted(timings)
        
        return {
            'operation': 'initialization',
            'iterations': iterations,
            'total_time': sum(timings),
            'mean': statistics.mean(timings),
            'median': statistics.median(timings),
            'min': min(timings),
            'max': max(timings),
            'stdev': statistics.stdev(timings) if len(timings) > 1 else 0,
            'p50': timings[len(timings) // 2] if timings else 0,
            'p90': timings[int(len(timings) * 0.9)] if timings else 0,
            'p95': timings[int(len(timings) * 0.95)] if timings else 0,
            'p99': timings[int(len(timings) * 0.99)] if timings else 0,
        }


class ParsePerformance:
    """Test parse operation performance."""
    
    @staticmethod
    def benchmark(parser: DateParser, test_cases: List[Tuple[str, str]], 
                  iterations: int = 1) -> Dict[str, Any]:
        """Benchmark parse operations with comprehensive metrics."""
        breakdown = EnhancedTimingBreakdown()
        successful_parses = 0
        failed_parses = 0
        pattern_stats = defaultdict(lambda: {'success': 0, 'fail': 0, 'timings': []})
        
        total_start = time.perf_counter()
        errors = 0
        
        total_ops = iterations * len(test_cases)
        pbar = tqdm(total=total_ops, desc="Parse operations", unit="ops", disable=not TQDM_AVAILABLE)
        
        for iteration in range(iterations):
            for date_string, pattern_key in test_cases:
                try:
                    result, duration = time_function(parser.parse, date_string)
                    breakdown.add_timing('parse', duration, {'pattern': pattern_key})
                    
                    pattern_stats[pattern_key]['timings'].append(duration)
                    
                    if result is not None:
                        successful_parses += 1
                        breakdown.add_timing('parse_success', duration)
                        pattern_stats[pattern_key]['success'] += 1
                    else:
                        failed_parses += 1
                        breakdown.add_timing('parse_failure', duration)
                        pattern_stats[pattern_key]['fail'] += 1
                except Exception:
                    errors += 1
                    # Still record timing for error cases (very fast)
                    breakdown.add_timing('parse_error', 0.0)
                    pattern_stats[pattern_key]['fail'] += 1
                pbar.update(1)
        
        pbar.close()
        total_time = time.perf_counter() - total_start
        total_operations = iterations * len(test_cases)
        
        # Calculate pattern-specific stats
        pattern_performance = {}
        for pattern_key, stats in pattern_stats.items():
            if stats['timings']:
                pattern_performance[pattern_key] = {
                    'count': len(stats['timings']),
                    'success_rate': stats['success'] / (stats['success'] + stats['fail']) 
                                   if (stats['success'] + stats['fail']) > 0 else 0,
                    'mean_time': statistics.mean(stats['timings']),
                    'median_time': statistics.median(stats['timings']),
                    'success_count': stats['success'],
                    'fail_count': stats['fail'],
                }
        
        stats = breakdown.get_all_stats()
        
        return {
            'operation': 'parse',
            'iterations': iterations,
            'test_cases': len(test_cases),
            'total_operations': total_operations,
            'total_time': total_time,
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'successful': successful_parses,
            'failed': failed_parses,
            'errors': errors,
            'success_rate': successful_parses / total_operations if total_operations > 0 else 0,
            'stats': stats,
            'pattern_performance': pattern_performance,
        }


class MatchPerformance:
    """Test match operation performance."""
    
    @staticmethod
    def benchmark(parser: DateParser, test_cases: List[Tuple[str, str]], 
                  iterations: int = 1) -> Dict[str, Any]:
        """Benchmark match operations."""
        breakdown = EnhancedTimingBreakdown()
        successful_matches = 0
        failed_matches = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        total_ops = iterations * len(test_cases)
        pbar = tqdm(total=total_ops, desc="Match operations", unit="ops", disable=not TQDM_AVAILABLE)
        
        for iteration in range(iterations):
            for date_string, pattern_key in test_cases:
                try:
                    result, duration = time_function(parser.match, date_string)
                    breakdown.add_timing('match', duration)
                    
                    if result is not None:
                        successful_matches += 1
                        breakdown.add_timing('match_success', duration)
                    else:
                        failed_matches += 1
                        breakdown.add_timing('match_failure', duration)
                except Exception:
                    errors += 1
                    # Still record timing for error cases (very fast)
                    breakdown.add_timing('match_error', 0.0)
                pbar.update(1)
        
        pbar.close()
        total_time = time.perf_counter() - total_start
        total_operations = iterations * len(test_cases)
        
        stats = breakdown.get_all_stats()
        
        return {
            'operation': 'match',
            'iterations': iterations,
            'test_cases': len(test_cases),
            'total_operations': total_operations,
            'total_time': total_time,
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'successful': successful_matches,
            'failed': failed_matches,
            'errors': errors,
            'success_rate': successful_matches / total_operations if total_operations > 0 else 0,
            'stats': stats,
        }


class MatchPrefixPerformance:
    """Test matchPrefix function performance."""
    
    @staticmethod
    def benchmark(test_cases: List[Tuple[str, str]], iterations: int = 100) -> Dict[str, Any]:
        """Benchmark matchPrefix function."""
        breakdown = EnhancedTimingBreakdown()
        
        total_start = time.perf_counter()
        
        total_ops = iterations * len(test_cases)
        pbar = tqdm(total=total_ops, desc="MatchPrefix operations", unit="ops", disable=not TQDM_AVAILABLE)
        
        for iteration in range(iterations):
            for date_string, _ in test_cases:
                prefix = date_string[:6] if len(date_string) > 6 else date_string
                _, duration = time_function(matchPrefix, prefix)
                breakdown.add_timing('match_prefix', duration)
                pbar.update(1)
        
        pbar.close()
        
        total_time = time.perf_counter() - total_start
        total_operations = iterations * len(test_cases)
        
        stats = breakdown.get_all_stats()
        
        return {
            'operation': 'match_prefix',
            'iterations': iterations,
            'test_cases': len(test_cases),
            'total_operations': total_operations,
            'total_time': total_time,
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }


class BatchPerformance:
    """Test large batch processing efficiency."""
    
    @staticmethod
    def benchmark(parser: DateParser, test_cases: List[Tuple[str, str]], 
                  batch_sizes: List[int] = [100, 500, 1000, 5000]) -> Dict[str, Any]:
        """Benchmark batch processing with different batch sizes."""
        results = {}
        
        pbar = tqdm(batch_sizes, desc="Batch processing", unit="batch", disable=not TQDM_AVAILABLE)
        for batch_size in pbar:
            if batch_size > len(test_cases):
                continue
            
            pbar.set_description(f"Batch processing (size={batch_size})")
            batch = test_cases[:batch_size]
            start = time.perf_counter()
            
            for date_string, _ in batch:
                try:
                    parser.parse(date_string)
                except Exception:
                    pass  # Continue on errors
            
            duration = time.perf_counter() - start
            throughput = batch_size / duration if duration > 0 else 0
            
            results[f'batch_{batch_size}'] = {
                'batch_size': batch_size,
                'total_time': duration,
                'throughput': throughput,
                'time_per_item': duration / batch_size if batch_size > 0 else 0,
            }
        
        pbar.close()
        return {
            'operation': 'batch_processing',
            'results': results,
        }


class MemoryPerformance:
    """Test memory usage patterns."""
    
    @staticmethod
    def benchmark(parser: DateParser, test_cases: List[Tuple[str, str]], 
                  iterations: int = 1) -> Dict[str, Any]:
        """Benchmark memory usage."""
        if not TRACEMALLOC_AVAILABLE:
            return {'error': 'tracemalloc not available'}
        
        tracemalloc.start()
        
        # Initial snapshot
        snapshot1 = tracemalloc.take_snapshot()
        
        # Perform operations
        total_ops = iterations * len(test_cases)
        pbar = tqdm(total=total_ops, desc="Memory profiling", unit="ops", disable=not TQDM_AVAILABLE)
        
        for iteration in range(iterations):
            for date_string, _ in test_cases:
                try:
                    parser.parse(date_string)
                except Exception:
                    pass  # Continue on errors
                pbar.update(1)
        
        pbar.close()
        
        # Final snapshot
        snapshot2 = tracemalloc.take_snapshot()
        
        # Calculate difference
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        
        total_memory = sum(stat.size_diff for stat in top_stats)
        peak_memory = tracemalloc.get_traced_memory()[1]
        
        tracemalloc.stop()
        
        return {
            'operation': 'memory',
            'iterations': iterations,
            'test_cases': len(test_cases),
            'total_memory_diff': total_memory,
            'peak_memory': peak_memory,
            'memory_per_operation': total_memory / (iterations * len(test_cases)) 
                                   if (iterations * len(test_cases)) > 0 else 0,
        }


class PatternSpecificPerformance:
    """Analyze performance by pattern type."""
    
    @staticmethod
    def analyze(parse_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pattern-specific performance from parse results."""
        pattern_perf = parse_results.get('pattern_performance', {})
        
        if not pattern_perf:
            return {'error': 'No pattern performance data available'}
        
        # Find fastest and slowest patterns
        patterns_by_time = sorted(
            pattern_perf.items(),
            key=lambda x: x[1].get('mean_time', 0)
        )
        
        fastest = patterns_by_time[:10] if len(patterns_by_time) >= 10 else patterns_by_time
        slowest = patterns_by_time[-10:] if len(patterns_by_time) >= 10 else patterns_by_time
        
        # Calculate statistics
        mean_times = [p[1].get('mean_time', 0) for p in patterns_by_time]
        success_rates = [p[1].get('success_rate', 0) for p in patterns_by_time]
        
        return {
            'operation': 'pattern_analysis',
            'total_patterns': len(pattern_perf),
            'fastest_patterns': [
                {'pattern': p[0], 'mean_time': p[1].get('mean_time', 0),
                 'success_rate': p[1].get('success_rate', 0)}
                for p in fastest
            ],
            'slowest_patterns': [
                {'pattern': p[0], 'mean_time': p[1].get('mean_time', 0),
                 'success_rate': p[1].get('success_rate', 0)}
                for p in slowest
            ],
            'pattern_time_stats': {
                'mean': statistics.mean(mean_times) if mean_times else 0,
                'median': statistics.median(mean_times) if mean_times else 0,
                'min': min(mean_times) if mean_times else 0,
                'max': max(mean_times) if mean_times else 0,
            },
            'pattern_success_stats': {
                'mean': statistics.mean(success_rates) if success_rates else 0,
                'median': statistics.median(success_rates) if success_rates else 0,
                'min': min(success_rates) if success_rates else 0,
                'max': max(success_rates) if success_rates else 0,
            },
        }


class RegressionDetector:
    """Detect performance regressions by comparing against baseline."""
    
    @staticmethod
    def load_baseline(baseline_path: Path) -> Optional[Dict[str, Any]]:
        """Load baseline metrics from JSON file."""
        if not baseline_path.exists():
            return None
        
        try:
            with open(baseline_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load baseline: {e}")
            return None
    
    @staticmethod
    def compare(current: Dict[str, Any], baseline: Dict[str, Any], 
                threshold: float = 0.10) -> Dict[str, Any]:
        """Compare current results against baseline."""
        regressions = []
        improvements = []
        unchanged = []
        
        # Compare key metrics
        metrics_to_compare = [
            ('initialization', 'mean'),
            ('parse', 'stats', 'parse', 'mean'),
            ('match', 'stats', 'match', 'mean'),
            ('match_prefix', 'stats', 'match_prefix', 'mean'),
        ]
        
        for metric_path in metrics_to_compare:
            try:
                current_val = current
                baseline_val = baseline
                
                for key in metric_path:
                    if isinstance(current_val, dict):
                        current_val = current_val.get(key)
                    if isinstance(baseline_val, dict):
                        baseline_val = baseline_val.get(key)
                
                if current_val is None or baseline_val is None:
                    continue
                
                if baseline_val == 0:
                    continue
                
                change_pct = (current_val - baseline_val) / baseline_val
                metric_name = '.'.join(metric_path)
                
                if change_pct > threshold:
                    regressions.append({
                        'metric': metric_name,
                        'baseline': baseline_val,
                        'current': current_val,
                        'change_pct': change_pct * 100,
                    })
                elif change_pct < -threshold:
                    improvements.append({
                        'metric': metric_name,
                        'baseline': baseline_val,
                        'current': current_val,
                        'change_pct': change_pct * 100,
                    })
                else:
                    unchanged.append({
                        'metric': metric_name,
                        'baseline': baseline_val,
                        'current': current_val,
                        'change_pct': change_pct * 100,
                    })
            except (KeyError, TypeError):
                continue
        
        return {
            'regressions': regressions,
            'improvements': improvements,
            'unchanged': unchanged,
            'regression_count': len(regressions),
            'improvement_count': len(improvements),
        }


class StatisticalAnalyzer:
    """Perform statistical analysis on performance data."""
    
    @staticmethod
    def analyze(breakdown: EnhancedTimingBreakdown, operation: str) -> Dict[str, Any]:
        """Perform statistical analysis on timing data."""
        stats = breakdown.get_stats(operation)
        if not stats:
            return {}
        
        outliers = breakdown.get_outliers(operation, threshold=2.0)
        
        # Confidence interval calculation (95% CI)
        timings = breakdown.timings[operation]
        if len(timings) > 1:
            mean = stats['mean']
            stdev = stats['stdev']
            n = len(timings)
            # Using t-distribution approximation (z-score for large n)
            ci_95 = 1.96 * (stdev / (n ** 0.5)) if n > 0 else 0
            confidence_interval = {
                'lower': mean - ci_95,
                'upper': mean + ci_95,
                'level': 0.95,
            }
        else:
            confidence_interval = None
        
        return {
            'operation': operation,
            'basic_stats': stats,
            'outliers': {
                'count': len(outliers),
                'threshold': 2.0,
                'examples': outliers[:10],  # Top 10 outliers
            },
            'confidence_interval': confidence_interval,
        }


class LibraryComparison:
    """Compare qddate with different configurations against external libraries."""
    
    @staticmethod
    def benchmark_qddate(parser: DateParser, test_cases: List[str], 
                         config: str = 'default', **kwargs) -> Dict[str, Any]:
        """Benchmark qddate with specified configuration."""
        breakdown = EnhancedTimingBreakdown()
        successful = 0
        failed = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        for date_string in test_cases:
            try:
                result, duration = time_function(parser.parse, date_string, **kwargs)
                breakdown.add_timing('parse', duration)
                if result is not None:
                    successful += 1
                else:
                    failed += 1
            except Exception:
                errors += 1
                breakdown.add_timing('parse', 0.0)
                failed += 1
        
        total_time = time.perf_counter() - total_start
        total_operations = len(test_cases)
        stats = breakdown.get_all_stats()
        
        return {
            'library': f'qddate_{config}',
            'config': config,
            'total_time': total_time,
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': successful / total_operations if total_operations > 0 else 0,
            'mean_time': stats.get('parse', {}).get('mean', 0),
            'median_time': stats.get('parse', {}).get('median', 0),
            'p95_time': stats.get('parse', {}).get('p95', 0),
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }
    
    @staticmethod
    def benchmark_dateparser(test_cases: List[str]) -> Dict[str, Any]:
        """Benchmark dateparser library."""
        if not DATEPARSER_AVAILABLE:
            return {'error': 'dateparser not available'}
        
        breakdown = EnhancedTimingBreakdown()
        successful = 0
        failed = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        for date_string in test_cases:
            try:
                result, duration = time_function(dateparser.parse, date_string)
                breakdown.add_timing('parse', duration)
                if result is not None:
                    successful += 1
                else:
                    failed += 1
            except Exception:
                errors += 1
                breakdown.add_timing('parse', 0.0)
                failed += 1
        
        total_time = time.perf_counter() - total_start
        total_operations = len(test_cases)
        stats = breakdown.get_all_stats()
        
        return {
            'library': 'dateparser',
            'total_time': total_time,
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': successful / total_operations if total_operations > 0 else 0,
            'mean_time': stats.get('parse', {}).get('mean', 0),
            'median_time': stats.get('parse', {}).get('median', 0),
            'p95_time': stats.get('parse', {}).get('p95', 0),
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }
    
    @staticmethod
    def benchmark_dateutil(test_cases: List[str]) -> Dict[str, Any]:
        """Benchmark dateutil library."""
        if not DATEUTIL_AVAILABLE:
            return {'error': 'dateutil not available'}
        
        breakdown = EnhancedTimingBreakdown()
        successful = 0
        failed = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        for date_string in test_cases:
            try:
                result, duration = time_function(dateutil_parser.parse, date_string)
                breakdown.add_timing('parse', duration)
                if result is not None:
                    successful += 1
                else:
                    failed += 1
            except (ValueError, TypeError, AttributeError):
                errors += 1
                breakdown.add_timing('parse', 0.0)
                failed += 1
        
        total_time = time.perf_counter() - total_start
        total_operations = len(test_cases)
        stats = breakdown.get_all_stats()
        
        return {
            'library': 'dateutil',
            'total_time': total_time,
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': successful / total_operations if total_operations > 0 else 0,
            'mean_time': stats.get('parse', {}).get('mean', 0),
            'median_time': stats.get('parse', {}).get('median', 0),
            'p95_time': stats.get('parse', {}).get('p95', 0),
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }
    
    @staticmethod
    def benchmark_arrow(test_cases: List[str]) -> Dict[str, Any]:
        """Benchmark arrow library."""
        if not ARROW_AVAILABLE:
            return {'error': 'arrow not available'}
        
        breakdown = EnhancedTimingBreakdown()
        successful = 0
        failed = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        for date_string in test_cases:
            try:
                result, duration = time_function(arrow.get, date_string)
                if result is not None:
                    # Convert to datetime for consistency
                    _ = result.datetime
                    successful += 1
                else:
                    failed += 1
                breakdown.add_timing('parse', duration)
            except Exception:
                # Catch all exceptions (ValueError, TypeError, AttributeError, ParserError, etc.)
                errors += 1
                breakdown.add_timing('parse', 0.0)
                failed += 1
        
        total_time = time.perf_counter() - total_start
        total_operations = len(test_cases)
        stats = breakdown.get_all_stats()
        
        return {
            'library': 'arrow',
            'total_time': total_time,
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': successful / total_operations if total_operations > 0 else 0,
            'mean_time': stats.get('parse', {}).get('mean', 0),
            'median_time': stats.get('parse', {}).get('median', 0),
            'p95_time': stats.get('parse', {}).get('p95', 0),
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }
    
    @staticmethod
    def benchmark_pendulum(test_cases: List[str]) -> Dict[str, Any]:
        """Benchmark pendulum library."""
        if not PENDULUM_AVAILABLE:
            return {'error': 'pendulum not available'}
        
        breakdown = EnhancedTimingBreakdown()
        successful = 0
        failed = 0
        errors = 0
        
        total_start = time.perf_counter()
        
        for date_string in test_cases:
            try:
                result, duration = time_function(pendulum.parse, date_string)
                breakdown.add_timing('parse', duration)
                if result is not None:
                    successful += 1
                else:
                    failed += 1
            except (ValueError, TypeError, AttributeError):
                errors += 1
                breakdown.add_timing('parse', 0.0)
                failed += 1
        
        total_time = time.perf_counter() - total_start
        total_operations = len(test_cases)
        stats = breakdown.get_all_stats()
        
        return {
            'library': 'pendulum',
            'total_time': total_time,
            'total_operations': total_operations,
            'successful': successful,
            'failed': failed,
            'errors': errors,
            'success_rate': successful / total_operations if total_operations > 0 else 0,
            'mean_time': stats.get('parse', {}).get('mean', 0),
            'median_time': stats.get('parse', {}).get('median', 0),
            'p95_time': stats.get('parse', {}).get('p95', 0),
            'throughput': total_operations / total_time if total_time > 0 else 0,
            'stats': stats,
        }
    
    @staticmethod
    def run_all_comparisons(test_cases: List[Tuple[str, str]], 
                           iterations: int = 1) -> Dict[str, Any]:
        """Run benchmarks for all libraries and qddate configurations."""
        # Extract just the date strings
        date_strings = [ds for ds, _ in test_cases]
        
        if not date_strings:
            return {'error': 'No test cases provided'}
        
        print(f"Running library comparisons on {len(date_strings)} test cases...")
        results = {}
        
        # Create qddate parser
        parser = DateParser()
        
        # qddate with default configuration
        print("  Benchmarking qddate (default)...")
        results['qddate_default'] = LibraryComparison.benchmark_qddate(
            parser, date_strings, config='default'
        )
        
        # qddate with all filters off
        print("  Benchmarking qddate (all filters off)...")
        results['qddate_no_filters'] = LibraryComparison.benchmark_qddate(
            parser, date_strings, config='no_filters',
            noprefix=True, nocharsetfilter=True, noseparatorfilter=True,
            noyearformatfilter=True, nolanguagefilter=True
        )
        
        # qddate without prefix filter
        print("  Benchmarking qddate (no prefix filter)...")
        results['qddate_no_prefix'] = LibraryComparison.benchmark_qddate(
            parser, date_strings, config='no_prefix', noprefix=True
        )
        
        # dateparser
        print("  Benchmarking dateparser...")
        results['dateparser'] = LibraryComparison.benchmark_dateparser(date_strings)
        
        # dateutil
        print("  Benchmarking dateutil...")
        results['dateutil'] = LibraryComparison.benchmark_dateutil(date_strings)
        
        # arrow
        print("  Benchmarking arrow...")
        results['arrow'] = LibraryComparison.benchmark_arrow(date_strings)
        
        # pendulum
        print("  Benchmarking pendulum...")
        results['pendulum'] = LibraryComparison.benchmark_pendulum(date_strings)
        
        print("  Library comparisons complete!")
        return results
    
    @staticmethod
    def generate_comparison_table(results: Dict[str, Dict[str, Any]]) -> str:
        """Generate a formatted comparison table."""
        # Filter out errors
        valid_results = {k: v for k, v in results.items() if 'error' not in v}
        
        # Sort by total time
        sorted_results = sorted(
            valid_results.items(),
            key=lambda x: x[1].get('total_time', float('inf'))
        )
        
        # Get baseline (qddate default)
        baseline = valid_results.get('qddate_default', {})
        baseline_time = baseline.get('total_time', 1.0)
        baseline_success = baseline.get('success_rate', 0)
        
        lines = []
        lines.append("=" * 120)
        lines.append("Library Comparison Table")
        lines.append("=" * 120)
        lines.append(f"{'Rank':<5} {'Library':<25} {'Total Time':<12} {'Success Rate':<12} {'Mean Time':<12} {'vs qddate':<15} {'Throughput':<12}")
        lines.append("-" * 120)
        
        for rank, (key, result) in enumerate(sorted_results, 1):
            lib_name = result.get('library', key)
            # Improve formatting for qddate configs
            if lib_name.startswith('qddate_'):
                config_name = lib_name.replace('qddate_', 'qddate (')
                config_name = config_name.replace('_', ' ').replace('default', 'default)')
                config_name = config_name.replace('no filters', 'no filters)')
                config_name = config_name.replace('no prefix', 'no prefix)')
                lib_name = config_name
            
            total_time = result.get('total_time', 0)
            success_rate = result.get('success_rate', 0)
            mean_time = result.get('mean_time', 0)
            throughput = result.get('throughput', 0)
            
            # Calculate relative speed
            if baseline_time > 0:
                speed_ratio = total_time / baseline_time
                if speed_ratio < 1.0:
                    speed_str = f"{1.0/speed_ratio:.2f}X faster"
                elif speed_ratio > 1.0:
                    speed_str = f"{speed_ratio:.2f}X slower"
                else:
                    speed_str = "same"
            else:
                speed_str = "N/A"
            
            marker = " <-- baseline" if key == 'qddate_default' else ""
            
            lines.append(
                f"{rank:<5} {lib_name:<25} {total_time:>10.4f}s {success_rate:>11.1%} "
                f"{mean_time*1000:>10.3f}ms {speed_str:<15} {throughput:>10.0f} ops/s{marker}"
            )
        
        lines.append("=" * 120)
        lines.append(f"\nBaseline: qddate (default) - {baseline_time:.4f}s total, {baseline_success:.1%} success rate")
        lines.append("Note: Success rate shows percentage of test cases successfully parsed")
        lines.append("=" * 120)
        
        return "\n".join(lines)


def run_comprehensive_tests(csv_path: Path, iterations: int = 1, 
                           prefix_iterations: int = 50,
                           skip_memory: bool = False,
                           pattern_filter: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run comprehensive performance tests."""
    print("=" * 80)
    print("QDDate Comprehensive Performance Test Suite")
    print("=" * 80)
    print(f"Python version: {sys.version.split()[0]}")
    print(f"CSV file: {csv_path}")
    print(f"Iterations: {iterations}")
    print()
    
    # Load test data
    print("Loading test data from CSV...")
    test_cases = load_test_data(csv_path)
    print(f"Loaded {len(test_cases)} test cases")
    
    # Filter by pattern if specified
    if pattern_filter:
        test_cases = [(ds, pk) for ds, pk in test_cases if pk in pattern_filter]
        print(f"Filtered to {len(test_cases)} test cases matching patterns: {pattern_filter}")
    
    print()
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'python_version': sys.version,
        'test_cases_count': len(test_cases),
        'iterations': iterations,
        'prefix_iterations': prefix_iterations,
    }
    
    # 1. Initialization performance
    print("1. Benchmarking parser initialization...")
    init_results = InitializationPerformance.benchmark(iterations=5)
    results['initialization'] = init_results
    print(f"   Mean initialization time: {init_results['mean']*1000:.2f}ms")
    print()
    
    # 2. Create parser
    print("2. Creating parser instance...")
    parser = DateParser()
    print("   Parser created successfully")
    print()
    
    # 3. MatchPrefix performance
    print("3. Benchmarking matchPrefix...")
    prefix_results = MatchPrefixPerformance.benchmark(test_cases, iterations=prefix_iterations)
    results['match_prefix'] = prefix_results
    prefix_stats = prefix_results['stats'].get('match_prefix', {})
    print(f"   Mean time per call: {prefix_stats.get('mean', 0)*1000000:.2f}μs")
    print(f"   Throughput: {prefix_results['throughput']:.0f} ops/sec")
    print()
    
    # 4. Match performance
    print("4. Benchmarking match operations...")
    match_results = MatchPerformance.benchmark(parser, test_cases, iterations=iterations)
    results['match'] = match_results
    match_stats = match_results['stats'].get('match', {})
    print(f"   Mean time per match: {match_stats.get('mean', 0)*1000:.2f}ms")
    print(f"   P95: {match_stats.get('p95', 0)*1000:.2f}ms")
    print(f"   Success rate: {match_results['success_rate']*100:.1f}%")
    print(f"   Throughput: {match_results['throughput']:.0f} ops/sec")
    if match_results.get('errors', 0) > 0:
        print(f"   Errors: {match_results['errors']}")
    print()
    
    # 5. Parse performance
    print("5. Benchmarking parse operations...")
    parse_results = ParsePerformance.benchmark(parser, test_cases, iterations=iterations)
    results['parse'] = parse_results
    parse_stats = parse_results['stats'].get('parse', {})
    print(f"   Mean time per parse: {parse_stats.get('mean', 0)*1000:.2f}ms")
    print(f"   P95: {parse_stats.get('p95', 0)*1000:.2f}ms")
    print(f"   Success rate: {parse_results['success_rate']*100:.1f}%")
    print(f"   Throughput: {parse_results['throughput']:.0f} ops/sec")
    print(f"   Patterns analyzed: {len(parse_results.get('pattern_performance', {}))}")
    if parse_results.get('errors', 0) > 0:
        print(f"   Errors: {parse_results['errors']}")
    print()
    
    # 6. Pattern-specific analysis
    print("6. Analyzing pattern-specific performance...")
    pattern_analysis = PatternSpecificPerformance.analyze(parse_results)
    results['pattern_analysis'] = pattern_analysis
    if 'fastest_patterns' in pattern_analysis:
        print(f"   Fastest pattern: {pattern_analysis['fastest_patterns'][0]['pattern']}")
        print(f"   Slowest pattern: {pattern_analysis['slowest_patterns'][-1]['pattern']}")
    print()
    
    # 7. Batch performance
    print("7. Benchmarking batch processing...")
    batch_results = BatchPerformance.benchmark(parser, test_cases)
    results['batch_processing'] = batch_results
    for batch_key, batch_data in batch_results['results'].items():
        print(f"   {batch_key}: {batch_data['throughput']:.0f} ops/sec")
    print()
    
    # 8. Memory performance
    if not skip_memory:
        print("8. Benchmarking memory usage...")
        memory_results = MemoryPerformance.benchmark(parser, test_cases[:1000], iterations=1)
        results['memory'] = memory_results
        if 'error' not in memory_results:
            print(f"   Peak memory: {memory_results['peak_memory'] / 1024 / 1024:.2f} MB")
            print(f"   Memory per operation: {memory_results['memory_per_operation'] / 1024:.2f} KB")
        else:
            print(f"   {memory_results['error']}")
        print()
    else:
        print("8. Skipping memory profiling (--skip-memory)")
        print()
    
    # 9. Library comparison
    print("9. Running library comparisons...")
    library_comparison_results = LibraryComparison.run_all_comparisons(test_cases, iterations=iterations)
    results['library_comparison'] = library_comparison_results
    
    # Print comparison table
    print("\n" + LibraryComparison.generate_comparison_table(library_comparison_results))
    print()
    
    return results


def save_results(results: Dict[str, Any], output_dir: Path, baseline_path: Optional[Path] = None):
    """Save results in multiple formats."""
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Save JSON report
    json_file = output_dir / f'performance_report_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"JSON report saved to: {json_file}")
    
    # Save CSV summary
    csv_file = output_dir / f'performance_summary_{timestamp}.csv'
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Category', 'Metric', 'Value', 'Unit'])
        
        # Initialization
        if 'initialization' in results:
            init = results['initialization']
            writer.writerow(['initialization', 'mean_time', f"{init['mean']*1000:.4f}", 'ms'])
            writer.writerow(['initialization', 'median_time', f"{init['median']*1000:.4f}", 'ms'])
        
        # Parse
        if 'parse' in results:
            parse = results['parse']
            parse_stats = parse['stats'].get('parse', {})
            writer.writerow(['parse', 'mean_time', f"{parse_stats.get('mean', 0)*1000:.4f}", 'ms'])
            writer.writerow(['parse', 'p95_time', f"{parse_stats.get('p95', 0)*1000:.4f}", 'ms'])
            writer.writerow(['parse', 'success_rate', f"{parse['success_rate']:.4f}", 'ratio'])
            writer.writerow(['parse', 'throughput', f"{parse['throughput']:.0f}", 'ops/sec'])
        
        # Match
        if 'match' in results:
            match = results['match']
            match_stats = match['stats'].get('match', {})
            writer.writerow(['match', 'mean_time', f"{match_stats.get('mean', 0)*1000:.4f}", 'ms'])
            writer.writerow(['match', 'p95_time', f"{match_stats.get('p95', 0)*1000:.4f}", 'ms'])
            writer.writerow(['match', 'success_rate', f"{match['success_rate']:.4f}", 'ratio'])
            writer.writerow(['match', 'throughput', f"{match['throughput']:.0f}", 'ops/sec'])
        
        # MatchPrefix
        if 'match_prefix' in results:
            prefix = results['match_prefix']
            prefix_stats = prefix['stats'].get('match_prefix', {})
            writer.writerow(['match_prefix', 'mean_time', f"{prefix_stats.get('mean', 0)*1000000:.4f}", 'μs'])
            writer.writerow(['match_prefix', 'throughput', f"{prefix['throughput']:.0f}", 'ops/sec'])
        
        # Library comparison
        if 'library_comparison' in results:
            lib_comp = results['library_comparison']
            for lib_key, lib_data in lib_comp.items():
                if 'error' not in lib_data:
                    lib_name = lib_data.get('library', lib_key)
                    writer.writerow(['library_comparison', f'{lib_name}_total_time', f"{lib_data.get('total_time', 0):.4f}", 's'])
                    writer.writerow(['library_comparison', f'{lib_name}_success_rate', f"{lib_data.get('success_rate', 0):.4f}", 'ratio'])
                    writer.writerow(['library_comparison', f'{lib_name}_mean_time', f"{lib_data.get('mean_time', 0)*1000:.4f}", 'ms'])
                    writer.writerow(['library_comparison', f'{lib_name}_throughput', f"{lib_data.get('throughput', 0):.0f}", 'ops/sec'])
    
    print(f"CSV summary saved to: {csv_file}")
    
    # Generate text summary
    text_file = output_dir / f'performance_summary_{timestamp}.txt'
    with open(text_file, 'w') as f:
        f.write("QDDate Performance Test Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Python version: {results['python_version']}\n")
        f.write(f"Test cases: {results['test_cases_count']}\n")
        f.write(f"Iterations: {results['iterations']}\n\n")
        
        if 'initialization' in results:
            init = results['initialization']
            f.write("Initialization:\n")
            f.write(f"  Mean: {init['mean']*1000:.2f}ms\n")
            f.write(f"  Median: {init['median']*1000:.2f}ms\n\n")
        
        if 'parse' in results:
            parse = results['parse']
            parse_stats = parse['stats'].get('parse', {})
            f.write("Parse Operations:\n")
            f.write(f"  Mean: {parse_stats.get('mean', 0)*1000:.2f}ms\n")
            f.write(f"  P95: {parse_stats.get('p95', 0)*1000:.2f}ms\n")
            f.write(f"  Success rate: {parse['success_rate']*100:.1f}%\n")
            f.write(f"  Throughput: {parse['throughput']:.0f} ops/sec\n\n")
        
        if 'match' in results:
            match = results['match']
            match_stats = match['stats'].get('match', {})
            f.write("Match Operations:\n")
            f.write(f"  Mean: {match_stats.get('mean', 0)*1000:.2f}ms\n")
            f.write(f"  P95: {match_stats.get('p95', 0)*1000:.2f}ms\n")
            f.write(f"  Success rate: {match['success_rate']*100:.1f}%\n")
            f.write(f"  Throughput: {match['throughput']:.0f} ops/sec\n\n")
        
        # Library comparison
        if 'library_comparison' in results:
            f.write("\n" + "=" * 80 + "\n")
            f.write("Library Comparison\n")
            f.write("=" * 80 + "\n\n")
            f.write(LibraryComparison.generate_comparison_table(results['library_comparison']))
            f.write("\n\n")
    
    print(f"Text summary saved to: {text_file}")
    
    # Save as baseline if requested
    if baseline_path:
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Baseline saved to: {baseline_path}")
    
    return json_file, csv_file, text_file


def generate_comparison_report(current: Dict[str, Any], baseline: Dict[str, Any], 
                               output_dir: Path) -> Path:
    """Generate comparison report between current and baseline."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    comparison_file = output_dir / f'comparison_report_{timestamp}.txt'
    
    detector = RegressionDetector()
    comparison = detector.compare(current, baseline)
    
    with open(comparison_file, 'w') as f:
        f.write("Performance Comparison Report\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Baseline timestamp: {baseline.get('timestamp', 'unknown')}\n")
        f.write(f"Current timestamp: {current.get('timestamp', 'unknown')}\n\n")
        
        f.write(f"Regressions detected: {comparison['regression_count']}\n")
        f.write(f"Improvements detected: {comparison['improvement_count']}\n\n")
        
        if comparison['regressions']:
            f.write("REGRESSIONS (>10% slower):\n")
            f.write("-" * 80 + "\n")
            for reg in comparison['regressions']:
                f.write(f"  {reg['metric']}:\n")
                f.write(f"    Baseline: {reg['baseline']:.6f}s\n")
                f.write(f"    Current:  {reg['current']:.6f}s\n")
                f.write(f"    Change:   +{reg['change_pct']:.1f}%\n\n")
        
        if comparison['improvements']:
            f.write("IMPROVEMENTS (>10% faster):\n")
            f.write("-" * 80 + "\n")
            for imp in comparison['improvements']:
                f.write(f"  {imp['metric']}:\n")
                f.write(f"    Baseline: {imp['baseline']:.6f}s\n")
                f.write(f"    Current:  {imp['current']:.6f}s\n")
                f.write(f"    Change:   {imp['change_pct']:.1f}%\n\n")
    
    print(f"Comparison report saved to: {comparison_file}")
    return comparison_file


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Comprehensive performance test suite for qddate',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--csv', type=str, 
                       default='benchmarks/test_data.csv',
                       help='Path to test data CSV file')
    parser.add_argument('--iterations', type=int, default=1,
                       help='Number of iterations per test case')
    parser.add_argument('--prefix-iterations', type=int, default=50,
                       help='Number of iterations for prefix benchmark')
    parser.add_argument('--baseline', type=str, default=None,
                       help='Path to baseline JSON file for regression detection')
    parser.add_argument('--save-baseline', type=str, default=None,
                       help='Save results as baseline to specified path')
    parser.add_argument('--output-dir', type=str, default='benchmarks/results',
                       help='Output directory for reports')
    parser.add_argument('--skip-memory', action='store_true',
                       help='Skip memory profiling (faster runs)')
    parser.add_argument('--pattern-filter', type=str, nargs='+',
                       help='Filter test cases by pattern keys')
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    
    output_dir = Path(args.output_dir)
    baseline_path = Path(args.baseline) if args.baseline else None
    save_baseline_path = Path(args.save_baseline) if args.save_baseline else None
    
    # Run tests
    results = run_comprehensive_tests(
        csv_path=csv_path,
        iterations=args.iterations,
        prefix_iterations=args.prefix_iterations,
        skip_memory=args.skip_memory,
        pattern_filter=args.pattern_filter,
    )
    
    # Save results
    save_results(results, output_dir, save_baseline_path)
    
    # Compare with baseline if provided
    if baseline_path:
        baseline = RegressionDetector.load_baseline(baseline_path)
        if baseline:
            print("\nComparing with baseline...")
            comparison = RegressionDetector.compare(results, baseline)
            if comparison['regression_count'] > 0:
                print(f"WARNING: {comparison['regression_count']} regressions detected!")
            if comparison['improvement_count'] > 0:
                print(f"INFO: {comparison['improvement_count']} improvements detected!")
            generate_comparison_report(results, baseline, output_dir)
    
    print("\n" + "=" * 80)
    print("Performance testing complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()

