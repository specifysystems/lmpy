"""Split occurrence data files into groups for processing."""
import argparse
import json
import os

from lmpy.data_preparation.occurrence_splitter import (
    DEFAULT_MAX_WRITERS,
    get_writer_key_from_fields_func,
    get_writer_filename_func,
    OccurrenceSplitter,
)
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.log import Logger
from lmpy.point import Point, PointCsvReader, PointDwcaReader
from lmpy.tools._config_parser import _process_arguments, test_files


# .....................................................................................
DESCRIPTION = '''\
Group and split occurrence data from one or more sources so that like-records (ex. \
species) can be processed together.'''


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='split_occurrence_data',
        description=DESCRIPTION,
    )
    parser.add_argument(
        '--config_file',
        type=str,
        help='Configuration file containing script arguments.'
    )
    parser.add_argument(
        '--log_filename',
        '-l',
        type=str,
        help='A file location to write logging data.'
    )
    parser.add_argument(
        '--log_console',
        action='store_true',
        default=False,
        help='If provided, write log to console.'
    )
    parser.add_argument(
        '-r',
        '--report_filename',
        type=str,
        help='File location to write the wrangler report.'
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
        '--species_list_filename',
        type=str,
        help='File location to write list of species seen (after wrangling).'
    )

    parser.add_argument(
        'out_dir',
        type=str,
        help='Directory where the output data should be written.',
    )
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = []
    if args.dwca:
        for dwca_fn, wranglers_fn in args.dwca:
            errs = test_files(
                (dwca_fn, "DwCA input"),
                (wranglers_fn, "Occurrence Wrangler configuration"))
            all_missing_inputs.extend(errs)
    if args.csv:
        # For each csv file
        for csv_fn, wranglers_fn, _, _, _ in args.csv:
            errs = test_files(
                (csv_fn, "CSV data"),
                (wranglers_fn, "Occurrence Wrangler configuration"))
            all_missing_inputs.extend(errs)
    return all_missing_inputs


# .....................................................................................
def cli():
    """Command-line interface for splitting occurrence datasets.

    Raises:
        Exception: on failure to load wranglers
        OSError: on failure to write to report filename
        IOError: on failure to write to report filename
    """
    parser = build_parser()
    args = _process_arguments(parser, 'config_file')

    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    # Default key field is 'species_name'
    if args.key_field is None:
        args.key_field = [Point.SPECIES_ATTRIBUTE]

    # Establish functions for getting writer key and filename
    writer_key_func = get_writer_key_from_fields_func(*tuple(args.key_field))
    writer_filename_func = get_writer_filename_func(args.out_dir)

    # Determine fields to write
    write_fields = None
    if args.out_field is not None:
        write_fields = args.out_field

    # Wrangler Factory
    wrangler_factory = WranglerFactory(logger=logger)

    full_report = {}

    # Initialize processor
    with OccurrenceSplitter(
        writer_key_func,
        writer_filename_func,
        write_fields=write_fields,
        max_writers=args.max_open_writers,
        logger=logger
    ) as occurrence_processor:
        # For each dwca file
        if args.dwca:
            for dwca_fn, wranglers_fn in args.dwca:
                reader = PointDwcaReader(dwca_fn)
                try:
                    with open(wranglers_fn, mode='rt') as in_json:
                        wranglers = wrangler_factory.get_wranglers(json.load(in_json))
                except Exception:
                    raise
                curr_report = occurrence_processor.process_reader(reader, wranglers)
                full_report[dwca_fn] = curr_report

        # For each csv file
        if args.csv:
            for csv_fn, wranglers_fn, sp_key, x_key, y_key in args.csv:
                reader = PointCsvReader(csv_fn, sp_key, x_key, y_key)
                with open(wranglers_fn, mode='rt') as in_json:
                    try:
                        wranglers = wrangler_factory.get_wranglers(json.load(in_json))
                    except Exception:
                        raise
                    curr_report = occurrence_processor.process_reader(reader, wranglers)
                    full_report[csv_fn] = curr_report

        if args.species_list_filename:
            occurrence_processor.write_species_list(args.species_list_filename)

        # If the output report was requested, write it
        if args.report_filename:
            # Add final species list to report
            species_seen = occurrence_processor.get_species_seen()
            full_report['species_count'] = len(species_seen)
            full_report['species_list'] = species_seen
            try:
                with open(args.report_filename, mode='wt') as out_file:
                    json.dump(full_report, out_file, indent=4)
            except OSError:
                raise
            except IOError:
                raise


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
