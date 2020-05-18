"""Module containing various filtering functions."""
import os
from osgeo import ogr


# .............................................................................
def get_bounding_box_filter(min_x, min_y, max_x, max_y):
    """Get a filter function for the specified bounding box.

    Args:
        x_index (str or int): The index of the 'x' value for each point.
        y_index (str or int): The index of the 'y' value for each point.
        min_x (numeric): The minimum 'x' value for the bounding box.
        min_y (numeric): The minimum 'y' value for the bounding box.
        max_x (numeric): The maximum 'x' value for the bounding box.
        max_y (numeric): The maximum 'y' value for the bounding box.

    Returns:
        function - A function that takes a point as input and returns a boolean
            output indicating if the point is valid according to this filter.
    """
    # .......................
    def bounding_box_filter(point):
        """Bounding box filter function."""
        return (min_x <= point.x <= max_x and
                min_y <= point.y <= max_y)
    return bounding_box_filter


# .............................................................................
def get_data_flag_filter(filter_flags):
    """Get a filter function for the specified flags.

    Args:
        flag_field_index (str or int): The index of the flag field for each
            point.
        filter_flags (list): A list of flag values that should be considered to
            be invalid.

    Returns:
        function - A function that takes a point as input and returns a boolean
            output indicating if the point is valid according to this filter.
    """
    # .......................
    def flag_filter(point):
        """Data flag filter function."""
        test_flags = point.flags
        if not isinstance(test_flags, (list, tuple)):
            test_flags = [test_flags]
        return not any([flag in filter_flags for flag in test_flags])
    return flag_filter


# .............................................................................
def get_disjoint_geometries_filter(geometry_wkts):
    """Get a filter function for disjoint geometries.

    Args:
        geometries (list of ogr.Geometry): A list of geometries to check for
            intersection.

    Returns:
        function - A function that takes a point as input and returns a boolean
            output indicating if the point is valid according to this filter.
    """
    geometries = []
    for wkt in geometry_wkts:
        geometries.append(ogr.CreateGeometryFromWkt(wkt))

    # .......................
    def disjoint_geometry_filter(point):
        """Intersect geometry filter function."""
        point_geometry = ogr.Geometry(ogr.wkbPoint)
        point_geometry.AddPoint(point.x, point.y)
        return all(
            [geom.Intersection(
                point_geometry).IsEmpty() for geom in geometries])
    return disjoint_geometry_filter


# .............................................................................
def get_intersect_geometries_filter(geometry_wkts):
    """Get a filter function for intersecting the provided geometries.

    Args:
        geometries (list of ogr.Geometry): A list of geometries to check for
            intersection.

    Returns:
        function - A function that takes a point as input and returns a boolean
            output indicating if the point is valid according to this filter.
    """
    geometries = []
    for wkt in geometry_wkts:
        geometries.append(ogr.CreateGeometryFromWkt(wkt))

    # .......................
    def intersect_geometry_filter(point):
        """Intersect geometry filter function."""
        point_geometry = ogr.Geometry(ogr.wkbPoint)
        point_geometry.AddPoint(point.x, point.y)
        return any(
            [not geom.Intersection(
                point_geometry).IsEmpty() for geom in geometries])
    return intersect_geometry_filter


# .............................................................................
def get_unique_localities_filter():
    """Get a filter function that only allows unique (x, y) values.

    Returns:
        function - A function that takes a point as input and returns a boolean
            output indicating if the point is valid according to this filter.
    """
    unique_values = []

    # .......................
    def unique_localities_filter(point):
        """Unique localities filter function."""
        test_val = (point.x, point.y)
        if test_val in unique_values:
            return False
        unique_values.append(test_val)
        return True
    return unique_localities_filter


# .............................................................................
__all__ = ['get_bounding_box_filter', 'get_data_flag_filter',
           'get_disjoint_geometries_filter', 'get_intersect_geometries_filter',
           'get_unique_localities_filter']
