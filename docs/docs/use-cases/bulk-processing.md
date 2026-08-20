---
title: "Bulk processing"
description: "Parse large corpora of date strings with a reused parser"
---
# Bulk processing

qddate is meant for millions of strings, not one-off interactive parsing. The
performance model assumes a long-lived parser and relatively uniform inputs.

## Worker pattern

```python
import qddate

parser = qddate.DateParser(languages=["en", "ru", "de"])

def parse_column(values):
    out = []
    for value in values:
        if not value:
            out.append(None)
            continue
        out.append(parser.parse(str(value).strip()))
    return out
```

Construct the parser **outside** the loop and outside per-row map functions.
In multiprocessing, construct one parser per worker, not per row.

## Measure before tuning

Run the bundled suite when you change patterns or Python versions:

```bash
pip install -e ".[bench,test]"
python benchmarks/bench.py
python benchmarks/comprehensive_performance_test.py --skip-memory
```

See [performance](/getting-started/performance) for the full list of scripts.

## Filter flags stay on

The hierarchical filters exist for bulk work. Disabling them (`noprefix=True`,
and similar) is for diagnosis, not production throughput.

## Related

- [Performance](/getting-started/performance)
- [Best practices](/getting-started/best-practices)
- [parse()](/api/parse)
