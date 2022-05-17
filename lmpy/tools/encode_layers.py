"""Script to encode layers into a Matrix."""
import argparse
import os

from lmpy.data_preparation.layer_encoder import LayerEncoder
from lmpy.tools._config_parser import _process_arguments


# .....................................................................................
DESCRIPTION = 'Encode raster and / or vector layers into a site by layer matrix.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='encode_layers', description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '--encode_method',
        '-m',
        type=str,
        choices=['biogeo', 'presence_absence', 'largest_class', 'mean_value'],
        default='mean_value',
        help='The method to use to encode each layer.',
    )
    parser.add_argument(
        '--min_coverage',
        type=float,
        default=25,
        help='Minimum percentage of a cell that has to be covered to encode it.',
    )
    parser.add_argument(
        '--min_presence',
        type=float,
        default=10,
        help='Minimum value to be considered present when encoding presence absence.',
    )
    parser.add_argument(
        '--max_presence',
        type=float,
        default=127,
        help='The maximum value that should be considered present.',
    )
    parser.add_argument(
        'grid_filename',
        type=str,
        help='File location of grid to use for site geometries.',
    )
    parser.add_argument(
        'out_matrix_filename',
        type=str,
        help='File location to write the encoded matrix.',
    )
    # Layers to encode
    parser.add_argument(
        '--layer',
        '-l',
        nargs='*',
        action='append',
        help='File location of layer [ LABEL [ ATTRIBUTE FIELD ]].',
    )
    return parser


# .....................................................................................
def cli():
    """Command line interface for layer encoding.

    Raises:
        ValueError: Raised if an unknown encoding method is provided or too many layer
            arguments.
    """
    parser = build_parser()

    args = _process_arguments(parser, config_arg='config_file')

    encoder = LayerEncoder(args.grid_filename)

    for layer_args in args.layer:
        # if there are too many layer arguments, fail
        if len(layer_args) > 3:
            raise ValueError(
                'Too many layer arguments {}.'
                'Hint: Specify layer args last in command.'.format(layer_args)
            )
        # Process layer arguments, get filename for sure, try label and attribute field
        lyr_fn = layer_args[0]
        layer_attribute = None

        # Label
        if len(layer_args) > 1:
            lyr_label = layer_args[1]
            if len(layer_args) > 2:
                layer_attribute = layer_args[2]
        else:
            lyr_label = os.path.splitext(os.path.basename(lyr_fn))[0]

        if args.encode_method == 'biogeo':
            encoder.encode_biogeographic_hypothesis(
                lyr_fn, lyr_label, args.min_coverage, attribute_field=layer_attribute
            )
        elif args.encode_method == 'presence_absence':
            encoder.encode_presence_absence(
                lyr_fn,
                lyr_label,
                args.min_presence,
                args.max_presence,
                args.min_coverage,
                attribute_name=layer_attribute,
            )
        elif args.encode_method == 'largest_class':
            encoder.encode_largest_class(
                lyr_fn,
                lyr_label,
                args.min_coverage,
                attribute_name=layer_attribute,
            )
        elif args.encode_method == 'mean_value':
            encoder.encode_mean_value(
                lyr_fn, lyr_label, attribute_name=layer_attribute
            )
        else:
            raise ValueError('Unknown encoding method: {}'.format(args.encode_method))

    enc_mtx = encoder.get_encoded_matrix()
    enc_mtx.write(args.out_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
