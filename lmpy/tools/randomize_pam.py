"""This script will randomize a PAM while maintaining marginal totals."""
import argparse
from copy import deepcopy
import json
import os

from lmpy.log import Logger
from lmpy import Matrix
from lmpy.randomize.grady import grady_randomize
# from lmpy.randomize.swap import swap_randomize, trial_swap
from lmpy.tools._config_parser import _process_arguments, test_files


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

    Notes:
        TODO: enable Gotelli swap and trial swap methods
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
        "--log_filename",
        "-l",
        type=str,
        help="A file location to write logging data."
    )
    parser.add_argument(
        "--log_console",
        action="store_true",
        default=False,
        help="If provided, write log to console."
    )
    parser.add_argument(
        "-r",
        "--report_filename",
        type=str,
        help="File location to write the wrangler report."
    )
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
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = test_files((args.input_pam_filename, "PAM input"))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Function providing a command line interface to the tool.

    Raises:
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )

    in_pam = Matrix.load(args.input_pam_filename)
    if isinstance(args.output_pam_filename, str):
        output_pam_filenames = [args.output_pam_filename]
    for out_fn in output_pam_filenames:
        rand_pam = randomize_pam(deepcopy(in_pam))
        rand_pam.write(out_fn)
        logger.log(f"Wrote randomized PAM to {out_fn}", refname=script_name)

    # If the output report was requested, write it
    if args.report_filename:
        report = {
            "input_pam_filename": args.input_pam_filename,
            "output_pam_filenames": output_pam_filenames
        }
        try:
            with open(args.report_filename, mode='wt') as out_file:
                json.dump(report, out_file, indent=4)
        except OSError:
            raise
        except IOError:
            raise
        logger.log(
            f"Wrote report file to {args.report_filename}", refname=script_name)


# .....................................................................................
__all__ = ['build_parser', 'cli', 'randomize_pam']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
