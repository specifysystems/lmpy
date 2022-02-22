"""Script to encode layers into a Matrix."""
import argparse

from lmpy.data_preparation.layer_encoder import LayerEncoder


DESCRIPTION = 'Encode raster and / or vector layers into a site by layer matrix.'


# .....................................................................................
def cli():
    """Command line interface for layer encoding.

    Raises:
        ValueError: Raised if an unknown encoding method is provided.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        '--encode_method',
        '-m',
        type=str,
        choices=['biogeo', 'presence_absence', 'largest_class', 'mean_value'],
        default='mean_value',
        help='The method to use to encode each layer.'
    )
    parser.add_argument(
        '--min_coverage',
        type=float,
        default=25,
        help='Minimum percentage of a cell that has to be covered to encode it.'
    )
    parser.add_argument(
        '--min_presence',
        type=float,
        default=10,
        help='Minimum value to be considered present when encoding presence absence.'
    )
    parser.add_argument(
        '--max_presence',
        type=float,
        default=127,
        help='The maximum value that should be considered present.'
    )
    parser.add_argument(
        '--attribute_field',
        type=str,
        help='The vector attribute to use for encoding layers.'
    )
    parser.add_argument(
        'shapegrid_filename',
        type=str,
        help='File location of shapegrid to use for site geometries.'
    )
    parser.add_argument(
        'out_matrix_filename',
        type=str,
        help='File location to write the encoded matrix.'
    )
    # Layers to encode
    parser.add_argument(
        '--layer',
        '-l',
        nargs=2,
        action='append',
        help='File location of layer followed by a label.'
    )

    args = parser.parse_args()

    encoder = LayerEncoder(args.shapegrid_filename)

    for lyr_fn, lyr_label in args.layer:
        if args.encode_method == 'biogeo':
            encoder.encode_biogeographic_hypothesis(
                lyr_fn,
                lyr_label,
                args.min_coverage,
                event_field=args.attribute_field
            )
        elif args.encode_method == 'presence_absence':
            encoder.encode_presence_absence(
                lyr_fn,
                lyr_label,
                args.min_presence,
                args.max_presence,
                args.min_coverage,
                attribute_name=args.attribute_field
            )
        elif args.encode_method == 'largest_class':
            encoder.encode_largest_class(
                lyr_fn,
                lyr_label,
                args.min_coverage,
                attribute_name=args.attribute_field
            )
        elif args.encode_method == 'mean_value':
            encoder.encode_mean_value(
                lyr_fn,
                lyr_label,
                attribute_name=args.attribute_field
            )
        else:
            raise ValueError('Unknown encoding method: {}'.format(args.encode_method))

    enc_mtx = encoder.get_encoded_matrix()
    enc_mtx.write(args.out_matrix_filename)


# .....................................................................................
__all__ = ['cli']


# .....................................................................................
if __name__ == '__main__':
    cli()
