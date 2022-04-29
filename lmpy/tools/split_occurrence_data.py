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
def _process_arguments(parser):
    """Process arguments including filling in those provided by configuration file.

    Args:
        parser (argparse.ArgumentParser): An argparse.ArgumentParser with parameters.

    Returns:
        argparse.Namespace: An augmented Namespace with any parameters specified in a
            configuration file.
    """
    args = parser.parse_args()

    if args.config_file is not None:
        with open(args.config_file, mode='rt') as in_json:
            config = json.load(in_json)
            if 'csv' in config.keys():
                if not isinstance(config['csv'], list):
                    config['csv'] = [config['csv']]
                if args.csv is None:
                    args.csv = []
                args.csv.extend(config['csv'])
            if 'dwca' in config.keys():
                if args.dwca is None:
                    args.dwca = []
                args.dwca.extend(config['dwca'])

    return args


# .....................................................................................
def cli():
    """Command-line interface for splitting occurrence datasets."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '--config_file',
        type=str,
        help='Configuration file containing script arguments.'
    )
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
        'out_dir', type=str, help='Directory where the output data should be written.'
    )
    args = _process_arguments(parser)

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
