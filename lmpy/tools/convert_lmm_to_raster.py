"""Convert a lmpy Matrix to a GeoJSON (.geojson) file."""
import argparse
import json
import logging
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.spatial.map import (
    is_flattened_geospatial_matrix, rasterize_flattened_matrix)
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
        "--is_pam",
        action="store_true",
        default=False,
        help="If provided, input matrix is binary, and output raster will be written " +
             "with values stored as bytes."
    )
    parser.add_argument(
        "--column",
        action="append",
        type=str,
        help=("Header of one or more columns to map into a multi-band Geotiff file. "
              "If not provided, the first 256 columns will be added."),
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
    return all_missing_inputs


# ...................................................................................
def cli():
    """Provide a command-line tool for converting one or all columns in LMM to Raster.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.'

    Note:
        * Assumes the input is a matrix with sites as rows, identified by row_headers
    site_id, x_coordinate, y_coordinate.  Columns may be any site properties, such
    as species data, statistics, or other.
        * The number of output bands for a raster may be limited to 256, because
    the "bandnum" argument in
    https://trac.osgeo.org/postgis/browser/trunk/raster/rt_core/librtcore.h
    is defined as uint8 (0-255).  Yes, this is postgis, no I'm not certain.

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
        f"***Create raster image for matrix {args.in_lmm_filename}",
        refname=script_name)

    mtx = Matrix.load(args.in_lmm_filename)
    if is_flattened_geospatial_matrix(mtx):
        column_headers = mtx.get_column_headers()
        if args.column is None:
            columns = column_headers
        else:
            columns = []
            for col in args.column:
                if col in column_headers:
                    columns.append(col)
                else:
                    logger.log(
                        f"Error: column {col} is not present in matrix " +
                        f"{args.in_lmm_filename}, ignoring",
                        refname=script_name, log_level=logging.WARN)
            if len(columns) == 0:
                msg = (
                    f"No valid columns in {args.column} present in matrix " +
                    f"{args.in_lmm_filename}")
                logger.log(msg, refname=script_name, log_level=logging.ERROR)
                exit(msg)
            elif len(columns) > 256:
                columns = columns[:256]
                logger.log(
                    "Beware: creating a raster image only for the first 256 of "
                    f"{len(columns)} bands.", refname=script_name,
                    log_level=logging.WARN)

        report = rasterize_flattened_matrix(
            mtx, args.out_geotiff_filename, columns=columns, is_pam=args.is_pam,
            logger=logger)

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
