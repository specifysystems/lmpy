"""Convert a lmpy Matrix to a GeoJSON (.geojson) file."""
import argparse
import json
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.spatial.geojsonify import (
    geojsonify_matrix, geojsonify_matrix_with_shapefile,
)
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = 'Convert a lmpy Matrix to a GeoJSON file.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='convert_lmm_to_geojson',
        description=DESCRIPTION,
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-r',
        '--report_filename',
        type=str,
        help='File location to write the wrangler report.'
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
        '--shapefile_filename',
        '-s',
        type=str,
        help=(
            'Path to a shapefile that can be used to generate polygons matching '
            'matrix sites.'
        ),
    )
    parser.add_argument(
        '--resolution',
        type=float,
        help=(
            'Resolution of the polygons in the GeoJSON if a shapefile was not provided.'
            'Otherwise, use points.'
        ),
    )
    parser.add_argument(
        '--omit_value',
        '-o',
        action='append',
        nargs='*',
        type=float,
        help='Properties should be omitted if they have this value for a site.'
    )
    parser.add_argument(
        'in_lmm_filename', type=str, help='Lmpy .lmm filename to convert to GeoJSON.'
    )
    parser.add_argument(
        'out_geojson_filename',
        type=str,
        help='Location to write the converted matrix GeoJSON.',
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
    all_missing_inputs = test_files((args.in_lmm_filename, "Matrix input"))
    if args.shapefile_filename is not None:
        errs = test_files((args.shapefile_filename, "Input shapefile"))
        all_missing_inputs.extend(errs)
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for converting LMM to GeoJSON.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
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

    mtx = Matrix.load(args.in_lmm_filename)
    if args.shapefile_filename is not None:
        report = geojsonify_matrix_with_shapefile(
            mtx, args.shapefile_filename, args.out_geojson_filename,
            omit_values=args.omit_value, logger=logger
        )
    else:
        report = geojsonify_matrix(
            mtx, args.out_geojson_filename, resolution=args.resolution,
            omit_values=args.omit_value, logger=logger
        )
    report["matrix_filename"] = args.in_lmm_filename

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
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
