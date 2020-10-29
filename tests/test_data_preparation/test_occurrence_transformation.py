"""Tests the occurrence data filters
"""
import os
import tempfile

import numpy as np
import pytest

from lmpy.point import PointCsvReader, PointCsvWriter
from lmpy.data_preparation.occurrence_transformation import (
    get_chunk_key, sort_points, split_points, wrangle_points)
from lmpy.data_wrangling.occurrence.filters import (
    get_bounding_box_filter, get_minimum_points_filter)

# .............................................................................
def _create_csv_reader(num_points, num_species):
    """Create a sample csv reader file."""
    with tempfile.NamedTemporaryFile(
            mode='wt', encoding='utf8', suffix='.csv', delete=False
            ) as reader_file:
        reader_filename = reader_file.name
        reader_file.write('Species,x,y\n')
        for _ in range(num_points):
            reader_file.write(
                'Species {},{},{}\n'.format(
                    np.random.randint(0, num_species),
                    np.random.randint(-180, 180), np.random.randint(-90, 90)))
    return reader_filename


# .............................................................................
def _verify_sorted(reader_filename, species_field='species_name', x_field='x',
                   y_field='y'):
    """Verify that a set of points are sorted."""
    points_list = []
    with PointCsvReader(
            reader_filename, species_field, x_field, y_field) as reader:
        for points in reader:
            points_list.extend(points)
    last_point = None
    for point in points_list:
        # Use point comparison to check for sorted
        if last_point is not None and point < last_point:
            return False
        # Move to next point
        last_point = point
    return True


# .............................................................................
class Test_get_chunk_key:
    """Tests for get_chunk_key."""
    # ................................
    def test_general(self):
        """Perform general testing for getting chunk keys."""
        value = '12345'
        # Check positions
        assert get_chunk_key(value, 0, 2) == '12'
        assert get_chunk_key(value, 1, 2) == '34'
        assert get_chunk_key(value, 2, 2) == '5a'  # One char overflow
        assert get_chunk_key(value, 3, 2) == 'aa'  # Complete overflow

        # Check group sizes
        assert get_chunk_key(value, 0, 3) == '123'


# .............................................................................
class Test_sort_points:
    """Tests for sort_points."""
    # ................................
    def test_simple(self):
        """Test with one reader and no wranglers."""
        reader_filename = _create_csv_reader(200, 5)
        writer_filename = tempfile.NamedTemporaryFile(
            mode='wt', encoding='utf8', suffix='.csv').name
        with PointCsvReader(reader_filename, 'Species', 'x', 'y') as reader:
            with PointCsvWriter(
                    writer_filename, ['species_name', 'x', 'y']) as writer:
                sorted_points = sort_points(reader, writer)

        # Verify points are sorted
        assert _verify_sorted(writer_filename)

        # Delete files
        os.remove(reader_filename)
        os.remove(writer_filename)

    # ................................
    def test_multiple_readers(self):
        """Test with multiple data readers."""
        readers = []
        for _ in range(10):
            reader_filename = _create_csv_reader(1000, 10)
            reader = PointCsvReader(reader_filename, 'Species', 'x', 'y')
            reader.open()
            readers.append(reader)

        writer_filename = tempfile.NamedTemporaryFile(
            mode='wt', encoding='utf8', suffix='.csv').name
        with PointCsvWriter(
                writer_filename, ['species_name', 'x', 'y']) as writer:
            sorted_points = sort_points(readers, writer)

        # Verify points are sorted
        assert _verify_sorted(writer_filename)

        # Close readers and delete filenames
        for reader in readers:
            reader.close()
            os.remove(reader.filename)

        # Delete writer file
        os.remove(writer_filename)

    # ................................
    def test_multiple_with_wranglers(self):
        """Test with multiple readers and data wranglers."""
        wranglers = [
            get_bounding_box_filter(-30, -30, 30, 30),
            get_minimum_points_filter(10)
        ]
        readers = []
        for _ in range(10):
            reader_filename = _create_csv_reader(1000, 10)
            reader = PointCsvReader(reader_filename, 'Species', 'x', 'y')
            reader.open()
            readers.append(reader)

        writer_filename = tempfile.NamedTemporaryFile(
            mode='wt', encoding='utf8', suffix='.csv').name
        with PointCsvWriter(
                writer_filename, ['species_name', 'x', 'y']) as writer:
            sorted_points = sort_points(readers, writer, wranglers=wranglers)

        # Verify points are sorted
        assert _verify_sorted(writer_filename)

        # Close readers and delete filenames
        for reader in readers:
            reader.close()
            os.remove(reader.filename)

        # Delete writer file
        os.remove(writer_filename)


# .............................................................................
class Test_split_points:
    """Tests for split_points."""


# .............................................................................
class Test_wrangle_points:
    """Tests for wrangle_points."""
