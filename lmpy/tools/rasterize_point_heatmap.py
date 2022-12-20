"""Create a point heatmap image."""
import argparse
import json
import os

from lmpy.log import Logger
from lmpy.spatial.map import create_point_heatmap_matrix, rasterize_map_matrices
from lmpy.point import PointCsvReader, PointDwcaReader
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = "Create a point map image."


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    parser = argparse.ArgumentParser(
        prog="create_point_heatmap",
        description=DESCRIPTION
    )
    # The "--config_file" argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument("--config_file", type=str, help="Path to configuration file.")
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
        help="If provided, write logging statements to the console."
    )
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the summary report."
    )
    parser.add_argument(
        "--dwca",
        action="append",
        help="A Darwin-Core Archive filename to process.",
    )
    parser.add_argument(
        "--csv",
        action="append",
        nargs=4,
        help=(
            "A CSV file to process, a species header key, an x header key, "
            "and a y header key."
        ),
    )
    parser.add_argument(
        "raster_filename",
        type=str,
        help="A file path to write the raster geotiff file.",
    )
    parser.add_argument(
        "min_x",
        type=float,
        help="The minimum x value of the plot map range."
    )
    parser.add_argument(
        "min_y",
        type=float,
        help="The minimum y value of the plot map range."
    )
    parser.add_argument(
        "max_x",
        type=float,
        help="The maximum x value of the plot map range."
    )
    parser.add_argument(
        "max_y",
        type=float,
        help="The maximum y value of the plot map range."
    )
    parser.add_argument(
        "resolution",
        type=float,
        help="The resolution of each cell of the plot map."
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
    if args.dwca is not None:
        for dwca_fn in args.dwca:
            all_missing_inputs.extend(test_files((dwca_fn, "DwCA file")))
    if args.csv is not None:
        for csv_fn, _, _, _ in args.csv:
            all_missing_inputs.extend(test_files((csv_fn, "CSV file")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a point heatmap.

    Raises:
        ValueError: Raised if neither a CSV or DWCA is provided.
        OSError: on failure to write to report_filename.
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
        f"\n\n ***Create heatmap for points in raster {args.raster_filename}",
        refname=script_name)

    readers = []
    if args.dwca is not None:
        for dwca_fn in args.dwca:
            readers.append(PointDwcaReader(dwca_fn))
    if args.csv is not None:
        for csv_fn, sp_key, x_key, y_key in args.csv:
            readers.append(PointCsvReader(csv_fn, sp_key, x_key, y_key))
    if len(readers) == 0:
        raise ValueError("Must provide at least one CSV and / or DWCA.")

    point_heatmap, report = create_point_heatmap_matrix(
        readers, args.min_x, args.min_y, args.max_x, args.max_y, args.resolution,
        logger=logger)
    matrices = {"points": point_heatmap}
    report2 = rasterize_map_matrices(matrices, args.raster_filename, logger=logger)
    report.update(report2)
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
            f"Wrote report file to {args.report_filename}", refname=script_name)


# .....................................................................................
__all__ = ["build_parser", "cli"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()