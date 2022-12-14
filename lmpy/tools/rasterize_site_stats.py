"""Create a stat heatmap image.

This tool takes a column of a statistic matrix, representing sites for one
statistic, and puts them back into a 2-d matrix representing the sites as
a map, with values for the statistic in each cell.
"""
import argparse
import json
import os

from lmpy.log import Logger
from lmpy.matrix import Matrix
from lmpy.spatial.map import create_map_matrix_for_column, rasterize_map_matrices
from lmpy.statistics.pam_stats import PamStats
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = "Create a site-statistic raster file."


# .....................................................................................
def get_site_statistic_info():
    site_stat_matrix_types = [
        "covariance_stats", "site_matrix_stats", "site_tree_stats",
        "site_tree_distance_matrix_stats", "site_pam_dist_mtx_stats"]
    available_stats = {}
    for mt in site_stat_matrix_types:
        if mt == "covariance_stats":
            available_stats[mt] = ["sigma sites"]
        else:
            available_stats[mt] = [name for name, _ in getattr(PamStats, mt)]
    stat_names = []
    help_lines = [
        "The name of the statistic (must match column header) in the matrix.",
        "For each site-statistic matrix, its statistics columns are:"]
    for mt, stat_names in available_stats.items():
        help_lines.append(f"   {mt}: {stat_names}")
        stat_names.extend(stat_names)
    return "\n".join(help_lines), stat_names, site_stat_matrix_types


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    stat_help, stat_names, mtx_types = get_site_statistic_info()
    parser = argparse.ArgumentParser(
        prog="create_stat_heatmap",
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
        "--statistic",
        type=str,
        choices=stat_names,
        default=None,
        help=stat_help
    )
    parser.add_argument(
        "matrix_filename",
        type=str,
        help=(
            f"The file path of the site-statistic matrix (of type {mtx_types}) " +
            "containing one or all statistics to map.")
    )
    parser.add_argument(
        "raster_filename",
        type=str,
        help="A file path to write the generated geotiff image"
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
    all_missing_inputs = test_files((args.matrix_filename, "Matrix input"))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a site-statistic heatmap.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    try:
        args = _process_arguments(parser, config_arg="config_file")
    except FileNotFoundError as e:
        print("Missing file, exiting program")
        exit(f"{str(e)}")

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
        f"***Create raster image for matrix {args.matrix_filename}",
        refname=script_name)

    matrix = Matrix.load(args.matrix_filename)
    stat_names = matrix.get_column_headers()
    if args.statistic is not None:
        if args.statistic not in stat_names:
            msg = (f"Matrix {args.matrix_filename} does not contain  " +
                   f"column {args.statistic}available columns are {stat_names}")
            logger.log(msg, refname=script_name)
            print("Errors, exiting program")
            exit(msg)
    else:
        stat_names = [args.statistic]

    report = {"input_matrix": args.matrix_filename}

    logger.log(f"  and statistic(s) {stat_names}", refname=script_name)
    report["statistics"] = stat_names
    stat_matrices = {}
    for stat in stat_names:
        map_matrix, report = create_map_matrix_for_column(matrix, args.statistic)
        stat_matrices[stat] = map_matrix

    curr_rpt = rasterize_map_matrices(
        stat_matrices, args.raster_filename, logger=logger)
    report.update(curr_rpt)

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
