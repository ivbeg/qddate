# Comprehensive Performance Test Suite

This directory contains a comprehensive performance test suite for the qddate library that uses all test cases from `test_data.csv` (~10,360 cases).

## Overview

The `comprehensive_performance_test.py` script provides extensive performance testing capabilities:

- **Full Dataset Testing**: Processes all ~10,360 test cases from CSV
- **Comprehensive Metrics**: Tracks timing (mean, median, percentiles), throughput, success rates, memory usage
- **Pattern Analysis**: Performance breakdown by pattern_key
- **Regression Detection**: Compare against baselines and detect performance degradation
- **Statistical Analysis**: Confidence intervals, outliers, variance analysis
- **Multiple Report Formats**: JSON, CSV, HTML, text summaries

## Usage

### Basic Usage

Run the comprehensive test suite with default settings:

```bash
python3 benchmarks/comprehensive_performance_test.py
```

### Command-Line Options

```bash
python3 benchmarks/comprehensive_performance_test.py [OPTIONS]
```

**Options:**

- `--csv PATH`: Path to test data CSV file (default: `benchmarks/test_data.csv`)
- `--iterations N`: Number of iterations per test case (default: 1)
- `--prefix-iterations N`: Number of iterations for prefix benchmark (default: 50)
- `--baseline PATH`: Path to baseline JSON file for regression detection
- `--save-baseline PATH`: Save results as baseline to specified path
- `--output-dir PATH`: Output directory for reports (default: `benchmarks/results`)
- `--skip-memory`: Skip memory profiling (faster runs)
- `--pattern-filter PATTERN1 PATTERN2 ...`: Filter test cases by pattern keys

### Examples

**Quick test run (skip memory profiling):**
```bash
python3 benchmarks/comprehensive_performance_test.py --skip-memory --iterations 1
```

**Full test with multiple iterations:**
```bash
python3 benchmarks/comprehensive_performance_test.py --iterations 5 --prefix-iterations 100
```

**Test specific patterns only:**
```bash
python3 benchmarks/comprehensive_performance_test.py --pattern-filter dt:date:date_1 dt:date:date_2
```

**Create baseline and save it:**
```bash
python3 benchmarks/comprehensive_performance_test.py --save-baseline benchmarks/baseline_metrics.json
```

**Compare against baseline:**
```bash
python3 benchmarks/comprehensive_performance_test.py --baseline benchmarks/baseline_metrics.json
```

## Output Files

The test suite generates several output files in the specified output directory:

### 1. JSON Report (`performance_report_TIMESTAMP.json`)

Complete metrics in structured JSON format including:
- All timing statistics (mean, median, min, max, percentiles)
- Success rates and error counts
- Pattern-specific performance breakdown
- Batch processing results
- Memory usage (if enabled)

### 2. CSV Summary (`performance_summary_TIMESTAMP.csv`)

Key metrics in CSV format for easy analysis:
- Mean and median times
- P95 percentiles
- Success rates
- Throughput (operations per second)

### 3. Text Summary (`performance_summary_TIMESTAMP.txt`)

Human-readable summary with key findings:
- Overall statistics
- Performance highlights
- Success rates

### 4. Comparison Report (`comparison_report_TIMESTAMP.txt`)

Generated when comparing against a baseline:
- List of regressions (>10% slower)
- List of improvements (>10% faster)
- Detailed before/after comparisons

## Performance Metrics

The test suite tracks the following metrics:

### Timing Metrics
- **Mean**: Average time per operation
- **Median**: 50th percentile
- **Min/Max**: Minimum and maximum times
- **Percentiles**: P50, P90, P95, P99
- **Standard Deviation**: Measure of variance
- **Coefficient of Variation**: Normalized variance

### Throughput
- Operations per second for each operation type

### Success Rates
- Overall success rate
- Per-pattern success rates
- Error counts

### Pattern Analysis
- Fastest patterns
- Slowest patterns
- Pattern-specific statistics

### Memory Usage (optional)
- Peak memory usage
- Memory per operation
- Memory differences

