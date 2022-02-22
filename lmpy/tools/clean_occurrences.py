"""This tool cleans occurrence records according to the wranglers specified."""
import argparse
import json

from lmpy.data_wrangling.occurrence.factory import wrangler_factory
from lmpy.point import PointCsvReader, PointCsvWriter


# .....................................................................................
def clean_data(reader, writer_filename, wranglers, write_fields=None):
    """Clean occurrence data.

    Args:
        reader (PointCsvReader): A reader object that generates Point objects.
        writer_filename (str): A file location to write cleaned points.
        wranglers (list of Wranglers): A list of data wranglers that manipulate
            and / or filter Points for cleaning.
        write_fields (list or None): A list of Point attributes to write to output CSV.
            If None, determine from first cleaned Point.
    """
    # Open reader
    reader.open()
    writer = None
    for points in reader:
        for wrangler in wranglers:
            # If there are points, wrangle them
            if points:
                points = wrangler(points)
        # If any points are left, write them
        if points:
            if writer is None:
                if write_fields is None:
                    write_fields = points[0].get_attribute_names()
                writer = PointCsvWriter(writer_filename, write_fields)
                writer.open()
            writer.write_points(points)
    # Close reader and writer
    reader.close()
    if writer:
        writer.close()


# .....................................................................................
def cli():
    """A command-line interface to the tool."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-sp', '--species_key', type=str, default='species_name',
        help='The CSV column header for species name.'
    )
    parser.add_argument(
        '-x', '--x_key', type=str, default='x',
        help='The CSV column header for the X (longitude) field.'
    )
    parser.add_argument(
        '-y', '--y_key', type=str, default='y',
        help='The CSV column header for the Y (latitude) field.'
    )
    parser.add_argument(
        'reader_filename', type=str, help='Input occurrence CSV filename.'
    )
    parser.add_argument(
        'writer_filename', type=str, help='Output cleaned occurrence CSV filename.'
    )
    parser.add_argument(
        'wrangler_config_filename', type=str, help='Wrangler(s) configuration file.'
    )
    args = parser.parse_args()

    # Get wranglers
    wranglers = wrangler_factory(
        json.load(open(args.wrangler_config_filename, mode='rt'))
    )

    # Get reader
    reader = PointCsvReader(
        args.reader_filename, args.species_key, args.x_key, args.y_key
    )

    # Clean data
    clean_data(reader, args.writer_filename, wranglers)


# .....................................................................................
__all__ = ['clean_data', 'cli']


# .....................................................................................
if __name__ == '__main__':
    cli()
