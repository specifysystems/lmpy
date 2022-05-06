"""This tool cleans occurrence records according to the wranglers specified."""
import argparse
import json

from lmpy.data_wrangling.occurrence.factory import wrangler_factory
from lmpy.point import PointCsvReader, PointCsvWriter


# .....................................................................................
def clean_data(
    reader, writer_filename, wranglers, write_fields=None, log_output=False
):
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
        'wranglers': {wrangler_name: {'removed': 0} for wrangler_name, _ in wranglers}
    }
    # Open reader
    reader.open()
    writer = None
    for points in reader:
        report['input_records'] += len(points)
        for wrangler_name, wrangler in wranglers:
            # If there are points, wrangle them
            if points:
                tmp = len(points)
                sp_name = points[0].species_name
                points = wrangler(points)
                report['wranglers'][wrangler_name]['removed'] += tmp - len(points)
                log_msg(f'{wrangler_name} removed {tmp - len(points)} {sp_name} points')
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
        '-r', '--report_filename', type=str,
        help='File location to write optional output report JSON.'
    )
    parser.add_argument(
        '-l', '--log_output', action='store_true', default=False,
        help='Should output messages be written to console.'
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
    report = clean_data(
        reader, args.writer_filename, wranglers, log_output=args.log_output
    )

    # If the output report was requested, write it
    if args.report_filename:
        with open(args.report_filename, mode='wt') as out_file:
            json.dump(report, out_file, indent=4)


# .....................................................................................
__all__ = ['clean_data', 'cli']


# .....................................................................................
if __name__ == '__main__':
    cli()
