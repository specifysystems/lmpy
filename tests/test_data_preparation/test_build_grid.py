"""Tests build shapegrid."""
import os
from tempfile import NamedTemporaryFile
import pytest

from lmpy.data_preparation.build_grid import (
    build_shapegrid, hexagon_wkt_generator, make_polygon_wkt_from_points,
    square_wkt_generator)


# .............................................................................
class Test_build_shapegrid:
    """Test build_shapegrid."""
    # ................................
    def test_simple_square(self):
        """Basic test to make sure it doesn't just fail."""
        temp_filename = NamedTemporaryFile(suffix='.shp').name
        build_shapegrid(temp_filename, 0, 0, 90, 90, 3, 4326, 4)
        os.remove(temp_filename)

    # ................................
    def test_simple_hexagon(self):
        """Basic test to make sure it doesn't just fail."""
        temp_filename = NamedTemporaryFile(suffix='.shp').name
        build_shapegrid(temp_filename, 0, 0, 90, 90, 3, 4326, 6)
        os.remove(temp_filename)

    # ................................
    def test_invalid_shape(self):
        """Basic test to make sure it doesn't just fail."""
        temp_filename = NamedTemporaryFile(suffix='.shp').name
        with pytest.raises(ValueError):
            build_shapegrid(temp_filename, 0, 0, 90, 90, 3, 4326, 7)
        try:
            os.remove(temp_filename)
        except IOError:
            pass


# .............................................................................
class Test_make_polygon_wkt_from_points:
    """Test make_polygon_wkt_from_points."""
    # ................................
    def test_simple(self):
        """Perform a simple test that a known string is produced."""
        points = [(-10, -10), (-10, 10), (0, 0), (-10, -10)]
        point_strings = ['{} {}'.format(x, y) for x, y in points]
        point_strings.append('{} {}'.format(points[0][0], points[0][1]))
        test_string = 'POLYGON(({}))'.format(','.join(point_strings))
        assert make_polygon_wkt_from_points(points) == test_string


# .............................................................................
class Test_hexagon_wkt_generator:
    """Test hexagon_wkt_generator."""
    # ................................
    def test_simple(self):
        """Basic test to make sure it doesn't just fail and returns strings."""
        for pt_string in hexagon_wkt_generator(0, 0, 90, 90, 3, 3):
            assert isinstance(pt_string, str)


# .............................................................................
class Test_square_wkt_generator:
    """Test square_wkt_generator."""
    # ................................
    def test_simple(self):
        """Basic test to make sure it doesn't just fail and returns strings."""
        for pt_string in square_wkt_generator(0, 0, 90, 90, 3, 3):
            assert isinstance(pt_string, str)
