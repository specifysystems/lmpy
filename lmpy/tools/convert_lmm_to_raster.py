"""Convert a lmpy Matrix to a GeoJSON (.geojson) file."""
import argparse
import json
import logging
from logging import WARN
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.spatial.map import (rasterize_matrix)
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = "Convert a lmpy Matrix to a raster geotiff file."


# ...................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    parser = argparse.ArgumentParser(
        prog="convert_lmm_to_raster",
        description=DESCRIPTION,
    )
    parser.add_argument("--config_file", type=str, help="Path to configuration file.")
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the wrangler report."
    )
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
        "--column",
        type=str,
        help=("Header of column to map."),
    )
    parser.add_argument(
        "in_lmm_filename", type=str,
        help="Filename of lmpy matrix (.lmm) containing a y/0 axis of sites, " +
             "to convert to raster in geotiff format.  Note that the maximumn number" +
             "of layers is 256"
    )
    parser.add_argument(
        "out_geotiff_filename",
        type=str,
        help="Location to write the converted matrix into multi-band raster.",
    )
    return parser


# ...................................................................................
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


# ...................................................................................
def cli():
    """Provide a command-line tool for converting LMM to GeoJSON.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.'

    Todo: Test this fully
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg="config_file")
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit("\n".join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )
    logger.log(
        f"Beware: {script_name} has not been fully tested", refname=script_name,
        log_level=WARN)

    mtx = Matrix.load(args.in_lmm_filename)
    col_headers = mtx.get_column_headers()
    if args.column is not None:
        if args.column in col_headers:
            report = rasterize_matrix(
                mtx, args.out_geotiff_filename, column=args.column, logger=logger)

        else:
            logger.log(
                f"Column name {args.column} is not present in matrix " +
                f"{args.in_lmm_filename} columns {col_headers}", refname=script_name,
                log_level=logging.ERROR)
            print("Errors, exiting program")

    # If the output report was requested, write it
    if args.report_filename:
        report["matrix_filename"] = args.in_lmm_filename
        try:
            with open(args.report_filename, mode="wt") as out_file:
                json.dump(report, out_file, indent=4)
        except OSError:
            raise
        except IOError:
            raise
        except Exception as err:
            print(err)
            raise
        logger.log(
            f"Wrote report file to {args.report_filename}", refname=script_name)


# .....................................................................................
__all__ = ["build_parser", "cli"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()
