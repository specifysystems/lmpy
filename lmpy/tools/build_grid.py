"""Tool for building grid shapefiles."""
import argparse

from lmpy.data_preparation.build_grid import build_grid
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = '''\
Build a grid shapefile that is used to define the sites of a PAM or other \
multivariate Matrix for lmpy operations.'''


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='build_grid', description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        'grid_filename',
        type=str,
        help='File location to write grid shapefile.',
    )
    parser.add_argument('min_x', type=float, help='The minimum x value for the grid.')
    parser.add_argument('min_y', type=float, help='The minimum y value for the grid.')
    parser.add_argument('max_x', type=float, help='The maximum x value for the grid.')
    parser.add_argument('max_y', type=float, help='The maximum y value for the grid.')
    parser.add_argument(
        'cell_size',
        type=float,
        help='The resolution of each grid cell (in EPSG map units).',
    )
    parser.add_argument(
        'epsg', type=int, help='The EPSG code (map projection) for the grid.'
    )
    return parser


# .....................................................................................
def cli():
    """Command-line interface to build grid."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    cell_sides = 4  # Add this to parameters if we enable hexagons again
    build_grid(
        args.grid_filename,
        args.min_x,
        args.min_y,
        args.max_x,
        args.max_y,
        args.cell_size,
        args.epsg,
        cell_sides,
    )


# .....................................................................................
__all__ = ['build_parser', 'build_grid', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
