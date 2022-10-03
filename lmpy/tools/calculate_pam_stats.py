"""Tool for creating PAM statistics."""
import argparse
import json
import os

from lmpy.log import Logger
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
        if len(args.tree_matrix) != 3:
            all_missing_inputs.append(
                "Tree matrix option requires 3 matrix files: tree, node heights" +
                "and tip lengths")
        else:
            all_missing_inputs.extend(
                test_files((args.tree_matrix[1], "Node heights matrix file")))
            all_missing_inputs.extend(
                test_files((args.tree_matrix[2], "Tip lengths matrix file")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for computing statistics.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()

    args = _process_arguments(parser, 'config_file')
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
    logger.log(
        f"Calculate statistics for PAM {args.pam_filename}.", refname=script_name)

    report = {
        "pam_filename": args.pam_filename
    }

    tree = tree_matrix = node_heights_matrix = tip_lengths_matrix = None
    pam = Matrix.load(args.pam_filename)
    if args.tree_filename is not None:
        tree = TreeWrapper.from_filename(args.tree_filename)
        report["tree_filename"] = args.tree_filename

    if args.tree_matrix is not None:
        tree_matrix = Matrix.load(args.tree_matrix[0])
        node_heights_matrix = Matrix.load(args.tree_matrix[1])
        tip_lengths_matrix = Matrix.load(args.tree_matrix[2])
        # Add to report
        report["input tree_matrix"] = args.tree_matrix[0]
        report["input tip_lengths_matrix"] = args.tree_matrix[1]
        report["input tree_filename"] = args.tree_matrix[2]

    stats = PamStats(
        pam,
        tree=tree,
        tree_matrix=tree_matrix,
        node_heights_matrix=node_heights_matrix,
        tip_lengths_matrix=tip_lengths_matrix,
        logger=logger
    )

    # Write requested stats
    if args.covariance_matrix is not None:
        pth, fname = os.path.split(args.covariance_matrix)
        basename, ext = os.path.splitext(fname)
        covariance_stats = stats.calculate_covariance_statistics()
        for name, mtx in covariance_stats:
            fn = os.path.join(pth, f"{basename}_{name.replace(' ', '_')}{ext}")
            mtx.write(fn)
            logger.log(
                f"Wrote covariance {name} statistics to {fn}.", refname=script_name)
            report[f"output covariance matrix {name}"] = fn
        # with open(args.covariance_matrix, mode='wt') as f:
        #     json.dump(covariance_stats, f)

    if args.diversity_matrix is not None:
        diversity_stats = stats.calculate_diversity_statistics()
        diversity_stats.write(args.diversity_matrix)
        logger.log(
            f"Wrote diversity statistics to {args.diversity_matrix}.",
            refname=script_name)
        report["output diversity_matrix"] = args.diversity_matrix

    if args.site_stats_matrix is not None:
        site_stats = stats.calculate_site_statistics()
        site_stats.write(args.site_stats_matrix)
        logger.log(
            f"Wrote site statistics to {args.site_stats_matrix}.",
            refname=script_name)
        report["output site_stats_matrix"] = args.site_stats_matrix

    if args.species_stats_matrix is not None:
        species_stats = stats.calculate_species_statistics()
        species_stats.write(args.species_stats_matrix)
        logger.log(
            f"Wrote species statistics to {args.species_stats_matrix}.",
            refname=script_name)
        report["output species_stats_matrix"] = args.species_stats_matrix

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
