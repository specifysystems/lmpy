"""Module containing occurrence data wranglers for modifying point data."""
from copy import deepcopy

from lmpy.point import Point
from lmpy.data_wrangling.occurrence.common import get_occurrence_map, make_list


# .............................................................................
def get_attribute_modifier(att_name, replace_func):
    """Get a function that replaces an Point attribute using a replace func.

    Args:
        att_name (str): The point attribute to modify.
        replace_func (method): A method that returns a replacement value.

    Returns:
        function(point): A function that takes a list of points and returns
            points with the coordinates converted.
    """
    # .......................
    def modify_func(point):
        old_val = point.get_attribute(att_name)
        new_pt = deepcopy(point)
        new_pt.set_attribute(att_name, replace_func(old_val))
        return new_pt

    return get_occurrence_map(modify_func)


# .............................................................................
def get_common_format_modifier(attribute_map):
    """Get a function to convert points to a common format (common attributes).

    Args:
        attribute_map (dict): A map of current attribute name to new attribute
            name.

    Returns:
        function(point): A function that takes a list of points and returns
            points with the coordinates converted.
    """
    # .......................
    def modify_func(point):
        new_pt = Point(
            point.species_name, point.x, point.y,
            attributes={
                new_name: point.get_attribute(old_name)
                    for old_name, new_name in attribute_map.items()})
        return new_pt

    return get_occurrence_map(modify_func)


# .............................................................................
def get_coordinate_converter_modifier(in_epsg, out_epsg):
    """Get a function to convert points from one coordinate system to another.

    Args:
        in_epsg (int): The EPSG code of the incoming points.
        out_epsg (int): The target EPSG code for output points.

    Returns:
        function(point): A function that takes a list of points and returns
            points with the coordinates converted.
    """
    source = osr.SpatialReference()
    source.ImportFromEPSG(in_epsg)
    target = osr.SpatialReference()
    target.ImportFromEPSG(out_epsg)

    transform = osr.CoordinateTransformation(source, target)

    # .......................
    def converter_func(point):
        geom = ogr.CreateGeometryFromWkt(
            'POINT ({} {})'.format(point.x, point.y))
        geom.Transform(transform)
        pt = deepcopy(point)
        pt.x = geom.GetX()
        pt.y = geom.GetY()
        return pt

    return get_occurrence_map(converter_func)
