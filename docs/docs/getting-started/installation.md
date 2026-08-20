---
title: "Installation"
description: "Install qddate with pip, from source, or with the optional bench extra"
---
# Installation

qddate supports Python 3.8–3.12 on CPython and PyPy. The only runtime dependency
is [pyparsing](https://pypi.org/project/pyparsing/).

### Using pip

```bash
pip install qddate
```

### From source

```bash
git clone https://github.com/ivbeg/qddate.git
cd qddate
pip install -e .
```

With development extras (tests, linters, packaging tools):

```bash
pip install -e ".[dev,test]"
```

### Optional extras

| Extra | Enables |
|-------|---------|
| `test` | pytest and coverage |
| `bench` | dateparser, python-dateutil, arrow, pendulum for comparison scripts in `benchmarks/` |
| `dev` | ruff, tox, twine, build |

```bash
pip install "qddate[test]"
pip install "qddate[bench]"
pip install "qddate[dev]"
```

`bench` libraries are never imported by the parser at runtime. Install that extra
only when you want to run `benchmarks/bench.py` or related comparison scripts.

### Verify the install

```python
import qddate

parser = qddate.DateParser()
print(qddate.__version__)
print(parser.parse("2012-12-15"))
```

If `import qddate` fails, confirm you are on Python 3.8+ and that `pyparsing>=3.1.0`
is installed.

## Next steps

- [Quick start](/getting-started/quick-start)
- [Basic usage](/getting-started/basic-usage)
- [When to use qddate](/getting-started/when-to-use)
