"""This module contains tools for transforming raw occurrence data."""
import csv
from operator import itemgetter

from lmpy import Point


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
                    species_name_getter(pt_rec), x_getter(pt_rec),
                    y_getter(pt_rec), flags_getter(pt_rec)))
        except (IndexError, KeyError):
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

    if flags_getter:
        if isinstance(flags_getter, int):
            flags_getter = itemgetter(flags_getter)
    else:
        flag_getter = none_getter

    with open(filename) as in_file:
        if headers:
            _ = next(in_file)
        reader = csv.reader(in_file, delimiter=delimiter)
        points = _get_points_for_generator(
            reader, itemgetter(species_index), itemgetter(x_index),
            itemgetter(y_index), flag_getter)
    return points


# .............................................................................
def convert_json_to_point(json_obj, point_iterator=iter, species_name_getter,
                          x_getter, y_getter, flags_getter=none_getter):
    """Get a list of Points from a JSON object.

    Args:
        json_obj (dict or list): A JSON object to get point records from.
        point_iterator: An iterator function to pull records from the JSON
            object.
        species_name_getter: A function for getting species name from a record.
        x_getter: A function for getting the 'x' value from a record.
        y_getter: A function for getting the 'y' value from a record.
        flags_getter: A function for getting the 'flags' value from a record.

    Returns:
        list of Point named tuples
    """
    points = _get_points_for_generator(
        point_iterator(json_obj), species_name_getter, x_getter, y_getter,
        flags_getter)
    return points


# .............................................................................
def none_getter(obj):
    """Return None as a function.

    Returns:
        None - Always returns None.
    """
    return None
