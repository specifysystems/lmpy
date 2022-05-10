"""Calculate p-values for observed values compared to those generated from random."""
import argparse

from lmpy.matrix import Matrix
from lmpy.statistics.significance import (
    compare_absolute_values,
    compare_signed_values,
    get_significant_values,
    PermutationTests,
    SignificanceMethod,
)
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Calculate p-values for observed data compared with random.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='calculate_p_values',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-m',
        '--significance_method',
        dest='significance_method',
        type=str,
        choices=['bonferroni', 'fdr', 'raw'],
        default='raw',
        help=(
            'If provided, correct the p-values using the Bonferroni method (bonferroni)'
            'or Benjamini and Hochberg method (fdr).'
        ),
    )
    parser.add_argument(
        '--num_permutations',
        '-n',
        type=int,
        help=(
            'The total number of random iterations used (useful if only computing'
            'p-values for a subset of randomizations).'
        ),
    )
    parser.add_argument(
        '--abs',
        action='store_true',
        help='Compare absolute values instead of signed values.'
    )
    parser.add_argument(
        '--alpha',
        type=float,
        default=0.05,
        help='Alpha value for statistical significance or False Discovery Rate.',
    )
    parser.add_argument(
        '-s',
        '--significance_matrix_filename',
        dest='significance_matrix_filename',
        type=str,
        help='Path to write significance matrix.'
    )
    parser.add_argument(
        'p_values_matrix',
        type=str,
        help='Path to write the computed p-values matrix.'
    )
    parser.add_argument(
        'observed_matrix',
        type=str,
        help='Path to the observed data matrix.',
    )
    parser.add_argument(
        'random_matrix',
        type=str,
        nargs='+',
        help='Path to the random data matrix.',
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for calculating p-values."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    # Compare method
    if args.abs:
        compare_func = compare_absolute_values
    else:
        compare_func = compare_signed_values
    # Load observed matrix
    obs = Matrix.load(args.observed_matrix)
    # Create running stats
    perm_testing = PermutationTests(obs, compare_fn=compare_func)
    # For each random matrix
    for rand_mtx_filename in args.random_matrix:
        # Load matrix
        rand_mtx = Matrix.load(rand_mtx_filename)
        # Add to running stats
        perm_testing.add_permutation(rand_mtx)
    # Get p-values, scaled if desired
    p_values = perm_testing.get_p_values(num_iterations=args.num_permutations)
    # If correction, do it
    # Write p-values matrix
    p_values.write(args.p_values_matrix)
    # Write significant matrix if desired
    if args.significance_matrix_filename is not None:
        if args.significance_method == 'raw':
            sig_method = SignificanceMethod.RAW
        elif args.significance_method == 'fdr':
            sig_method = SignificanceMethod.FDR
        else:
            sig_method = SignificanceMethod.BONFERRONI
        sig_mtx = get_significant_values(
            p_values,
            alpha=args.alpha,
            correction_method=sig_method,
        )
        sig_mtx.write(args.significance_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
