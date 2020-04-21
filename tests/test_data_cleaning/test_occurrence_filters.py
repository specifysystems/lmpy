"""Tests the occurrence data filters
"""
import pytest

from lmpy import Point
from lmpy.data_cleaning.occurrence_filters import (
    get_bounding_box_filter, get_data_flag_filter,
    get_disjoint_geometries_filter, get_intersect_geometries_filter,
    get_unique_localities_filter)


# .............................................................................
class Test_occurrence_filters:
    """Test occurrence filters."""
    # .....................................
    def _filter_points(self, filter_function, points):
        """Filter points using provided function.

        Args:
            filter_function (function): A function that takes a point and
                returns a boolean value if it passes the filter.
            points (list of Point): A list of points to test.

        Returns:
            list - A list of points that pass the filter.
            int - A count of the points that were filtered out.
        """
        filter_count = 0
        filtered_points = []
        for point in points:
            if filter_function(point):
                filtered_points.append(point)
            else:
                filter_count += 1
        return (filtered_points, filter_count)

    # .....................................
    def test_get_bounding_box_filter(self):
        """Test the get_bounding_box_filter function."""
        test_points = [
            Point('species A', 10, 40),  # Should pass
            Point('species A', -10, 30),
            Point('species A', 30, 30),  # Should pass
            Point('species A', 50, 30),  # Should pass
            Point('species A', -30, -60)
        ]
        test_bounding_box = (0.0, 0.0, 180.0, 90.0)
        bbox_filter = get_bounding_box_filter(*test_bounding_box)
        filtered_points, filter_count = self._filter_points(
            bbox_filter, test_points)
        assert len(filtered_points) == 3
        assert filter_count == 2

    # .....................................
    def test_get_data_flag_filter(self):
        """Test the get_data_flag_filter function."""
        test_points = [
            Point('species A', 10, 40, ['bad']),
            Point('species A', -10, 30, ['good']),  # Should pass
            Point('species A', 30, 30, ['worse']),
            Point('species A', 50, 30, 'bad'),
            Point('species A', -30, -60, ['good'])  # Should pass
        ]
        data_flag_filter = get_data_flag_filter(['bad', 'worse'])
        filtered_points, filter_count = self._filter_points(
            data_flag_filter, test_points)
        assert len(filtered_points) == 2
        assert filter_count == 3

    # .....................................
    def test_get_disjoint_geometries_filter(self):
        """Test the get_disjoint_geometries_filter function."""
        test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
        test_points = [
            Point('species A', -10, 40),  # Should pass
            Point('species A', -10, 30),  # Should pass
            Point('species A', 30, 30),
            Point('species A', 50, 30),  # Should pass
            Point('species A', -30, -60)  # Should pass
        ]
        disjoint_filter = get_disjoint_geometries_filter(test_geometries)
        filtered_points, filter_count = self._filter_points(
            disjoint_filter, test_points)
        assert len(filtered_points) == 4
        assert filter_count == 1

    # .....................................
    def test_get_intersect_geometries_filter(self):
        """Test the get_intersect_geometries_filter function."""
        test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
        test_points = [
            Point('species A', -10, 40),
            Point('species A', -10, 30),
            Point('species A', 30, 30),  # Should pass
            Point('species A', 50, 30),
            Point('species A', -30, -60)
        ]
        intersect_filter = get_intersect_geometries_filter(test_geometries)
        filtered_points, filter_count = self._filter_points(
            intersect_filter, test_points)
        assert len(filtered_points) == 1
        assert filter_count == 4

    # .....................................
    def test_get_unique_localities_filter(self):
        """Test the get_unique_localities_filter function."""
        test_points = [
            Point('species A', -10, 40),  # Should pass
            Point('species A', -10, 30),  # Should pass
            Point('species A', 30, 30),  # Should pass
            Point('species A', 50, 30),  # Should pass
            Point('species A', -30, -60),  # Should pass
            Point('species A', -10, 40),
            Point('species A', -10, 30),
            Point('species A', 30, 30),
            Point('species A', 50, 30),
            Point('species A', -30, -60)
        ]
        unique_localities_filter = get_unique_localities_filter()
        filtered_points, filter_count = self._filter_points(
            unique_localities_filter, test_points)
        assert len(filtered_points) == 5
        assert filter_count == 5

    # .....................................
    def test_multiple_filters(self):
        """Test multiple filters."""
        test_bbox = ()
        test_points = [
            Point('species A', 113, 57, ['good']),  # A
            Point('species A', -49, -25, ['bad']),  # B
            Point('species A', -49, -25, ['bad']),  # C
            Point('species A', 168, -13, ['bad']),  # D
            Point('species A', 114, 82, ['good']),  # E
            Point('species A', -67, -63, ['worse']),  # F
            Point('species A', 138, 81, ['worse']),  # G
            Point('species A', 82, -88, ['good']),  # H
            Point('species A', 82, -88, ['good']),  # I
            Point('species A', -76, 55, ['good']),  # J
            Point('species A', -76, 55, ['good']),  # K
            Point('species A', -121, 82, ['good']),  # L
            Point('species A', 58, -89, ['good']),  # M
            Point('species A', 0, 0, ['good'])  # N
        ]
        unique_localities_filter = get_unique_localities_filter()
        data_flag_filter = get_data_flag_filter(['bad', 'worse'])
        bbox_filter = get_bounding_box_filter(-90, -90, 90, 90)
        disjoint_filter = get_disjoint_geometries_filter(
            ['POLYGON ((0 -10, 10 0, 0 10, -10 0, 0 -10))'])
        intersect_filter = get_intersect_geometries_filter(
            ['POLYGON ((-180 0, 0 0, 0 90, -180 90, -180 0))'])
        # Current points - ABCDEFGHIJKLMN
        filtered_points, filter_count = self._filter_points(
            unique_localities_filter, test_points)
        # Removed points - CIK
        assert len(filtered_points) == 11
        assert filter_count == 3

        # Current points - ABDEFGHJLMN
        filtered_points, filter_count = self._filter_points(
            data_flag_filter, filtered_points)
        # Removed points - BDFG
        assert len(filtered_points) == 7
        assert filter_count == 4

        # Current points - AEHJLMN
        filtered_points, filter_count = self._filter_points(
            bbox_filter, filtered_points)
        # Removed points - AEL
        assert len(filtered_points) == 4
        assert filter_count == 3

        # Current points - HJMN
        filtered_points, filter_count = self._filter_points(
            disjoint_filter, filtered_points)
        # Removed points - N
        assert len(filtered_points) == 3
        assert filter_count == 1

        # Current points - J
        filtered_points, filter_count = self._filter_points(
            intersect_filter, filtered_points)
        # Removed points - HM
        assert len(filtered_points) == 1
        assert filter_count == 2

    # .....................................
    def test_no_valid_points(self):
        """Test when no points pass filter."""
        test_points = [Point('species A', 30, 30)]
        bbox_filter = get_bounding_box_filter(10, 10, 20, 20)
        filtered_points, filter_count = self._filter_points(
            bbox_filter, test_points)
        assert len(filtered_points) == 0
        assert filter_count == 1
