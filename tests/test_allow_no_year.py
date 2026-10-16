"""Tests for the ``allow_no_year=`` parameter (canonical name) and the
deprecated ``noyear=`` alias.
"""

import warnings

import pytest

from qddate import DateParser


@pytest.fixture
def parser():
    return DateParser()


def test_default_behaviour_unchanged(parser):
    """Default ``allow_no_year=True`` produces the same result as the old
    ``noyear=True`` default."""
    # Default behaviour: "05.12" parses to today (or current year) because the
    # no-year pattern is allowed.
    result = parser.parse("05.12")
    assert result is not None
    assert result.month == 12
    assert result.day == 5


def test_allow_no_year_false_disables_no_year_patterns(parser):
    """Setting ``allow_no_year=False`` skips the no-year pattern, returning
    None for inputs that have no year component."""
    assert parser.parse("05.12", allow_no_year=False) is None


def test_allow_no_year_true_keeps_no_year_patterns(parser):
    """Setting ``allow_no_year=True`` explicitly keeps the no-year pattern."""
    # Same outcome as the default; assert this stays the case.
    result = parser.parse("05.12", allow_no_year=True)
    assert result is not None


def test_noyear_param_emits_deprecation_warning(parser):
    """Using the deprecated ``noyear=`` kwarg emits ``DeprecationWarning``."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parser.parse("05.12", noyear=True)
    deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert any("allow_no_year" in str(w.message) for w in deprecations), (
        f"Expected DeprecationWarning mentioning allow_no_year; got: {caught}"
    )


def test_noyear_false_also_emits_deprecation(parser):
    """Using ``noyear=False`` (not just ``True``) also emits the warning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parser.parse("05.12", noyear=False)
    assert any(
        "allow_no_year" in str(w.message)
        for w in caught
        if issubclass(w.category, DeprecationWarning)
    )


def test_match_also_supports_allow_no_year(parser):
    """``match()`` accepts ``allow_no_year=`` and rejects no-year patterns
    when False."""
    assert parser.match("05.12", allow_no_year=False) is None
    assert parser.match("05.12") is not None


def test_match_all_also_supports_allow_no_year(parser):
    """``match_all()`` accepts ``allow_no_year=``."""
    assert parser.match_all("05.12", allow_no_year=False) == []
    assert len(parser.match_all("05.12")) >= 1


def test_match_noyear_kwarg_emits_deprecation(parser):
    """``match()`` with ``noyear=`` also emits a deprecation warning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parser.match("05.12", noyear=False)
    assert any(
        "allow_no_year" in str(w.message)
        for w in caught
        if issubclass(w.category, DeprecationWarning)
    )


def test_match_all_noyear_kwarg_emits_deprecation(parser):
    """``match_all()`` with ``noyear=`` also emits a deprecation warning."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parser.match_all("05.12", noyear=False)
    assert any(
        "allow_no_year" in str(w.message)
        for w in caught
        if issubclass(w.category, DeprecationWarning)
    )
