"""Tool for wrangling a Matrix."""
import argparse

import json

from lmpy import Matrix
from lmpy.data_wrangling.factory import wrangler_factory


DESCRIPTION = '''\
Perform various wrangle operations on a matrix such as subsetting and reordering.'''


# .....................................................................................
def wrangle_matrix(mtx, wranglers):
    """Wrangle the Matrix as configured.

    Args:
        mtx (Matrix): A Matrix to wrangle.
        wranglers (list): A list of tree data wranglers.

    Returns:
        Matrix: The modified Matrix object.
    """
    wrangled_mtx = mtx
    return wrangled_mtx


# .....................................................................................
def cli():
    """Provice a command-line interface to the wrangle matrix tool."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'in_matrix_filename', type=str, help='Path to the input Matrix.'
    )
    parser.add_argument(
        'wrangler_configuration_file',
        type=str,
        help='Path to Matrix wrangler configuration.',
    )
    parser.add_argument(
        'out_matrix_filename', type=str, help='Path to the outut Matrix.'
    )
    args = parser.parse_args()

    in_mtx = Matrix.load(args.in_matrix_filename)
    with open(args.wrangler_configuration_file, mode='rt') as in_json:
        wranglers = wrangler_factory(json.load(in_json))

    wrangled_mtx = wrangle_matrix(in_mtx, wranglers)
    wrangled_mtx.write(args.out_matrix_filename)


# .....................................................................................
__all__ = ['cli', 'wrangle_matrix']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
