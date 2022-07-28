"""Tool for creating PAM statistics."""
import argparse
import json

from lmpy.matrix import Matrix
from lmpy.statistics.pam_stats import PamStats
from lmpy.tools._config_parser import _process_arguments, test_files
from lmpy.tree import TreeWrapper


DESCRIPTION = 'Compute statistics for a PAM and optionally a tree.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='calculate_pam_stats',
        description=DESCRIPTION,
    )
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
    parser.add_argument('--tree_filename', type=str, help='Path to matching tree.')
    parser.add_argument(
        '--tree_matrix', type=str, nargs=3, help='Path to tree matrix.'
    )

    # Output matrices
    parser.add_argument(
        '--covariance_matrix',
        type=str,
        help='Path to write covariance matrix if desired.',
    )
    parser.add_argument(
        '--diversity_matrix',
        type=str,
        help='Path to write diversity matrix if desired.',
    )
    parser.add_argument(
        '--site_stats_matrix',
        type=str,
        help='Path to write site statistics matrix if desired.',
    )
    parser.add_argument(
        '--species_stats_matrix',
        type=str,
        help='Path to write species statistics matrix if desired.',
    )

    # PAM
    parser.add_argument('pam_filename', type=str, help='Path to PAM file.')
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = test_files((args.pam_filename, "PAM file"))
    if args.tree_filename is not None:
        all_missing_inputs.extend(test_files((args.tree_filename, "Tree file")))
    if args.tree_matrix is not None:
        all_missing_inputs.extend(test_files((args.tree_matrix[0], "Tree matrix file")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for computing statistics."""
    parser = build_parser()

    args = _process_arguments(parser, 'config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    tree = tree_matrix = node_heights_matrix = tip_lengths_matrix = None
    pam = Matrix.load(args.pam_filename)
    if args.tree_filename is not None:
        tree = TreeWrapper.from_filename(args.tree_filename)

    if args.tree_matrix is not None:
        tree_matrix = Matrix.load(args.tree_matrix[0])
        node_heights_matrix = Matrix.load(args.tree_matrix[1])
        tip_lengths_matrix = Matrix.load(args.tree_matrix[2])

    stats = PamStats(
        pam,
        tree=tree,
        tree_matrix=tree_matrix,
        node_heights_matrix=node_heights_matrix,
        tip_lengths_matrix=tip_lengths_matrix,
    )

    # Write requested stats
    if args.covariance_matrix is not None:
        with open(args.covariance_matrix, mode='wt') as out_json:
            json.dump(stats.calculate_covariance_statistics(), out_json)

    if args.diversity_matrix is not None:
        stats.calculate_diversity_statistics().write(args.diversity_matrix)

    if args.site_stats_matrix is not None:
        stats.calculate_site_statistics().write(args.site_stats_matrix)

    if args.species_stats_matrix is not None:
        stats.calculate_species_statistics().write(args.species_stats_matrix)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
