"""Split occurrence data files into groups for processing."""
import argparse
import os

from lmpy.point import PointCsvReader, PointCsvWriter, PointDwcaReader


DESCRIPTION = '''\
Group and split occurrence data from one or more sources so that like-records (ex. \
species) can be processed together.'''


"""
Split once? recurse?
Determine how to split, use entire field value? multiple fields? split single field?
How to process each incoming file
Maybe limit number of open writers?  Close as needed, reopen and append?
"""

"""
For each file
   read data
   for each data chunk
       wrangle
       split
       write points and or flush
"""






"""
First round of each of the readers
For _ in depth -1
   split reader
   catalog next depth readers
For final depth readers
   sort and split by group field
"""
def get_species_filename(species_name):
    """Get a filename to write data to for the provided species name.

    Args:
        species_name (str): The name of a species to get a file path for.

    Returns:
        str: A file path that can be used to write specimen records.
    """


# .....................................................................................
def split_readers(readers_and_wranglers, out_dir, chunk_start, chunk_size):
    """Split and wrangle one or more readers into smaller chunks.

    Args:
        readers_and_wranglers (list of tuples): A list of tuples, each containing a
            point reader and a list of point data wranglers.
        out_dir (str): A directory where the output files should be written to.
        chunk_start (int): The index of the first character to use for chunking.
        chunk_size (int): The number of characters to use to determine chunk.

    Returns:
        list of str: A list of output files created.
    """
    writers = {}
    writer_filenames = []

    for reader, wranglers in readers_and_wranglers:
        reader.open()
        for points in reader:
            wrangled_points = wrangle_points(points)
            if len(wrangled_points) > 0:
                chunk = (
                    wrangled_points[0].species_name + 'aaaaaaaaaaaaaa'
                )[chunk_start:chunk_start+chunk_size]
                if chunk not in writers.keys():
                    # If we don't already have a writer for this chunk, create one
                    chunk_fn = os.path.join(out_dir, '{}.csv'.format(chunk))
                    writers[chunk] = PointCsvWriter(chunk_fn, write_fields)
                    writers[chunk].open()
                    writer_filenames.append(chunk_fn)
                writers[chunk].write_points(wrangled_points)
        reader.close()

    # Close writers
    for writer in writers.values():
        writer.close()

    return writer_filenames


# .....................................................................................
def sort_and_split(filename, write_fields, get_species_filename_func):
    """Perform a final sort and split of a file into the individual groups.

    Args:
        filename (str): A file of occurrence records to split into final groups.
        write_fields (list of str): A list of attributes to write to file.
    """
    all_points = []
    # Read all points
    with PointCsvReader(filename, 'species_name', 'x', 'y') as reader:
        for points in reader:
            all_points.extend(points)
    # Sort points on species name
    all_points.sort(key=lambda pt: pt.species_name)
    # Get and write point groups
    curr_species = all_points[0].species_name
    sp_points = []
    for pt in all_points:
        if pt.species_name != curr_species:
            # Write points
            # - Get filename
            sp_filename = get_species_filename_func(curr_species)
            with PointCsvWriter(sp_filename, write_fields) as writer:
                writer.write_points(sp_points)
            # Reset sp_points and curr_species
            curr_species = pt.species_name
            sp_points = []
        # Always add pt to sp_points
        sp_points.append(pt)
    # Write last points
    sp_filename = get_species_filename_func(curr_species)
    with PointCsvWriter(sp_filename, write_fields) as writer:
        writer.write_points(sp_points)


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
        '--num_chars',
        '-n',
        type=int,
        default=2,
        help='The number of characters to use for each split group.'
    )
    parser.add_argument(
        '--depth',
        '-d',
        type=int,
        default=2,
        help='How many group levels deep to split.'
    )
    parser.add_argument(
        '--num_procs',
        '-p',
        type=int,
        default=1,
        help='The maximum number of parallel processes to use (when possible).'
    )

    parser.add_argument(
        'out_dir',
        type=str,
        help='Directory where the output data should be written.'
    )
    args = parser.parse_args()


# .....................................................................................
__all__ = []


# .....................................................................................
if __name__ == '__main__':
    cli()
