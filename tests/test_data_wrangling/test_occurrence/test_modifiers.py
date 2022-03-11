"""Test the occurrence data wrangler modifiers module."""
from copy import deepcopy
import tempfile

import numpy as np

from lmpy import Point
from lmpy.data_wrangling.occurrence.modifiers import (
    get_accepted_name_modifier,
    get_attribute_modifier,
    get_common_format_modifier,
    get_coordinate_converter_modifier,
)


# ............................................................................
class Test_get_accepted_name_modifier:
    """Test get_accepted_name_modifier."""

    # .......................
    def test_simple(self):
        """Simple test that attribute values change as expected."""
        points = [
            Point('Oldname a1', 10, 20),
            Point('Oldname a2', 20, 30),
            Point('Newname a', -10, 0),
            Point('Oldname b', 30, 30),
        ]

        with tempfile.NamedTemporaryFile(
            mode='wt', encoding='utf8', delete=False
        ) as temp_out:
            temp_out.write('Name,Accepted name\n')
            temp_out.write('Oldname a1,Newname a\n')
            temp_out.write('Oldname a2,Newname a\n')
            temp_out.write('Newname a,Newname a')
            temp_filename = temp_out.name

        modifier = get_accepted_name_modifier(temp_filename)
        new_points = modifier(points)
        assert len(new_points) == 3
        new_points_2 = modifier(points[0])
        assert len(new_points_2) == 1


# ............................................................................
class Test_get_attribute_modifier:
    """Test get_attribute_modifier."""

    # .......................
    def test_simple(self):
        """Simple test that attribute values change as expected."""
        points = [
            Point('species 1', 10, 20, attributes={'val': 0}),
            Point('species 1', 20, 30, attributes={'val': 9}),
            Point('species 2', -10, 0, attributes={'val': -3}),
        ]

        def val_modify_func(orig_val):
            return orig_val + 1

        modifier = get_attribute_modifier('val', val_modify_func)
        new_points = modifier(points)
        test_orig = sorted(p.get_attribute('val') + 1 for p in points)
        test_new = sorted(p.get_attribute('val') for p in new_points)
        assert test_orig == test_new


# ............................................................................
class Test_get_common_format_modifier:
    """Test get_common_format_modifier."""

    # .......................
    def test_simple(self):
        """Simple test that attribute names can be changed by modifier."""
        old_att = 'old_att'
        new_att = 'new_att'
        points = [
            Point('species 1', 1, 1, attributes={old_att: 1}),
            Point('species 2', 2, 2, attributes={old_att: 2}),
            Point('species 3', 3, 3, attributes={old_att: 3}),
        ]
        modifier = get_common_format_modifier({old_att: new_att})
        new_points = modifier(points)
        for pt in new_points:
            assert pt.get_attribute(old_att) is None
            assert isinstance(pt.get_attribute(new_att), int)


# .............................................................................
class Test_get_coordinate_converter_modifier:
    """Test get_coordinate_converter_modifier."""

    # ..........................
    # def test_specific_values(self):
    #     """Test that conversion produces known values."""
    #     in_vals = (4326, -89.555857, 37.3040553)
    #     # out_vals = (2815, 333699.36, 163612.51)
    #     out_vals = (3857, -9907434.68, 4439106.79)
    #     converter = get_coordinate_converter_modifier(
    #       in_vals[0], out_vals[0])
    #     in_point = Point('test species', in_vals[1], in_vals[2])
    #     out_point = converter(in_point)[0]
    #     print(
    #         'out_point.x {}, out_vals[1], {}'.format(
    #           out_point.x, out_vals[1]))
    #     assert np.isclose(out_point.x, out_vals[1])
    #     assert np.isclose(out_point.y, out_vals[2])
    #     assert in_point.species_name == out_point.species_name

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
            converter = get_coordinate_converter_modifier(src_epsg, target_epsg)
            in_points = converter(in_points)
            src_epsg = target_epsg
        final_converter = get_coordinate_converter_modifier(src_epsg, in_vals[0])
        final_point = final_converter(in_points)[0]
        assert np.isclose(final_point.x, original_point.x)
        assert np.isclose(final_point.y, original_point.y)
        assert final_point.species_name == original_point.species_name
