"""Tests the occurrence_transformation module."""
import pytest

from data_preparation.occurrence_transformation import none_getter


# .............................................................................
def test_none_getter():
    """Tests that none_getter always returns None."""
    getter = none_gettter()
    assert getter(0) is None
    assert getter('a') is None
    assert getter(None) is None
    assert getter(b'0000') is None
