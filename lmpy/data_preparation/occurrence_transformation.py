"""This module contains tools for transforming raw occurrence data."""
import csv
from operator import itemgetter

from osgeo import ogr, osr

from lmpy import Point


# .............................................................................
def none_getter(obj):
    """Return None as a function.

    Returns:
        None - Always returns None.
    """
    return None


# .............................................................................
def _get_points_for_generator(rec_generator, species_name_getter, x_getter,
                              y_getter, flags_getter):
    """Get a list of Points from a specimen record generator.

    Args:
        rec_generator: A generator function that generates point records.
        species_name_getter: A function for getting species name from a record.
        x_getter: A function for getting the 'x' value from a record.
        y_getter: A function for getting the 'y' value from a record.
        flags_getter: A function for getting the 'flags' value from a record.

    Returns:
        list of Point named tuples
    """
    points = []
    for pt_rec in rec_generator:
        try:
            points.append(
                Point(
                    species_name_getter(pt_rec), float(x_getter(pt_rec)),
                    float(y_getter(pt_rec)), flags_getter(pt_rec)))
        except (IndexError, KeyError):  # pragma: no cover
            print('Could not extract required fields from {}'.format(pt_rec))
    return points


# .............................................................................
def convert_delimited_to_point(filename, species_getter, x_getter, y_getter,
                               flags_getter=none_getter, delimiter=', ',
                               headers=True):
    """Convert a file of delimited data into points.

    Args:
        filename (str): A path to a file of delimited data.
        species_getter (function or int): A method to get the species name or
            a column index in a delimited file.
        x_getter (function or int): A method to get the point x value or a
            column index in a delimited file.
        y_getter (function or int): A method to get the point y value or a
            column index in a delimited file.
        flags_getter (function or int): A method to get the point flags or a
            column index in a delimited file.
        delimiter (str): The delimiter of the delimited data.
        headers (bool): Does the file have a header row.

    Returns:
        list of Point objects
    """
    if isinstance(species_getter, int):
        species_getter = itemgetter(species_getter)

    if isinstance(x_getter, int):
        x_getter = itemgetter(x_getter)

    if isinstance(y_getter, int):
        y_getter = itemgetter(y_getter)

    with open(filename) as in_file:
        if headers:
            _ = next(in_file)
        reader = csv.reader(in_file, delimiter=delimiter)
        points = _get_points_for_generator(
            reader, species_getter, x_getter, y_getter, flags_getter)
    return points


# .............................................................................
def convert_json_to_point(json_obj, species_name_getter, x_getter, y_getter,
                          flags_getter=none_getter, point_iterator=iter):
    """Get a list of Points from a JSON object.

    Args:
        json_obj (dict or list): A JSON object to get point records from.
        species_name_getter: A function for getting species name from a record.
        x_getter: A function for getting the 'x' value from a record.
        y_getter: A function for getting the 'y' value from a record.
        flags_getter: A function for getting the 'flags' value from a record.
        point_iterator: An iterator function to pull records from the JSON
            object.

    Returns:
        list of Point named tuples
    """
    points = _get_points_for_generator(
        point_iterator(json_obj), species_name_getter, x_getter, y_getter,
        flags_getter)
    return points


# .............................................................................
def get_coordinate_converter(in_epsg, out_epsg):
    """Get a function to convert points from one coordinate system to another.

    Args:
        in_epsg (int): The EPSG code of the incoming points.
        out_epsg (int): The target EPSG code for output points.

    Returns:
        function(point): A function that takes a point and returns a new point
            with the coordinates converted.
    """
    source = osr.SpatialReference()
    source.ImportFromEPSG(in_epsg)
    target = osr.SpatialReference()
    target.ImportFromEPSG(out_epsg)

    transform = osr.CoordinateTransformation(source, target)

    def converter_func(point):
        geom = ogr.CreateGeometryFromWkt(
            'POINT ({} {})'.format(point.x, point.y))
        geom.Transform(transform)
        return Point(
            point.species_name, geom.GetX(), geom.GetY(), flags=point.flags)

    return converter_func


# .............................................................................
__all__ = ['convert_delimited_to_point', 'convert_json_to_point',
           'get_coordinate_converter', 'none_getter']
