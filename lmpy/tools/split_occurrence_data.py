"""Split occurrence data files into groups for processing."""
import argparse
import os

from lmpy.point import PointCsvReader, PointCsvWriter, PointDwcaReader


# .....................................................................................
DEFAULT_MAX_WRITERS = 100

DESCRIPTION = '''\
Group and split occurrence data from one or more sources so that like-records (ex. \
species) can be processed together.'''


# .....................................................................................
class OccurrenceSplitter:
    """A tool for splitting occurrence data by some criteria for easier processing."""
    # .......................
    def __init__(
        self, writer_key_func,
        writer_filename_func,
        write_fields=None,
        max_writers=DEFAULT_MAX_WRITERS
    ):
        """Constructor."""
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
    """Comman-line interface for splitting occurrence datasets."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '--dwca_file',
        action='append',
        nargs=2,
        help='A Darwin-Core Archive to process and associated wrangler configuration.'
    )
    parser.add_argument(
        '--csv_file',
        action='append',
        nargs=5,
        help=(
            'A CSV file to process, an associated wrangler configuration file, '
            'a species header key, an x header key, and a y header key.'
        )
    )

    parser.add_argument(
        'out_dir',
        type=str,
        help='Directory where the output data should be written.'
    )
    args = parser.parse_args()


# .....................................................................................
__all__ = ['cli']


# .....................................................................................
if __name__ == '__main__':
    cli()
