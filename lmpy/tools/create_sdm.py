"""Create an SDM using a method determined by the data."""
import argparse
import json
import os
import shutil

from lmpy.sdm.maxent import DEFAULT_MAXENT_OPTIONS
from lmpy.sdm.model import create_sdm
from lmpy.tools._config_parser import _process_arguments, get_logger, test_files


# .....................................................................................
DESCRIPTION = """
Create a species distribution model (SDM) from species data and environmental data and
project the model back onto the environmental data of the same type, but the same or
different values."""


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='create_sdm',
        description=DESCRIPTION,
    )
    parser.add_argument(
        '--config_file',
        type=str,
        help='Configuration file containing script arguments.'
    )
    parser.add_argument(
        '--log_filename',
        '-l',
        type=str,
        help='A file location to write logging data.'
    )
    parser.add_argument(
        '--log_console',
        action='store_true',
        default=False,
        help='If provided, write log to console.'
    )
    parser.add_argument(
        '-r',
        '--report_filename',
        type=str,
        help='File location to write the wrangler report.'
    )
    parser.add_argument(
        '-n',
        '--min_points',
        type=int,
        default=12,
        help='Minimum number of points to use Maxent.',
    )
    parser.add_argument(
        '-p',
        '--maxent_params',
        type=str,
        help=f'Extra options to send to Maxent (added to {DEFAULT_MAXENT_OPTIONS}.',
    )
    parser.add_argument(
        '--species_key',
        type=str,
        default='species_name',
        help='Header of CSV column containing species information.'
    )
    parser.add_argument(
        '--x_key',
        type=str,
        default='x',
        help='Header of CSV column containing X value for record.'
    )
    parser.add_argument(
        '--y_key',
        type=str,
        default='y',
        help='Header of CSV column containing Y value for record.'
    )
    parser.add_argument(
        '--species_name',
        type=str,
        default=None,
        help='Name of taxon to be modeled.'
    )
    # parser.add_argument(
    #     '-z', '--package_filename', type=str, help='Output package zip file.'
    # )
    parser.add_argument(
        'points_filename',
        type=str,
        help='File containing occurrences in species, x, y format.'
    )
    parser.add_argument(
        'env_dir',
        type=str,
        help='Directory containing environment layers for modeling.'
    )
    parser.add_argument(
        'ecoregions_filename', type=str, help='Ecoregions raster filename.'
    )
    parser.add_argument('work_dir', type=str, help='Directory where work can be done.')
    parser.add_argument(
        'model_raster_filename',
        type=str,
        help='File location to write final model raster.'
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
    # for fn in os.path.args.env_dir
    errs = test_files(
        (args.points_filename, "Occurrence data input"),
        (args.ecoregions_filename, "Ecoregion input file"))
    return errs


# .....................................................................................
def cli():
    """Provide a command-line interface for SDM modeling."""
    parser = build_parser()
    args = _process_arguments(parser, 'config_file')

    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = get_logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    species_name = args.species_name
    if species_name is None:
        species_name = os.path.splitext(os.path.basename(args.points_filename))[0]

    maxent_params = DEFAULT_MAXENT_OPTIONS
    if args.maxent_params is not None:
        maxent_params += f" {args.maxent_params}"

    projected_distribution_filename, maxent_lambdas_filename, report = create_sdm(
        args.min_points,
        args.points_filename,
        args.env_dir,
        args.ecoregions_filename,
        args.work_dir,
        species_name,
        maxent_arguments=maxent_params,
        sp_key=args.species_key,
        x_key=args.x_key,
        y_key=args.y_key,
        create_mask=True,
        logger=logger
    )

    model_dir = os.path.dirname(args.model_raster_filename)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    shutil.copy(projected_distribution_filename, args.model_raster_filename)

    # Conditionally write report file
    if args.report_filename is not None:
        with open(args.report_filename, mode='wt') as out_json:
            json.dump(report, out_json)


# .....................................................................................
if __name__ == '__main__':
    workdir = os.getcwd()
    print(f"PWD is {workdir}")
    cli()
