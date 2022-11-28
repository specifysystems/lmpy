"""Create a stat heatmap image."""
import argparse

import numpy as np

from lmpy.matrix import Matrix
from lmpy.plots.map import create_stat_heatmap_matrix, plot_matrix
from lmpy.statistics.pam_stats import PamStats
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = "Create a site-statistic heatmap image."


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
        "-b",
        "--base_layer",
        type=str,
        help="An optional base layer image for the plot.  Must have same extent.",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        help="A title to add to the plot image."
    )
    parser.add_argument(
        "--cmap",
        type=str,
        default="Reds",
        help="A color map to use for the image."
    )
    parser.add_argument(
        "--vmin",
        type=float,
        help="The minimum value for color scaling."
    )
    parser.add_argument(
        "--vmax",
        type=float,
        help="The maximum value for color scaling (use -1 to use maximum from data)."
    )
    parser.add_argument(
        "--mask_matrix",
        type=str,
        help="File path to a binary matrix to use as a mask."
    )

    parser.add_argument(
        "plot_filename",
        type=str,
        help="A file path to write the generated plot image.",
    )
    parser.add_argument(
        "matrix_filename",
        type=str,
        help=(
            f"The file path of the site-statistic matrix (of type {mtx_types}) " +
            "containing a statistic to map.")
    )
    parser.add_argument(
        "statistic",
        type=str,
        choices=stat_names,
        help=stat_help
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
    all_missing_inputs = test_files((args.matrix_filename, "Matrix input"))
    if args.mask_matrix is not None:
        all_missing_inputs.extend(test_files((args.mask_matrix, "Mask Matrix")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a site-statistic heatmap.

    Raises:
        Exception: on statistic not present in matrix column headers.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg="config_file")
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit("\n".join(errs))

    matrix = Matrix.load(args.matrix_filename)
    stat_names = matrix.get_column_headers()
    if args.statistic not in stat_names:
        raise Exception(
            f"Matrix {args.matrix_filename} does not contain column {args.statistic} " +
            f"available columns are {stat_names}"
        )
    if args.mask_matrix is not None:
        mask_matrix = Matrix.load(args.mask_matrix)
        matrix = Matrix(
            np.ma.masked_where(mask_matrix == 0, matrix),
            headers=matrix.get_headers()
        )
    matrix_heatmap = create_stat_heatmap_matrix(
        matrix,
        args.statistic,
        args.min_x,
        args.min_y,
        args.max_x,
        args.max_y,
        args.resolution
    )
    plot_matrix(
        args.plot_filename,
        matrix_heatmap,
        base_layer=args.base_layer,
        extent=(args.min_x, args.max_x, args.min_y, args.max_y),
        mask_val=0,
        title=args.title,
        cmap=args.cmap,
        vmin=args.vmin,
        vmax=args.vmax,
    )


# .....................................................................................
__all__ = ["build_parser", "cli"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()
