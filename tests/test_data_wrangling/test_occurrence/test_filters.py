"""Tests the occurrence data filters."""
from lmpy import Point
from lmpy.data_wrangling.occurrence.filters import (
    get_attribute_filter,
    get_bounding_box_filter,
    get_decimal_precision_filter,
    get_disjoint_geometries_filter,
    get_intersect_geometries_filter,
    get_minimum_points_filter,
    get_spatial_index_filter,
    get_unique_localities_filter,
)
from lmpy.spatial.spatial_index import create_geometry_from_bbox, SpatialIndex


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
            list: A list of points that pass the filter.
            int: A count of the points that were filtered out.
        """
        filter_count = 0
        filtered_points = filter_function(points)
        filter_count = len(points) - len(list(filtered_points))
        return (filtered_points, filter_count)

    # .....................................
    def test_get_bounding_box_filter(self):
        """Test the get_bounding_box_filter function."""
        test_points = [
            Point('species A', 10, 40),  # Should pass
            Point('species A', -10, 30),
            Point('species A', 30, 30),  # Should pass
            Point('species A', 50, 30),  # Should pass
            Point('species A', -30, -60),
        ]
        test_bounding_box = (0.0, 0.0, 180.0, 90.0)
        bbox_filter = get_bounding_box_filter(*test_bounding_box)
        filtered_points, filter_count = self._filter_points(bbox_filter, test_points)
        assert len(filtered_points) == 3
        assert filter_count == 2

    # .....................................
    def test_get_decimal_precision_filter(self):
        """Test the get_decimal_precision_filter function."""
        test_points = [
            Point('Species A', 10, 10),  # Should not pass
            Point('Species A', 10.0324, 9.23101),  # Should pass
            Point('Species A', 3.23421, 70.013),  # Should not pass
            Point('Species A', 60.23419, 40.10029),  # Should pass
            Point('Species A', 100.123, 19.33444),  # Should not pass
            Point('Species A', 1e-3, 1e-10),  # Should not pass
        ]
        decimal_filter = get_decimal_precision_filter(4)
        filtered_points, filter_count = self._filter_points(decimal_filter, test_points)
        assert len(filtered_points) == 2
        assert filter_count == 4

    # .....................................
    def test_get_attribute_filter(self):
        """Test the get_attribute_filter function."""
        test_points = [
            Point('species A', 10, 40, attributes={'flags': ['bad']}),
            # Should pass
            Point('species A', -10, 30, attributes={'flags': ['good']}),
            Point('species A', 30, 30, attributes={'flags': ['worse']}),
            Point('species A', 50, 30, attributes={'flags': 'bad'}),
            # Should pass
            Point('species A', -30, -60, attributes={'flags': ['good']}),
        ]

        def bad_filter(value):
            if isinstance(value, str):
                value = [value]
            return all([i not in ['bad', 'worse'] for i in list(value)])

        attribute_filter = get_attribute_filter('flags', bad_filter)
        filtered_points, filter_count = self._filter_points(
            attribute_filter, test_points
        )
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
            Point('species A', -30, -60),  # Should pass
        ]
        disjoint_filter = get_disjoint_geometries_filter(test_geometries)
        filtered_points, filter_count = self._filter_points(
            disjoint_filter, test_points
        )
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
            Point('species A', -30, -60),
        ]
        intersect_filter = get_intersect_geometries_filter(test_geometries)
        filtered_points, filter_count = self._filter_points(
            intersect_filter, test_points
        )
        assert len(filtered_points) == 1
        assert filter_count == 4

    # .....................................
    def test_get_minimum_points_filter(self):
        """Test the get_intersect_geometries_filter function."""
        test_points = [
            Point('species A', -10, 40),
            Point('species A', -10, 30),
            Point('species A', 30, 30),
            Point('species A', 50, 30),
            Point('species A', -30, -60),
        ]
        # Check when we have more than minimum
        min_points_filter = get_minimum_points_filter(1)
        filtered_points, filter_count = self._filter_points(
            min_points_filter, test_points
        )
        assert len(filtered_points) == len(test_points)
        assert filter_count == 0
        # Check when we have less than minimum
        min_points_filter = get_minimum_points_filter(len(test_points) + 10)
        filtered_points, filter_count = self._filter_points(
            min_points_filter, test_points
        )
        assert len(filtered_points) == 0
        assert filter_count == len(test_points)

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
            Point('species A', -30, -60),
        ]
        unique_localities_filter = get_unique_localities_filter()
        filtered_points, filter_count = self._filter_points(
            unique_localities_filter, test_points
        )
        assert len(filtered_points) == 5
        assert filter_count == 5

    # .....................................
    def test_multiple_filters(self):
        """Test multiple filters."""
        test_points = [
            Point('species A', 113, 57, attributes={'flags': ['good']}),  # A
            Point('species A', -49, -25, attributes={'flags': ['bad']}),  # B
            Point('species A', -49, -25, attributes={'flags': ['bad']}),  # C
            Point('species A', 168, -13, attributes={'flags': ['bad']}),  # D
            Point('species A', 114, 82, attributes={'flags': ['good']}),  # E
            Point('species A', -67, -63, attributes={'flags': ['worse']}),  # F
            Point('species A', 138, 81, attributes={'flags': ['worse']}),  # G
            Point('species A', 82, -88, attributes={'flags': ['good']}),  # H
            Point('species A', 82, -88, attributes={'flags': ['good']}),  # I
            Point('species A', -76, 55, attributes={'flags': ['good']}),  # J
            Point('species A', -76, 55, attributes={'flags': ['good']}),  # K
            Point('species A', -121, 82, attributes={'flags': ['good']}),  # L
            Point('species A', 58, -89, attributes={'flags': ['good']}),  # M
            Point('species A', 0, 0, attributes={'flags': ['good']}),  # N
        ]
        unique_localities_filter = get_unique_localities_filter()

        def bad_filter(value):
            return all([i not in ['bad', 'worse'] for i in list(value)])

        attribute_filter = get_attribute_filter('flags', bad_filter)
        bbox_filter = get_bounding_box_filter(-90, -90, 90, 90)
        disjoint_filter = get_disjoint_geometries_filter(
            ['POLYGON ((0 -10, 10 0, 0 10, -10 0, 0 -10))']
        )
        intersect_filter = get_intersect_geometries_filter(
            ['POLYGON ((-180 0, 0 0, 0 90, -180 90, -180 0))']
        )
        # Current points - ABCDEFGHIJKLMN
        filtered_points, filter_count = self._filter_points(
            unique_localities_filter, test_points
        )
        # Removed points - CIK
        assert len(filtered_points) == 11
        assert filter_count == 3

        # Current points - ABDEFGHJLMN
        filtered_points, filter_count = self._filter_points(
            attribute_filter, filtered_points
        )
        # Removed points - BDFG
        assert len(filtered_points) == 7
        assert filter_count == 4

        # Current points - AEHJLMN
        filtered_points, filter_count = self._filter_points(
            bbox_filter, filtered_points
        )
        # Removed points - AEL
        assert len(filtered_points) == 4
        assert filter_count == 3

        # Current points - HJMN
        filtered_points, filter_count = self._filter_points(
            disjoint_filter, filtered_points
        )
        # Removed points - N
        assert len(filtered_points) == 3
        assert filter_count == 1

        # Current points - J
        filtered_points, filter_count = self._filter_points(
            intersect_filter, filtered_points
        )
        # Removed points - HM
        assert len(filtered_points) == 1
        assert filter_count == 2

    # .....................................
    def test_no_valid_points(self):
        """Test when no points pass filter."""
        test_points = [Point('species A', 30, 30)]
        bbox_filter = get_bounding_box_filter(10, 10, 20, 20)
        filtered_points, filter_count = self._filter_points(bbox_filter, test_points)
        assert len(filtered_points) == 0
        assert filter_count == 1

    # ....................................
    def test_get_spatial_index_filter_from_scratch(self):
        """Test get_spatial_index_filter."""
        test_points = [
            Point('Species A', -10, -1),  # Should pass
            Point('Species A', 0, 0),  # Should pass
            Point('Species A', 30, 20),  # Should not pass
            Point('Species A', 40, 10),  # Should not pass
            Point('Species A', 10, 40),  # Should not pass
            Point('Species A', 30, 60),  # Should not pass
        ]

        def get_true_list(species_name):
            return [True]

        def get_true(hit, check_vals):
            return True

        sp_index = SpatialIndex()
        sp_index.add_feature(
            1, create_geometry_from_bbox(-10, -10, 10, 10), {'att_1': 'val_1'}
        )
        sp_index_filter = get_spatial_index_filter(sp_index, get_true_list, get_true)
        filtered_points, filter_count = self._filter_points(
            sp_index_filter, test_points
        )
        assert len(filtered_points) == 2
        assert filter_count == 4

    # ....................................
    def test_get_spatial_index_filter_from_file(self, generate_temp_filename):
        """Test get_spatial_index_filter.

        Args:
            generate_temp_filename (pytest.fixture): Fixture to generate filenames.
        """
        test_points = [
            Point('Species A', -10, -1),  # Should pass
            Point('Species A', 0, 0),  # Should pass
            Point('Species A', 30, 20),  # Should not pass
            Point('Species A', 40, 10),  # Should not pass
            Point('Species A', 10, 40),  # Should not pass
            Point('Species A', 30, 60),  # Should not pass
            Point('Species B', 0, 0),
        ]

        def get_species_intersection_func(species_name):
            if species_name == 'Species A':
                return [True]
            else:
                return None

        def get_true(hit, check_vals):
            return True

        temp_filename = generate_temp_filename()
        sp_index = SpatialIndex(temp_filename)
        sp_index.add_feature(
            1, create_geometry_from_bbox(-10, -10, 10, 10), {'att_1': 'val_1'}
        )
        sp_index.save()
        # sp_index.close()
        sp_index = None
        sp_index_filter = get_spatial_index_filter(
            temp_filename, get_species_intersection_func, get_true
        )
        filtered_points, filter_count = self._filter_points(
            sp_index_filter, test_points
        )
        assert len(filtered_points) == 7
        assert filter_count == 0
