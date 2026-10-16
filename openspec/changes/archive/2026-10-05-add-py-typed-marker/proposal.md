# OpenSpec Change: Add `py.typed` marker (PEP 561)

The previous round shipped type hints on the public API and made `mypy
qddate/__init__.py qddate/qdparser.py` clean. Downstream consumers don't yet
benefit because the wheel does not advertise "this package ships type hints"
via PEP 561 — they have to manually tell mypy to look at `qddate/` and
`qddate.pyi` will never be picked up. This change adds the `py.typed` marker
and configures the build to ship it.

## Why

PEP 561 (`typing`/packaging) says a package declares its type hints are
publicly available by including a `py.typed` file at the package root. Without
this marker, mypy/pyright treat a missing `.pyi` file as "no types provided",
even when inline annotations exist. The marker has to:

1. Be in the sdist.
2. Be installed alongside the `.py` files at the package root.
3. Be listed in `[tool.setuptools.package-data]` so the build system copies it
   into the wheel.

Today the package has hints but no marker, so `pip install qddate` and a
downstream `mypy` run treat `qddate` as untyped.

## What changes

**Add `qddate/py.typed`**
- New: empty marker file declaring the package is typed (PEP 561).
- Reason: Advertise type hints to downstream tooling.
- Impact: Non-breaking.

**Wire it into the wheel**
- Edit `pyproject.toml`'s `[tool.setuptools.package-data]` to include
  `"qddate" = ["py.typed"]`.
- Reason: setuptools needs an explicit instruction to ship the marker.
- Impact: Non-breaking.

**CI verification**
- Add a wheel-build smoke check (optional): the `dist/*.whl` for a fresh
  build must contain `qddate/py.typed`.
- Reason: Lock in the contract.

## Out of scope

- Generating a `.pyi` stub (the inline annotations are sufficient and pyright
  reads inline hints without `.pyi`).
- Adding per-platform stub markers.