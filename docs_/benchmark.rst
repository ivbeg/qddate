Benchmark
--------------------

Benchmark code qddate vs dateparser is at `tests/bench.py'.
It runs 10 times against 50 raw dates, so it's up to 500 comparisons

Latest run:
>>> Bench per 10 pass: qddate 0.5 seconds, dateparser 44.8 seconds
>>> qddate.DateParser.parse is 84.7X faster over dateparser.parse


Note: This benchmarking was for internal testing only. Independent benchmark will be highly appreciated.
Feel free to write me at ivan@begtin.tech
