"""Tool for building shapegrid shapefiles."""
import argparse

from lmpy.data_preparation.build_grid import build_shapegrid


DESCRIPTION = '''\
Build a Shapegrid shapefile that is used to define the sites of a PAM or other \
multivariate Matrix for lmpy operations.'''


# .....................................................................................
def cli():
    """Command-line interface to build shapegrid."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'shapegrid_filename',
        type=str,
        help='File location to write shapegrid shapefile.',
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
        'epsg', type=int, help='The EPSG code (map projection) for the shapegrid.'
    )
    args = parser.parse_args()
    cell_sides = 4  # Add this to parameters if we enable hexagons again
    build_shapegrid(
        args.shapegrid_filename,
        args.min_x,
        args.min_y,
        args.max_x,
        args.max_y,
        args.cell_size,
        args.epsg,
        cell_sides,
    )


# .....................................................................................
__all__ = ['build_shapegrid', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
