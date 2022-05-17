"""Tool for wrangling a Matrix."""
import argparse

import json

from lmpy import Matrix
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.tools._config_parser import _process_arguments, get_logger


DESCRIPTION = '''\
Perform various wrangle operations on a matrix such as subsetting and reordering.'''


# .....................................................................................
def wrangle_matrix(mtx, wranglers):
    """Wrangle the Matrix as configured.

    Args:
        mtx (Matrix): A Matrix to wrangle.
        wranglers (list): A list of tree data wranglers.

    Returns:
        Matrix: The modified Matrix object.
        list: A list of report dictionaries.
    """
    report = []
    for wrangler in wranglers:
        mtx = wrangler.wrangle_matrix(mtx)
        report.append(wrangler.get_report())
    return mtx, report


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='wrangle_matrix', description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-r',
        '--report_filename',
        type=str,
        help='File location to write the wrangler report.'
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
        'in_matrix_filename', type=str, help='Path to the input Matrix.'
    )
    parser.add_argument(
        'wrangler_configuration_file',
        type=str,
        help='Path to Matrix wrangler configuration.',
    )
    parser.add_argument(
        'out_matrix_filename', type=str, help='Path to the outut Matrix.'
    )
    return parser


# .....................................................................................
def cli():
    """Provide a command-line interface to the wrangle matrix tool."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    logger = get_logger(
        'wrangle_matrix',
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    in_mtx = Matrix.load(args.in_matrix_filename)
    with open(args.wrangler_configuration_file, mode='rt') as in_json:
        wrangler_factory = WranglerFactory(logger=logger)
        wranglers = wrangler_factory.get_wranglers(json.load(in_json))

    wrangled_mtx, report = wrangle_matrix(in_mtx, wranglers)
    wrangled_mtx.write(args.out_matrix_filename)

    if args.report_filename is not None:
        with open(args.report_filename, mode='wt') as report_out:
            json.dump(report, report_out)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'wrangle_matrix']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
