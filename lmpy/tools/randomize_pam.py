"""This script will randomize a PAM while maintaining marginal totals."""
import argparse
from copy import deepcopy

from lmpy import Matrix
from lmpy.randomize.grady import grady_randomize
from lmpy.tools._config_parser import _process_arguments


DESCRIPTION = '''\
Randomize a binary presence-absence matrix (PAM) while maintaining marginal totals.\
'''


# .....................................................................................
def randomize_pam(in_pam):
    """Randomize a PAM.

    Args:
        in_pam (Matrix): The input PAM to be randomized.

    Returns:
        Matrix: A randomized PAM that maintains marginal totals.
    """
    random_pam = grady_randomize(in_pam)
    return random_pam


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='randomize_pam', description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        'input_pam_filename',
        type=str,
        help='The file location of the PAM to randomize.',
    )
    parser.add_argument(
        'output_pam_filename',
        nargs='+',
        type=str,
        help='The file location to write the randomized PAM.',
    )
    return parser


# .....................................................................................
def cli():
    """Function providing a command line interface to the tool."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    in_pam = Matrix.load(args.input_pam_filename)
    if isinstance(args.output_pam_filename, str):
        args.output_pam_filename = [args.output_pam_filename]
    for out_fn in args.output_pam_filename:
        rand_pam = randomize_pam(deepcopy(in_pam))
        rand_pam.write(out_fn)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'randomize_pam']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
