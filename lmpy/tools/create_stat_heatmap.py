"""Create a stat heatmap image."""
import argparse

import numpy as np

from lmpy.matrix import Matrix
from lmpy.plots.map import create_stat_heatmap_matrix, plot_matrix
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Create a statistic heatmap image.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='create_stat_heatmap',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-b',
        '--base_layer',
        type=str,
        help='An optional base layer image for the plot.  Must have same extent.',
    )
    parser.add_argument(
        '-t',
        '--title',
        type=str,
        help='A title to add to the plot image.'
    )
    parser.add_argument(
        '--cmap',
        type=str,
        default='Reds',
        help='A color map to use for the image.'
    )
    parser.add_argument(
        '--vmin',
        type=float,
        help='The minimum value for color scaling.'
    )
    parser.add_argument(
        '--vmax',
        type=float,
        help='The maximum value for color scaling (use -1 to use maximum from data).'
    )
    parser.add_argument(
        '--mask_matrix',
        type=str,
        help='File path to a binary matrix to use as a mask.'
    )

    parser.add_argument(
        'plot_filename',
        type=str,
        help='A file path to write the generated plot image.',
    )
    parser.add_argument(
        'matrix_filename',
        type=str,
        help='The file path of the matrix containing the data to map.'
    )
    parser.add_argument(
        'statistic',
        type=str,
        help='The name of the statistic (must match column header) in the matrix.'
    )
    parser.add_argument(
        'min_x',
        type=float,
        help='The minimum x value of the plot map range.'
    )
    parser.add_argument(
        'min_y',
        type=float,
        help='The minimum y value of the plot map range.'
    )
    parser.add_argument(
        'max_x',
        type=float,
        help='The maximum x value of the plot map range.'
    )
    parser.add_argument(
        'max_y',
        type=float,
        help='The maximum y value of the plot map range.'
    )
    parser.add_argument(
        'resolution',
        type=float,
        help='The resolution of each cell of the plot map.'
    )

    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a point heatmap."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')

    matrix = Matrix.load(args.matrix_filename)
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
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
