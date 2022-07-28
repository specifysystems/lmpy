"""Script to encode layers into a Matrix."""
import argparse
import os

from lmpy.data_preparation.layer_encoder import LayerEncoder
from lmpy.log import Logger
from lmpy.tools._config_parser import _process_arguments, test_files


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
    # Layers to encode
    parser.add_argument(
        '--layer_file_pattern',
        type=str,
        help='File pattern to one or more layers.',
    )
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_errors: Error messages for display on exit.
    """
    all_errors = []
    if args.min_coverage < 0 or args.min_coverage > 100:
        all_errors.append(
            f"Argument min_coverage {args.min_coverage} is not between 0 and 100")
    if args.min_presence >= args.max_presence:
        all_errors.append(
            f"Argument min_presence {args.args.min_presence} is not less than " +
            f"max_presence {args.max_presence}")
    if not os.path.exists(args.grid_filename):
        all_errors.extend(test_files((args.grid_filename, "Input grid file")))
    if args.layer is not None:
        for layer_args in args.layer:
            # if there are too many layer arguments, fail
            if len(layer_args) > 3:
                all_errors.append(f"Too many layer arguments {layer_args}.")
            # Test all layer files
            lyr_fn = layer_args[0]
            all_errors.extend(test_files((lyr_fn, "Input layer")))
    return all_errors


# .....................................................................................
def cli():
    """Command line interface for layer encoding.

    Raises:
        ValueError: Raised if an unknown encoding method is provided or too many layer
            arguments.
    """
    ref = "encode_layers"
    parser = build_parser()

    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    layers = {}
    if args.layer_file_pattern is not None:
        import glob
        lyrfiles = glob.glob(os.path.join(args.layer_file_pattern))
        for fn in lyrfiles:
            layers[fn] = {
                'attribute': None,
                'label': os.path.splitext(os.path.basename(fn))[0]}

    if args.layer is not None:
        for layer_args in args.layer:
            lyr_fn = layer_args[0]
            layers[lyr_fn] = {
                'attribute': None,
                'label': os.path.splitext(os.path.basename(lyr_fn))[0]}
            if len(layer_args) > 1:
                # First optional arg is label
                layers[lyr_fn]['label'] = layer_args[1]
                if len(layer_args) > 2:
                    # Second optional arg is attribute
                    layers[lyr_fn]['attribute'] = layer_args[2]

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )
    logger.log(
        f"Encode {len(layers)} layers for matrix {args.out_matrix_filename}",
        refname=ref)

    encoder = LayerEncoder(args.grid_filename, logger=logger)

    logger.log(
        f"Start encoding {len(layers)} layers to matrix {args.out_matrix_filename} " +
        f"with {args.encode_method}", refname=ref)
    for lyr_fn, lyr_args in layers.items():
        if args.encode_method == 'biogeo':
            encoder.encode_biogeographic_hypothesis(
                lyr_fn, lyr_args['label'], args.min_coverage,
                attribute_field=lyr_args['attribute'],
            )
        elif args.encode_method == 'presence_absence':
            encoder.encode_presence_absence(
                lyr_fn,
                lyr_args['label'],
                args.min_presence,
                args.max_presence,
                args.min_coverage,
                attribute_name=lyr_args['attribute'],
            )
        elif args.encode_method == 'largest_class':
            encoder.encode_largest_class(
                lyr_fn,
                lyr_args['label'],
                args.min_coverage,
                attribute_name=lyr_args['attribute'],
            )
        elif args.encode_method == 'mean_value':
            encoder.encode_mean_value(
                lyr_fn, lyr_args['label'], attribute_name=lyr_args['attribute']
            )
        else:
            raise ValueError('Unknown encoding method: {}'.format(args.encode_method))
        logger.log(f"Completed encode {lyr_fn}", refname=ref)

    enc_mtx = encoder.get_encoded_matrix()
    enc_mtx.write(args.out_matrix_filename)
    logger.log(f"***Completed matrix {args.out_matrix_filename}", refname=ref)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
