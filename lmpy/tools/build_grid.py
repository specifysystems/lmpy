"""Tool for building grid shapefiles."""
import argparse
import json
import os
import sqlite3

from lmpy.data_preparation.build_grid import build_grid
from lmpy.log import Logger
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = '''\
Build a grid shapefile that is used to define the sites of a PAM or other \
multivariate Matrix for lmpy operations.'''


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='build_grid', description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        "--log_filename",
        "-l",
        type=str,
        help="A file location to write logging data."
    )
    parser.add_argument(
        "--log_console",
        action="store_true",
        default=False,
        help="If provided, write log to console."
    )
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the wrangler report."
    )
    parser.add_argument(
        'grid_filename',
        type=str,
        help='File location to write grid shapefile.',
    )
    parser.add_argument('min_x', type=float, help='The minimum x value for the grid.')
    parser.add_argument('min_y', type=float, help='The minimum y value for the grid.')
    parser.add_argument('max_x', type=float, help='The maximum x value for the grid.')
    parser.add_argument('max_y', type=float, help='The maximum y value for the grid.')
    parser.add_argument(
        'cell_size',
        type=float,
        help='The resolution of each grid cell (in EPSG map units).',
    )
    parser.add_argument(
        'epsg', type=int, help='The EPSG code (map projection) for the grid.'
    )
    return parser


# .....................................................................................
def _test_epsg_code(code):
    err = None
    proj_db_file = "/usr/share/proj/proj.db"
    if not os.path.exists(proj_db_file):
        from osgeo import osr
        err = f"Missing proj4 database {proj_db_file}"

    conn = sqlite3.connect(proj_db_file)
    cursor = conn.cursor()
    q = "select code from crs_view where auth_name = 'EPSG'"
    results = cursor.execute(q).fetchall()
    valid_codes = [int(row[0]) for row in results]
    if code not in valid_codes:
        ver = f"{osr.GetPROJVersionMajor()}.{osr.GetPROJVersionMinor()}"
        err = f"Code {code} os not a valid EPSG code in proj4 version {ver}"
    return err


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_errors = []
    if args.min_x >= args.max_x or args.min_y >= args.max_y:
        all_errors.append(
            f'Illegal bounds: ({args.min_x}, {args.min_y}, {args.max_x}, {args.max_y})')
    err = _test_epsg_code(args.epsg)
    if err is not None:
        all_errors.append(err)
    return all_errors


# .....................................................................................
def cli():
    """Command-line interface to build grid.

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

    cell_sides = 4  # Add this to parameters if we enable hexagons again
    report = build_grid(
        args.grid_filename,
        args.min_x,
        args.min_y,
        args.max_x,
        args.max_y,
        args.cell_size,
        args.epsg,
        cell_sides,
        logger=logger
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
        logger.log(f"Wrote report file to {args.report_filename}")


# .....................................................................................
__all__ = ['build_parser', 'build_grid', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