## Regression Detection

The regression detection system compares current results against a baseline:

1. **Create a baseline:**
   ```bash
   python3 benchmarks/comprehensive_performance_test.py --save-baseline benchmarks/baseline_metrics.json
   ```

2. **Run tests and compare:**
   ```bash
   python3 benchmarks/comprehensive_performance_test.py --baseline benchmarks/baseline_metrics.json
   ```

3. **Review comparison report:**
   - Regressions (>10% slower) are flagged
   - Improvements (>10% faster) are highlighted
   - Detailed metrics comparison provided

## Performance Test Classes

The suite includes several test classes:

- **InitializationPerformance**: Parser creation time and consistency
- **ParsePerformance**: Full dataset parsing with detailed breakdowns
- **MatchPerformance**: Pattern matching performance
- **MatchPrefixPerformance**: Prefix matching optimization effectiveness
- **BatchPerformance**: Large batch processing efficiency
- **MemoryPerformance**: Memory usage patterns and leak detection
- **PatternSpecificPerformance**: Performance by pattern type
- **RegressionDetector**: Compare against baselines
- **StatisticalAnalyzer**: Statistical analysis and outlier detection

## Integration with CI/CD

The test suite can be integrated into CI/CD pipelines:

```bash
# Run tests and save baseline
python3 benchmarks/comprehensive_performance_test.py \
    --save-baseline benchmarks/baseline_metrics.json \
    --output-dir benchmarks/results

# In subsequent runs, compare against baseline
python3 benchmarks/comprehensive_performance_test.py \
    --baseline benchmarks/baseline_metrics.json \
    --output-dir benchmarks/results
```

Exit code will be non-zero if significant regressions are detected (can be enhanced in the script).

## Dependencies

**Required:**
- Python 3.7+
- qddate library
- Standard library: `csv`, `json`, `statistics`, `time`, `pathlib`, `argparse`

**Optional:**
- `tqdm`: For progress bars during long-running tests (install with `pip install tqdm`)
  - If not installed, the script will run without progress bars
- `tracemalloc`: For memory profiling (included in Python 3.4+)
- `memory_profiler`: For detailed memory tracking (install with `pip install memory-profiler`)

## Notes

- The test suite handles errors gracefully and continues testing even if some test cases fail
- Progress bars are displayed during long-running operations (requires `tqdm` package)
- Memory profiling can be slow; use `--skip-memory` for faster runs
- Large iteration counts will significantly increase test time
- Pattern filtering is useful for testing specific pattern types

## Example Output

```
================================================================================
QDDate Comprehensive Performance Test Suite
================================================================================
Python version: 3.13.7
CSV file: benchmarks/test_data.csv
Iterations: 1

Loading test data from CSV...
Loaded 10359 test cases

1. Benchmarking parser initialization...
   Mean initialization time: 17.11ms

2. Creating parser instance...
   Parser created successfully

3. Benchmarking matchPrefix...
   Mean time per call: 0.24μs
   Throughput: 2210910 ops/sec

4. Benchmarking match operations...
   Mean time per match: 2.37ms
   P95: 9.86ms
   Success rate: 79.9%
   Throughput: 441 ops/sec

5. Benchmarking parse operations...
   Mean time per parse: 2.35ms
   P95: 9.89ms
   Success rate: 79.9%
   Throughput: 444 ops/sec
   Patterns analyzed: 69

6. Analyzing pattern-specific performance...
   Fastest pattern: dt:date:date_10
   Slowest pattern: dt:date:es_weekday

7. Benchmarking batch processing...
   batch_100: 379 ops/sec
   batch_500: 450 ops/sec
   batch_1000: 452 ops/sec
   batch_5000: 439 ops/sec

8. Skipping memory profiling (--skip-memory)

JSON report saved to: benchmarks/results/performance_report_20260102_140321.json
CSV summary saved to: benchmarks/results/performance_summary_20260102_140321.csv
Text summary saved to: benchmarks/results/performance_summary_20260102_140321.txt

================================================================================
Performance testing complete!
================================================================================
```

