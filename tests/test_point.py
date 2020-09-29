"""Tests the occurrence_transformation module."""
from copy import deepcopy
from operator import itemgetter
import os
from random import randint, shuffle
import tempfile

import numpy as np
import pytest

from lmpy import Point
from lmpy.point import none_getter
from lmpy.data_wrangling.occurrence.modifiers import (
    get_coordinate_converter_modifier)


# .............................................................................
def _flag_getter(index):
    """Returns a getter for the test flags separated by ', '"""
    def getter(obj):
        flag_string = obj[index]
        return flag_string.split(', ')
    return getter


# .............................................................................
def test_none_getter():
    """Tests that none_getter always returns None."""
    getter = none_getter
    assert getter(0) is None
    assert getter('a') is None
    assert getter(None) is None
    assert getter(b'0000') is None


# .............................................................................
class Test_get_coordinate_converter_modifier:
    """Test get_coordinate_converter_modifier."""
    # ..........................
    def test_specific_values(self):
        """Test that conversion produces known values."""
        in_vals = (4326, -89.555857, 37.3040553)
        out_vals = (2815, 333699.36, 163612.51)
        converter = get_coordinate_converter_modifier(in_vals[0], out_vals[0])
        in_point = Point('test species', in_vals[1], in_vals[2])
        out_point = converter(in_point)[0]
        assert np.isclose(out_point.x, out_vals[1])
        assert np.isclose(out_point.y, out_vals[2])
        assert in_point.species_name == out_point.species_name

    # ..........................
    def test_to_and_back(self):
        """Test conversion from one to another and back."""
        in_vals = (4326, -89.555857, 37.3040553)
        converter = get_coordinate_converter_modifier(in_vals[0], 3395)
        converter_2 = get_coordinate_converter_modifier(3395, in_vals[0])
        in_point = Point('test species', in_vals[1], in_vals[2])
        out_point = converter(in_point)[0]
        out_point_2 = converter_2(out_point)[0]
        assert np.isclose(out_point_2.x, in_vals[1])
        assert np.isclose(out_point_2.y, in_vals[2])
        assert in_point.species_name == out_point.species_name

    # ..........................
    def test_transitive(self):
        """Test conversion from one to another to another and back."""
        in_vals = (4326, -89.555857, 37.3040553)
        epsgs = [3395, 2815]
        original_point = Point('Test species', in_vals[1], in_vals[2])
        in_points = [deepcopy(original_point)]
        src_epsg = in_vals[0]
        for target_epsg in epsgs:
            converter = get_coordinate_converter_modifier(
                src_epsg, target_epsg)
            in_points = converter(in_points)
            src_epsg = target_epsg
        final_converter = get_coordinate_converter_modifier(
            src_epsg, in_vals[0])
        final_point = final_converter(in_points)[0]
        assert np.isclose(final_point.x, original_point.x)
        assert np.isclose(final_point.y, original_point.y)
        assert final_point.species_name == original_point.species_name
