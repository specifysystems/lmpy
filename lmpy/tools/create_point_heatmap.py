"""Create a point heatmap image."""
import argparse

from lmpy.spatial.map import create_point_heatmap_matrix
from lmpy.plots.plot import plot_matrix
from lmpy.point import PointCsvReader, PointDwcaReader
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = 'Create a point map image.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='create_point_heatmap',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
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
        help="If provided, write logging statements to the console."
    )
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the summary report."
    )
    parser.add_argument(
        '-b',
        '--base_layer',
        type=str,
        help='An optional base layer image for the plot.  Must have same extent.',
    )
    parser.add_argument(
        '--dwca',
        action='append',
        help='A Darwin-Core Archive filename to process.',
    )
    parser.add_argument(
        '--csv',
        action='append',
        nargs=4,
        help=(
            'A CSV file to process, a species header key, an x header key, '
            'and a y header key.'
        ),
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
        'plot_filename',
        type=str,
        help='A file path to write the generated plot image.',
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
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = []
    if args.dwca is not None:
        for dwca_fn in args.dwca:
            all_missing_inputs.extend(test_files((dwca_fn, "DwCA file")))
    if args.csv is not None:
        for csv_fn, _, _, _ in args.csv:
            all_missing_inputs.extend(test_files((csv_fn, "CSV file")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for creating a point heatmap.

    Raises:
        ValueError: Raised if neither a CSV or DWCA is provided.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    readers = []
    if args.dwca is not None:
        for dwca_fn in args.dwca:
            readers.append(PointDwcaReader(dwca_fn))
    if args.csv is not None:
        for csv_fn, sp_key, x_key, y_key in args.csv:
            readers.append(PointCsvReader(csv_fn, sp_key, x_key, y_key))
    if len(readers) == 0:
        raise ValueError('Must provide at least one CSV and / or DWCA.')

    point_heatmap = create_point_heatmap_matrix(
        readers,
        args.min_x,
        args.min_y,
        args.max_x,
        args.max_y,
        args.resolution
    )
    plot_matrix(
        point_heatmap,
        args.plot_filename,
        base_layer=args.base_layer,
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
