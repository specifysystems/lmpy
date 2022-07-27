"""Create an SDM using a method determined by the data."""
import argparse
import json
import os
import shutil

from lmpy.log import Logger
from lmpy.sdm.model import project_sdm
from lmpy.tools._config_parser import _process_arguments, test_files


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
        prog='project_sdm',
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
        '--species_name',
        type=str,
        default=None,
        help='Name of taxon to be projected.'
    )
    # parser.add_argument(
    #     '-z', '--package_filename', type=str, help='Output package zip file.'
    # )
    parser.add_argument(
        'maxent_lambdas_file',
        type=str,
        help='File containing Maxent SDM lambdas file.'
    )
    parser.add_argument(
        'env_dir',
        type=str,
        help='Directory containing environment layers for modeling.'
    )
    parser.add_argument('work_dir', type=str, help='Directory where work can be done.')
    parser.add_argument(
        'model_raster_filename',
        type=str,
        help='File location to write final model raster.'
    )
    return parser


# .....................................................................................
# def test_inputs(args):
#     """Test input data and configuration files for existence.
#
#     Args:
#         args: arguments pre-processed for this tool.
#
#     Returns:
#         all_missing_inputs: Error messages for display on exit.
#     """
#     # for fn in os.path.args.env_dir
#     errs = test_files([args.maxent_lambdas_file, "Maxent model file"])
#     return errs


# .....................................................................................
def cli():
    """Provide a command-line interface for SDM modeling.

    Note:
        create_sdm creates a raster projected distribution map using the same
        environmental layers as were used for modeling.  This function is intended to
        project an pre-created model onto different environmental layres.
    """
    parser = build_parser()
    args = _process_arguments(parser, 'config_file')

    maxent_lambdas_file = f"{args.maxent_lambdas_file}"
    errs = test_files([maxent_lambdas_file, "Maxent model file"])
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    species_name = args.species_name
    if species_name is None:
        species_name = os.path.splitext(os.path.basename(args.model_raster_filename))[0]

    output_raster_filename, report = project_sdm(
        maxent_lambdas_file,
        args.env_dir,
        species_name,
        args.work_dir,
        logger=logger
    )

    # Move model raster
    output_dir = os.path.dirname(args.output_map_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    shutil.copy(output_raster_filename, args.output_map_filename)

    # Conditionally write report file
    if args.report_filename is not None:
        with open(args.report, mode='wt') as out_json:
            json.dump(report, out_json)


# .....................................................................................
if __name__ == '__main__':
    workdir = os.getcwd()
    print(f"PWD is {workdir}")
    cli()
