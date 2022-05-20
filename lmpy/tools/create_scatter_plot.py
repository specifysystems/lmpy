"""Create a scatter plot for two matrix vectors."""
import argparse
import json

from lmpy.matrix import Matrix
from lmpy.plots.scatter import create_scatter_plot
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Create a scatter plot for two matrix statistics.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='create_scatter_plot',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')

    parser.add_argument('-t', '--title', type=str, help='A title for the plot image.')
    parser.add_argument('--x_label', type=str, help='A label for the x-axis.')
    parser.add_argument('--y_label', type=str, help='A label for the y-axis.')
    parser.add_argument(
        '-s',
        '--std_dev_style',
        type=str,
        action='append',
        help=(
            'A dictionary of parameters to style a standard deviation ellipse.  '
            'Multiple etries will result in multiple ellipses.'
        )
    )

    parser.add_argument(
        'plot_filename', type=str, help='File location to write plot image.'
    )
    parser.add_argument(
        'matrix_filename', type=str, help='File location of matrix containing data.'
    )
    parser.add_argument(
        'x_statistic',
        type=str,
        help='Column header of the vector to use for the x-axis.'
    )
    parser.add_argument(
        'y_statistic',
        type=str,
        help='Column header of the vector to use for the y-axis.'
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a scatter plot."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')

    data = Matrix.load(args.matrix_filename)
    col_headers = data.get_column_headers()
    x_column = col_headers.index(args.x_statistic)
    y_column = col_headers.index(args.y_statistic)

    std_dev_styles = None
    if args.std_dev_style is not None:
        std_dev_styles = [json.loads(style) for style in args.std_dev_style]

    create_scatter_plot(
        args.plot_filename,
        data[:, x_column],
        data[:, y_column],
        title=args.title,
        x_label=args.x_label,
        y_label=args.y_label,
        std_dev_styles=std_dev_styles,
    )


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
