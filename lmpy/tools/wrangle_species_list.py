"""Tool for wrangling a Matrix."""
import argparse

import json

from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.species_list import SpeciesList
from lmpy.tools._config_parser import _process_arguments, get_logger


DESCRIPTION = 'Perform various wrangle operations on a species list.'


# .....................................................................................
def wrangle_species_list(species_list, wranglers):
    """Wrangle the SpeciesList as configured.

    Args:
        species_list (SpeciesList): A SpeciesList to wrangle.
        wranglers (list): A list of tree data wranglers.

    Returns:
        SpeciesList: The modified SpeciesList object.
        list: A list of report dictionaries.
    """
    report = []
    for wrangler in wranglers:
        species_list = wrangler.wrangle_species_list(species_list)
        report.append(wrangler.get_report())
    return species_list, report


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='wrangle_species_list',
        description=DESCRIPTION
    )
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
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
        'in_species_list_filename', type=str, help='Path to the input SpeciesList.'
    )
    parser.add_argument(
        'wrangler_configuration_file',
        type=str,
        help='Path to Matrix wrangler configuration.',
    )
    parser.add_argument(
        'out_species_list_filename', type=str, help='Path to the outut SpeciesList.'
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line interface to the wrangle species list tool."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    logger = get_logger(
        'wrangle_species_list',
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    in_species_list = SpeciesList.from_file(args.in_species_list_filename)
    with open(args.wrangler_configuration_file, mode='rt') as in_json:
        wrangler_factory = WranglerFactory(logger=logger)
        wranglers = wrangler_factory.get_wranglers(json.load(in_json))

    wrangled_species_list, report = wrangle_species_list(in_species_list, wranglers)
    wrangled_species_list.write(args.out_species_list_filename)

    if args.report_filename is not None:
        with open(args.report_filename, mode='wt') as report_out:
            json.dump(report, report_out)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'wrangle_species_list']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
