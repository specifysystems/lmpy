"""This tool aggregates matrices by concatenating or adding."""
import argparse

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
        '--ndim',
        type=int,
        help='The number of dimensions in the output matrix for sum.',
        default=-1
    )
    parser.add_argument(
        'method',
        choices=['add', 'concatenate'],
        type=str,
        help='Method to use to aggregate the matrices.'
    )
    parser.add_argument(
        'axis',
        type=int,
        help='The axis to aggregate matrices on.'
    )
    parser.add_argument(
        'output_matrix_filename',
        type=str,
        help='Path to write out the aggregated matrices.'
    )
    parser.add_argument(
        'input_matrix_filename',
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
    out_matrix = None
    input_matrices = [Matrix.load(fn) for fn in args.input_matrix_filename]
    if args.method == 'add':
        if args.ndim > 0:
            n_dims = args.ndim
        else:
            n_dims = min(mtx.ndim for mtx in input_matrices)
        for mtx in input_matrices:
            if mtx.ndim > n_dims:
                mtx = mtx.sum(axis=-1)
            if out_matrix is None:
                out_matrix = Matrix(mtx)
            else:
                out_matrix += mtx
    else:
        out_matrix = Matrix.concatenate(input_matrices, axis=args.axis)
    out_matrix.write(args.output_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
