"""Split occurrence data files into groups for processing."""
import argparse
import json

from lmpy.data_preparation.occurrence_splitter import (
    DEFAULT_MAX_WRITERS,
    get_writer_key_from_fields_func,
    get_writer_filename_func,
    OccurrenceSplitter,
)
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.point import PointCsvReader, PointDwcaReader


# .....................................................................................
DESCRIPTION = '''\
Group and split occurrence data from one or more sources so that like-records (ex. \
species) can be processed together.'''


# .....................................................................................
def get_writer_filename_func(base_dir):
    """Get a function that returns a filename from a writer key.

    Args:
        base_dir (str): A base directory for all writers.

    Returns:
        Method: A function that returns a filename when given a writer key.
    """

    def get_writer_filename_from_key(writer_key):
        """Get a writer filename from a writer key and create directories if needed.

        Args:
            writer_key (str or list): A writer key to use to generate a filename.

        Returns:
            str: A file path to use for the writer.
        """
        try:
            writer_fn = '{}.csv'.format(os.path.join(base_dir, writer_key))
        except TypeError:  # Tried to join iterable
            writer_fn = '{}.csv'.format(os.path.join(base_dir, *writer_key))
        os.makedirs(os.path.dirname(writer_fn), exist_ok=True)
        return writer_fn

    return get_writer_filename_from_key


# .....................................................................................
def get_writer_key_from_fields_func(*fields):
    """Get a function that returns a writer key from fields of a point.

    Args:
        *fields (list): A list of fields to use to determine the Point's writer key.

    Returns:
        Method: A function that takes a Point as an argument and returns a key.
    """
    key_fields = list(fields)

    # .......................
    def key_from_fields_func(point):
        """Get a wrangler key for a point.

        Args:
            point (Point): A point object to get a writer key for.

        Returns:
            Object: An object representing the key for the particular point.
        """
        writer_key = [point.get_attribute(fld) for fld in key_fields]
        if len(writer_key) == 1:
            return writer_key[0]
        return writer_key

    return key_from_fields_func


# .....................................................................................
class OccurrenceSplitter:
    """A tool for splitting occurrence data by some criteria for easier processing."""

    # .......................
    def __init__(
        self,
        writer_key_func,
        writer_filename_func,
        write_fields=None,
        max_writers=DEFAULT_MAX_WRITERS,
    ):
        """Constructor.

        Args:
            writer_key_func (Method): A function for determining a writer to use.  It
                should take a Point as input and return a dictionary key.
            writer_filename_func (Method): A function to determine the file location
                to write data for a particular writer.  It should take a dictionary
                key and return a string.
            write_fields (list): A list of fields to write for each writer.  If None,
                use all fields in the first output Point object.
            max_writers (int): The maximum number of open writers (files) at any given
                time.
        """
        self.get_writer_key = writer_key_func
        self.get_writer_filename = writer_filename_func
        self.writer_fields = write_fields
        self.max_writers = max_writers
        self.writers = {}

    # .......................
    def __enter__(self):
        """Context manager magic method.

        Returns:
            OccurrenceSplitter: This instance.
        """
        return self

    # .......................
    def __exit__(self, *args):
        """Context manager magic method on exit.

        Args:
            *args: Position arguments passed to the method.
        """
        self.flush_writers()

    # .......................
    def flush_writers(self):
        """Close all open occurrence writers."""
        for writer in self.writers:
            writer.close()
        self.writers = {}

    # .......................
    def open_writer(self, writer_key):
        """Open an occurrence writer for the provided key.

        Args:
            writer_key (object): Some key that can be used to determine a writer.
        """
        # Flush or close writers if needed
        if len(self.writers) >= self.max_writers:
            self.flush_writers
        # Open the new writer
        self.writers[writer_key] = PointCsvWriter(
            self.get_writer_filename(writer_key), self.writer_fields
        )
        self.writers[writer_key].open()

    # .......................
    def process_reader(self, reader, wranglers):
        """Process an occurrence reader.

        Args:
            reader (PointCsvReader or PointDwcaReader): An occurrence reader instance.
            wranglers (list): A list of occurrence data wranglers.
        """
        reader.open()
        for points in reader:
            for wrangler in wranglers:
                if points:
                    points = wrangler(points)
            if points:
                self.write_points(points)
        reader.close()

    # .......................
    def write_points(self, points):
        """Write points using the appropriate writer.

        Args:
            points (list): A list of point objects to write to file.
        """
        if points:
            writer_key = self.get_writer_key(points[0])
            if writer_key not in self.writers.keys():
                if self.writer_fields is None:
                    self.writer_fields = list(points[0].attributes.keys())
                self.open_writer(writer_key)
            self.writers[writer_key].write_points(points)


# .....................................................................................
def cli():
    """Command-line interface for splitting occurrence datasets."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '-m',
        '--max_open_writers',
        type=int,
        default=DEFAULT_MAX_WRITERS,
        choices=range(1, 500),
        metavar='[1 - 500]',
        help=(
            'The maximum number of data writers to have open at once. '
            'Too many open files can cause errors. '
            'Default: {}.'.format(DEFAULT_MAX_WRITERS)
        ),
    )
    parser.add_argument(
        '-k',
        '--key_field',
        action='append',
        type=str,
        help=(
            'A field to use to determine writer key.  Multiple values can be used to '
            'utilize multiple fields.'
        ),
    )
    parser.add_argument(
        '-of',
        '--out_field',
        action='append',
        type=str,
        help=(
            'Include this field in the outputs.  If not provided, all fields from the '
            'first point ready for output will be used.'
        ),
    )
    parser.add_argument(
        '--dwca',
        action='append',
        nargs=2,
        help='A Darwin-Core Archive to process and associated wrangler configuration.',
    )
    parser.add_argument(
        '--csv',
        action='append',
        nargs=5,
        help=(
            'A CSV file to process, an associated wrangler configuration file, '
            'a species header key, an x header key, and a y header key.'
        ),
    )

    parser.add_argument(
        'out_dir',
        type=str,
        help='Directory where the output data should be written.',
    )
    args = parser.parse_args()

    # Establish functions for getting writer key and filename
    writer_key_func = get_writer_key_from_fields_func(*tuple(args.key_field))
    writer_filename_func = get_writer_filename_func(args.out_dir)

    # Determine fields to write
    write_fields = None
    if args.out_field is not None:
        write_fields = args.out_field

    # Wrangler Factory
    wrangler_factory = WranglerFactory()

    # Initialize processor
    with OccurrenceSplitter(
        writer_key_func,
        writer_filename_func,
        write_fields=write_fields,
        max_writers=args.max_open_writers,
    ) as occurrence_processor:
        # For each dwca file
        if args.dwca:
            for dwca_fn, wranglers_fn in args.dwca:
                reader = PointDwcaReader(dwca_fn)
                with open(wranglers_fn, mode='rt') as in_json:
                    wranglers = wrangler_factory.get_wranglers(json.load(in_json))
                occurrence_processor.process_reader(reader, wranglers)
        if args.csv:
            # For each csv file
            for csv_fn, wranglers_fn, sp_key, x_key, y_key in args.csv:
                reader = PointCsvReader(csv_fn, sp_key, x_key, y_key)
                with open(wranglers_fn, mode='rt') as in_json:
                    wranglers = wrangler_factory.get_wranglers(json.load(in_json))
                occurrence_processor.process_reader(reader, wranglers)


# .....................................................................................
__all__ = ['cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
