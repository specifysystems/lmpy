"""This tool aggregates matrices by concatenating or adding."""
import argparse

import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Aggregate matrices.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='aggregate_matrices',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        'method',
        choices=['add', 'concatenate'],
        type=str,
        help='Method to use to aggregate the matrices.'
    )
    parser.add_argument(
        'out_matrix_filename',
        type=str,
        help='Path to write out the aggregated matrices.'
    )
    parser.add_argument(
        'input_matrix',
        type=str,
        nargs='+',
        help='Path to input matrix to aggregate.'
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for aggregating matrices."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    if args.method == 'add':
        out_matrix = np.sum(
            [Matrix.load(fn) for fn in args.input_matrix],
            axis=args.axis
        )
    else:
        out_matrix = Matrix.concatenate(
            [Matrix.load(fn) for fn in args.input_matrix],
            axis=args.axis
        )
    out_matrix.write(args.out_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
