"""
Legacy setup.py for backward compatibility.
Modern packaging configuration is in pyproject.toml (PEP 621).
This file is kept for compatibility with older build tools.
"""
from setuptools import setup

# All metadata is now in pyproject.toml
# This minimal setup.py allows pip to install in editable mode
# with older versions of pip that don't fully support pyproject.toml
setup()
