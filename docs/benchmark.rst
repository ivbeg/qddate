Benchmark
---------

The reference benchmark lives in ``benchmarks/bench.py`` and compares qddate
with `dateparser <https://github.com/scrapinghub/dateparser>`_ on a corpus of
50 multilingual date strings. Run it with::

    python benchmarks/bench.py

The helper script runs several passes (configurable inside the file) and prints
per-run timings together with the relative speed-up.

**Interpreting the numbers**

* The benchmark is CPU and storage bound; expect large variation across
  hardware, Python versions, and pyparsing releases.
* ``benchmarks/bench.py`` enables pyparsing packrat mode during the run so the
  reported numbers reflect the current optimized parser defaults.
* For a deeper discussion about profiling methodology and optimization ideas,
  see :file:`PERFORMANCE_ANALYSIS.md`.

If you run the benchmark on additional datasets or have more representative
numbers for your workloads, please file an issue or pull request with the
results so we can document them here.
