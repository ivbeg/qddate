"""
Performance regression tests for qddate.

These tests establish baseline performance metrics and detect regressions.
"""

import pytest
import time
import statistics
from qddate import DateParser

# Baseline performance thresholds (in seconds)
# These should be updated after profiling to reflect actual performance
BASELINE_THRESHOLDS = {
    'initialization_mean': 0.5,  # 500ms
    'parse_mean': 0.01,  # 10ms per parse
    'match_mean': 0.008,  # 8ms per match
    'match_prefix_mean': 0.00001,  # 10μs per matchPrefix call
}

# Test data
TEST_CASES = [
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
]


@pytest.fixture(scope='module')
def parser():
    """Create a parser instance for testing."""
    return DateParser()


def time_function(func, *args, **kwargs):
    """Time a function call."""
    start = time.perf_counter()
    result = func(*args, **kwargs)
    duration = time.perf_counter() - start
    return result, duration


class TestInitializationPerformance:
    """Test parser initialization performance."""
    
    def test_initialization_time(self):
        """Test that initialization completes within threshold."""
        timings = []
        iterations = 5
        
        for _ in range(iterations):
            _, duration = time_function(DateParser)
            timings.append(duration)
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['initialization_mean'], \
            f"Initialization too slow: {mean_time:.4f}s (threshold: {BASELINE_THRESHOLDS['initialization_mean']}s)"
    
    def test_initialization_consistency(self):
        """Test that initialization time is consistent."""
        timings = []
        iterations = 5
        
        for _ in range(iterations):
            _, duration = time_function(DateParser)
            timings.append(duration)
        
        # Check that standard deviation is reasonable (less than 50% of mean)
        if len(timings) > 1:
            stdev = statistics.stdev(timings)
            mean = statistics.mean(timings)
            assert stdev < mean * 0.5, \
                f"Initialization time too variable: stdev={stdev:.4f}s, mean={mean:.4f}s"


class TestParsePerformance:
    """Test parse operation performance."""
    
    def test_parse_time(self, parser):
        """Test that parse operations complete within threshold."""
        timings = []
        
        for text in TEST_CASES:
            _, duration = time_function(parser.parse, text)
            timings.append(duration)
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['parse_mean'], \
            f"Parse too slow: {mean_time:.4f}s (threshold: {BASELINE_THRESHOLDS['parse_mean']}s)"
    
    def test_parse_batch_performance(self, parser):
        """Test batch parsing performance."""
        iterations = 10
        timings = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            for text in TEST_CASES:
                parser.parse(text)
            duration = time.perf_counter() - start
            timings.append(duration / len(TEST_CASES))
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['parse_mean'] * 1.5, \
            f"Batch parse too slow: {mean_time:.4f}s per parse"
    
    def test_parse_success_rate(self, parser):
        """Test that parse succeeds for valid dates."""
        successful = 0
        total = len(TEST_CASES)
        
        for text in TEST_CASES:
            result = parser.parse(text)
            if result is not None:
                successful += 1
        
        success_rate = successful / total
        # Should parse at least 80% of test cases
        assert success_rate >= 0.8, \
            f"Parse success rate too low: {success_rate:.1%} (expected >= 80%)"


class TestMatchPerformance:
    """Test match operation performance."""
    
    def test_match_time(self, parser):
        """Test that match operations complete within threshold."""
        timings = []
        
        for text in TEST_CASES:
            _, duration = time_function(parser.match, text)
            timings.append(duration)
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['match_mean'], \
            f"Match too slow: {mean_time:.4f}s (threshold: {BASELINE_THRESHOLDS['match_mean']}s)"
    
    def test_match_batch_performance(self, parser):
        """Test batch matching performance."""
        iterations = 10
        timings = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            for text in TEST_CASES:
                parser.match(text)
            duration = time.perf_counter() - start
            timings.append(duration / len(TEST_CASES))
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['match_mean'] * 1.5, \
            f"Batch match too slow: {mean_time:.4f}s per match"


class TestMatchPrefixPerformance:
    """Test matchPrefix function performance."""
    
    def test_match_prefix_time(self):
        """Test that matchPrefix completes within threshold."""
        from qddate.dirty import matchPrefix
        
        timings = []
        iterations = 100
        
        for _ in range(iterations):
            for text in TEST_CASES:
                prefix = text[:6] if len(text) > 6 else text
                _, duration = time_function(matchPrefix, prefix)
                timings.append(duration)
        
        mean_time = statistics.mean(timings)
        assert mean_time < BASELINE_THRESHOLDS['match_prefix_mean'], \
            f"matchPrefix too slow: {mean_time:.6f}s (threshold: {BASELINE_THRESHOLDS['match_prefix_mean']}s)"


class TestPrefixOptimization:
    """Test that prefix optimization provides benefit."""
    
    def test_prefix_vs_no_prefix(self, parser):
        """Test that prefix matching improves performance."""
        # With prefix
        timings_with_prefix = []
        for text in TEST_CASES:
            _, duration = time_function(parser.parse, text, noprefix=False)
            timings_with_prefix.append(duration)
        
        # Without prefix
        timings_without_prefix = []
        for text in TEST_CASES:
            _, duration = time_function(parser.parse, text, noprefix=True)
            timings_without_prefix.append(duration)
        
        mean_with = statistics.mean(timings_with_prefix)
        mean_without = statistics.mean(timings_without_prefix)
        
        # Prefix should be faster or at least not significantly slower
        # Allow 20% tolerance for variance
        assert mean_with <= mean_without * 1.2, \
            f"Prefix matching slower than expected: with={mean_with:.6f}s, without={mean_without:.6f}s"


class TestMemoryUsage:
    """Test memory usage characteristics."""
    
    def test_no_memory_leak(self, parser):
        """Test that repeated parsing doesn't cause memory leaks."""
        # This is a basic test - full memory profiling should use memory_profiler
        initial_objects = len([x for x in dir(parser) if not x.startswith('_')])
        
        # Perform many parse operations
        for _ in range(100):
            for text in TEST_CASES:
                parser.parse(text)
        
        final_objects = len([x for x in dir(parser) if not x.startswith('_')])
        
        # Should not create excessive new attributes
        assert final_objects <= initial_objects + 5, \
            "Possible memory leak detected (too many new attributes)"


class TestPerformanceConsistency:
    """Test performance consistency across runs."""
    
    def test_parse_consistency(self, parser):
        """Test that parse performance is consistent."""
        text = '01.12.2009'
        timings = []
        
        for _ in range(20):
            _, duration = time_function(parser.parse, text)
            timings.append(duration)
        
        # Check that variance is reasonable
        if len(timings) > 1:
            stdev = statistics.stdev(timings)
            mean = statistics.mean(timings)
            coefficient_of_variation = stdev / mean if mean > 0 else 0
            
            # CV should be less than 0.5 (50% variation)
            assert coefficient_of_variation < 0.5, \
                f"Parse performance too variable: CV={coefficient_of_variation:.2f}"


@pytest.mark.skipif(True, reason="Baseline thresholds need to be updated after profiling")
class TestBaselineThresholds:
    """Test that baseline thresholds are reasonable."""
    
    def test_thresholds_are_set(self):
        """Test that baseline thresholds are configured."""
        assert BASELINE_THRESHOLDS, "Baseline thresholds not configured"
        
        for key, value in BASELINE_THRESHOLDS.items():
            assert value > 0, f"Threshold {key} must be positive"
            assert isinstance(value, (int, float)), f"Threshold {key} must be numeric"

