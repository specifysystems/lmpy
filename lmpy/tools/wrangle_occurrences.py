"""This tool cleans occurrence records according to the wranglers specified."""
import argparse
import json
import os.path

from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.point import PointCsvReader, PointCsvWriter
from lmpy.tools._config_parser import _process_arguments, get_logger, test_files


# .....................................................................................
DESCRIPTION = 'Clean (filter / modify) occurrence records using data wranglers.'


# .....................................................................................
def clean_data(reader, writer_filename, wranglers, write_fields=None, log_output=False):
    """Clean occurrence data.

    Args:
        reader (PointCsvReader): A reader object that generates Point objects.
        writer_filename (str): A file location to write cleaned points.
        wranglers (list of Wranglers): A list of data wranglers that manipulate
            and / or filter Points for cleaning.
        write_fields (list or None): A list of Point attributes to write to output CSV.
            If None, determine from first cleaned Point.
        log_output (bool): Should output be logged to console.

    Returns:
        dict: Output report from data wrangling.
    """
    if log_output:

        def log_msg(msg):
            print(msg)

    else:

        def log_msg(msg):
            pass

    report = {
        'input_records': 0,
        'output_records': 0,
        'wranglers': [wrangler.get_report() for wrangler in wranglers],
    }
    # Open reader
    reader.open()
    writer = None
    for points in reader:
        report['input_records'] += len(points)
        for wrangler in wranglers:
            wrangler_name = wrangler.name
            # If there are points, wrangle them
            if points:
                in_count = len(points)
                sp_name = points[0].species_name
                points = wrangler.wrangle_points(points)
                if in_count - len(points) > 0:
                    log_msg(
                        f"{wrangler_name} removed {in_count - len(points)} {sp_name}"
                        + " points")
        # If any points are left, write them
        if points:
            report['output_records'] += len(points)
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
    return report


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='wrangle_occurrences',
        description=DESCRIPTION,
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-sp',
        '--species_key',
        type=str,
        default='species_name',
        help='The CSV column header for species name.',
    )
    parser.add_argument(
        '-x',
        '--x_key',
        type=str,
        default='x',
        help='The CSV column header for the X (longitude) field.',
    )
    parser.add_argument(
        '-y',
        '--y_key',
        type=str,
        default='y',
        help='The CSV column header for the Y (latitude) field.',
    )
    parser.add_argument(
        '-r',
        '--report_filename',
        type=str,
        help='File location to write optional output report JSON.',
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
        'reader_filename', type=str, help='Input occurrence CSV filename.'
    )
    parser.add_argument(
        'writer_filename', type=str, help='Output cleaned occurrence CSV filename.'
    )
    parser.add_argument(
        'wrangler_config_filename', type=str, help='Wrangler(s) configuration file.'
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
    all_missing_inputs = test_files((args.reader_filename, "Occurrence CSV input"))
    all_missing_inputs.extend(
        test_files((args.wrangler_config_filename, "Wrangler configuration")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """A command-line interface to the tool.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    args = _process_arguments(parser, 'config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = get_logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )
    from logging import INFO
    logger.log(INFO, f"Starting {script_name}")

    # Get wranglers
    wrangler_factory = WranglerFactory(logger=logger)
    with open(args.wrangler_config_filename, mode='rt') as in_json:
        wranglers = wrangler_factory.get_wranglers(json.load(in_json))

    # Get reader
    reader = PointCsvReader(
        args.reader_filename, args.species_key, args.x_key, args.y_key
    )

    # Clean data
    report = clean_data(
        reader, args.writer_filename, wranglers, log_output=args.log_console
    )

    # If the output report was requested, write it
    if args.report_filename:
        try:
            with open(args.report_filename, mode='wt') as out_file:
                json.dump(report, out_file, indent=4)
        except OSError:
            raise
        except IOError:
            raise


# .....................................................................................
__all__ = ['build_parser', 'clean_data', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
