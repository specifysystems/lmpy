"""This module contains tools for transforming raw occurrence data."""
import csv
import sys

from lmpy.point import PointCsvReader


max_int = sys.maxsize
while True:
    # Decrease max_int value by factor of 10 if overflow
    try:
        csv.field_size_limit(max_int)
        break
    except OverflowError:  # pragma: no cover
        max_int = int(max_int / 10)


# .............................................................................
def get_chunk_key(value, group_position, group_size, filler_char='a'):
    """Get the chunk key from the value.

    Args:
        value (str): The value to pull the chunk key from.
        group_position (int): The position of the group chunk.
        group_size (int): The number of characters that comprises the group.
        filler_char (str): What to use for filler characters in case the group chunk is
            less than the desired number of characters.

    Returns:
        str: The group chunk key from the value.
    """
    value += 10 * filler_char
    return value[group_size * group_position:group_size * (group_position + 1)].lower()


# .............................................................................
def sort_points(readers, writer, wranglers=None):
    """Sort and clean occurrence points.

    Args:
        readers (:obj:`list` of :obj:`PointReader): A list of point readers.
        writer (PointWriter): A point writer to output points.
        wranglers (list of DataWranglers): An optional list of data wranglers
            to use to modify / filter points.
    """
    # Make sure readers is a list
    if isinstance(readers, PointCsvReader):
        readers = [readers]
    in_points = []
    # Sort points
    for reader in readers:
        for points in reader:
            in_points.extend(points)
    sorted_points = sorted(in_points)
    in_points = None
    # Filter if desired
    if wranglers:
        for flt in wranglers:
            if sorted_points:
                sorted_points = flt(sorted_points)
    # Write points
    writer.write_points(sorted_points)


# .............................................................................
def split_points(
    readers,
    writers,
    group_attribute,
    group_size,
    group_position,
    wranglers=None
):
    """Split points in the readers into smaller chunks for easier processing.

    Args:
        readers (:obj:`list` of :obj:`PointReader): A list of point readers.
        writers (dict): A dictionary of {combo: PointWriter} used for writing
            points.
        group_attribute (str): The Point attribute to be used to determine
            which group the Point belongs to.
        group_size (int): How many characters to use for determining group.
        group_position (int): Starting character index to use for determining
            group.
        wranglers (list of DataWranglers): An optional list of data wranglers
            to use to modify / filter points.

    Note:
        group_attribute should be used when instantiating the Point readers.
    """
    for reader in readers:
        for points in reader:
            # Assume all points returned go into the same group
            location_key = get_chunk_key(
                points[0].get_attribute(group_attribute), group_position,
                group_size)
            if wranglers:
                for flt in wranglers:
                    if points:
                        points = flt(points)
            writers[location_key].write_points(points)


# .............................................................................
def wrangle_points(readers, writer, wranglers=None):
    """Wrangle input points and write output points.

    Args:
        readers (:obj:`list` of :obj:`PointReader): A list of point readers.
        writer (PointWriter): A point writer to output points.
        wranglers (list of DataWranglers): An optional list of data wranglers
            to use to modify / filter points.
    """
    # Make sure readers is a list
    if isinstance(readers, PointCsvReader):
        readers = [readers]
    for reader in readers:
        for points in reader:
            if wranglers:
                for flt in wranglers:
                    if points:
                        points = flt(points)
            # Write wrangled points
            writer.write_points(points)


# .............................................................................
__all__ = ['get_chunk_key', 'sort_points', 'split_points', 'wrangle_points']
