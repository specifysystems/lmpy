"""This script will randomize a PAM while maintaining marginal totals."""
import argparse

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
def cli():
    """Function providing a command line interface to the tool."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument(
        'input_pam_filename',
        type=str,
        help='The file location of the PAM to randomize.',
    )
    parser.add_argument(
        'output_pam_filename',
        type=str,
        help='The file location to write the randomized PAM.',
    )
    args = _process_arguments(parser)
    in_pam = Matrix.load(args.input_pam_filename)
    rand_pam = randomize_pam(in_pam)
    rand_pam.write(args.output_pam_filename)


# .....................................................................................
__all__ = ['cli', 'randomize_pam']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
