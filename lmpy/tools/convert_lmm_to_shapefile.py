"""Convert a lmpy Matrix to a GeoJSON (.geojson) file."""
import argparse
import json
from logging import WARN
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.spatial.map import vectorize_geospatial_matrix
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = "Convert a lmpy Matrix to a shapefile."


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    parser = argparse.ArgumentParser(
        prog="convert_lmm_to_shapefile",
        description=DESCRIPTION,
    )
    parser.add_argument("--config_file", type=str, help="Path to configuration file.")
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the report."
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
        help="If provided, input matrix is a binary PAM."
    )
    parser.add_argument(
        "--geometry_type",
        "-g",
        type=str,
        choices=["point", "polygon"],
        default="polygon",
        help="The type of geometry to create in the shapefile.",
    )
    parser.add_argument(
        "in_lmm_filename", type=str,
        help="Filename of lmpy matrix (.lmm) containing a y/0 axis of sites, " +
             "to convert to polygons in a shapefile."
    )
    parser.add_argument(
        "out_shapefile",
        type=str,
        help="Location to write the converted matrix as a shapefile.",
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
    # if args.shapefile_filename is not None:
    #     errs = test_files((args.shapefile_filename, "Input shapefile"))
    #     all_missing_inputs.extend(errs)
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for converting LMM to GeoJSON.

    Raises:
        OSError: on failure to write to report_filename or geojson filename.
        IOError: on failure to write to report_filename.
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
    report = vectorize_geospatial_matrix(
        mtx, args.out_shapefile, create_polygon=(args.geometry_type == "polygon"),
        is_pam=args.is_pam, logger=logger)

    report["matrix_filename"] = args.in_lmm_filename
    report["out_shapefile"] = args.out_shapefile

    # If the output report was requested, write it
    if args.report_filename:
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
            f"Wrote report file to {args.report_filename}",
            refname=os.path.splitext(os.path.basename(__file__))[0])


# .....................................................................................
__all__ = ["build_parser", "cli"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()
