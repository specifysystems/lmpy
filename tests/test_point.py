"""Tests the occurrence_transformation module."""
from copy import deepcopy
import json
from operator import itemgetter
import os
from random import randint, shuffle, triangular
import tempfile

import numpy as np
import pytest

from lmpy import Point
from lmpy.point import (
    none_getter, PointCsvReader, PointCsvWriter, PointJsonWriter)


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


# ............................................................................
class Test_Point:
    """Test Point class."""
    # ..........................
    def test_constructor(self):
        """Basic constructor tests."""
        pt = Point('test_species', 0, 0)
        with pytest.raises(ValueError):
            Point(None, 0, 0)

    # ..........................
    def test_equality(self):
        """Test for point equality and inequality."""
        pt_1 = Point('Species', 30, 30)
        pt_2 = Point('Species 2', 30, 30)
        pt_3 = Point('Species', 30, 30)
        assert pt_1 == pt_3
        assert pt_1 != pt_2

    # ..........................
    def test_less_than(self):
        """Test for less than."""
        pt_1 = Point('Species 1', 30, 30)
        pt_2 = Point('Species 2', 30, 30)
        pt_3 = Point('Species 1', 40, 20)
        pt_4 = Point('Species 1', 20, 40)
        pt_5 = Point('Species 1', 30, 40)
        assert pt_1 < pt_2
        assert pt_1 < pt_3
        assert pt_4 < pt_1
        assert pt_1 < pt_5
        assert not pt_1 < pt_1
        assert not pt_2 < pt_3

    # ..........................
    def test_get_set_attribute(self):
        """Test get and set attribute."""
        pt = Point('Species', 0, 0)
        assert pt.get_attribute('test') is None
        pt.set_attribute('test', 1)
        assert pt.get_attribute('test') == 1

    # ..........................
    def test_repr(self):
        """Test the repr function."""
        assert repr(Point('Species', 0, 0))


# ............................................................................
class Test_PointCsvReader:
    """Test the PointCSVReader class."""
    # ..........................
    def _make_csv(self, num_species, species_field, x_field, y_field,
                  geopoint_field=None):
        """Make a CSV file."""
        if geopoint_field is not None:
            headers = [species_field, geopoint_field]

            def string_point(pt):
                return '"{}", "{}"\n'.format(
                    pt.species_name,
                    json.dumps({x_field: pt.x, y_field: pt.y}).replace(
                        '"', '""'))
        else:
            headers = [species_field, x_field, y_field]

            def string_point(pt):
                return '{}, {}, {}\n'.format(
                    pt.species_name, pt.x, pt.y)
        out_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.csv', delete=False)
        i = 0
        # Write headers
        out_file.write('{}\n'.format(','.join(headers)))
        while i < num_species:
            pt = Point(
                'Species {}'.format(i), triangular(-180.0, 180.0),
                triangular(-90.0, 90.0))
            out_file.write(string_point(pt))
            if triangular(0.0, 1.0) > 0.92:
                i += 1
        out_file.close()
        return out_file.name

    # ..........................
    def test_reader_species_x_y(self):
        """Test with a CSV file of species, x, y."""
        pt_filename = self._make_csv(5, 'species', 'lon', 'lat')
        with PointCsvReader(pt_filename, 'species', 'lon', 'lat') as reader:
            for points in reader:
                assert len(points) > 0
        os.remove(pt_filename)

    # ..........................
    def test_reader_species_geopoint(self):
        """Test with a CSV file of species, geopt."""
        pt_filename = self._make_csv(
            10, 'species', 'lon', 'lat', geopoint_field='geopt')
        with PointCsvReader(pt_filename, 'species', 'lon', 'lat',
                            geopoint='geopt') as reader:
            for points in reader:
                assert len(points) > 0
        os.remove(pt_filename)


# ............................................................................
class Test_PointCsvWriter:
    """Test PointCsvWriter class."""
    # ..........................
    def test_basic(self):
        """Perform simple test."""
        out_file = tempfile.NamedTemporaryFile(
            suffix='.csv', delete=False, mode='w')
        filename = out_file.name
        with PointCsvWriter(filename, ['species_name', 'x', 'y']) as writer:
            writer.write_points(Point('species', 0, 0))
            writer.write_points(
                [
                    Point('species', 10, 10),
                    Point('species', 20, 20),
                    Point('species', -30, -30)
                ])
        os.remove(filename)


# ............................................................................
class Test_PointJsonWriter:
    """Test PointJsonWriter class."""
    # ..........................
    def test_basic(self):
        """Perform simple test."""
        out_file = tempfile.NamedTemporaryFile(
            suffix='.json', delete=False, mode='w')
        filename = out_file.name
        with PointJsonWriter(filename) as writer:
            writer.write_points(Point('species', 0, 0))
            writer.write_points(
                [
                    Point('species', 10, 10),
                    Point('species', 20, 20),
                    Point('species', -30, -30)
                ])
        os.remove(filename)
