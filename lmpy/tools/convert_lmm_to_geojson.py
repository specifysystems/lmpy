"""Convert a lmpy Matrix to a GeoJSON (.geojson) file."""
import argparse
import json

from lmpy.matrix import Matrix
from lmpy.spatial.geojsonify import (
    geojsonify_matrix, geojsonify_matrix_with_shapefile,
)
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = 'Convert a lmpy Matrix to a GeoJSON file.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='convert_lmm_to_geojson',
        description=DESCRIPTION,
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '--shapefile_filename',
        '-s',
        type=str,
        help=(
            'Path to a shapefile that can be used to generate polygons matching '
            'matrix sites.'
        ),
    )
    parser.add_argument(
        '--resolution',
        '-r',
        type=float,
        help=(
            'Resolution of the polygons in the GeoJSON if a shapefile was not provided.'
            'Otherwise, use points.'
        ),
    )
    parser.add_argument(
        '--omit_value',
        '-o',
        action='append',
        nargs='*',
        type=float,
        help='Properties should be omitted if they have this value for a site.'
    )
    parser.add_argument(
        'in_lmm_filename', type=str, help='Lmpy .lmm filename to convert to GeoJSON.'
    )
    parser.add_argument(
        'out_geojson_filename',
        type=str,
        help='Location to write the converted matrix GeoJSON.',
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line tool for converting LMM to GeoJSON."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    mtx = Matrix.load(args.in_lmm_filename)
    if args.shapefile_filename is not None:
        matrix_geojson = geojsonify_matrix_with_shapefile(
            mtx, args.shapefile_filename, omit_values=args.omit_value
        )
    else:
        matrix_geojson = geojsonify_matrix(
            mtx, resolution=args.resolution, omit_values=args.omit_value
        )
    with open(args.out_geojson_filename, mode='wt') as out_json:
        json.dump(matrix_geojson, out_json)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
