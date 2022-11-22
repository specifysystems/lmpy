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


DESCRIPTION = """\
Randomize a binary presence-absence matrix (PAM) while maintaining marginal totals.\
"""


# .....................................................................................
def randomize_pam(in_pam, method="grady", logger=None):
    """Randomize a PAM.

    Args:
        in_pam (Matrix): The input PAM to be randomized.
        method (str): the algorithm for randomizing the PAM
        logger (lmpy.log.Logger): logger for printing to file and console

    Returns:
        Matrix: A randomized PAM that maintains marginal totals.

    Raises:
        Exception: on method other than `grady`
    """
    if method == "grady":
        random_pam = grady_randomize(in_pam)
    else:
        raise Exception(f"Randomization method {method} is not yet enabled")
    if logger is not None:
        logger.log(
            f"Randomized PAM using {method}",
            refname=os.path.splitext(os.path.basename(__file__))[0])
    return random_pam


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool"s parameters.
    """
    parser = argparse.ArgumentParser(prog="randomize_pam", description=DESCRIPTION)
    parser.add_argument("--config_file", type=str, help="Path to configuration file.")
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
        "--randomization_method",
        "-m",
        type=str,
        choices=["grady"],
        default="grady",
        help="The method to use to randomize the matrix.",
    )
    parser.add_argument(
        "--output_pam_count",
        type=int,
        help=("Number of randomized PAMs to create."),
    )
    parser.add_argument(
        "--output_pam_basefilename",
        nargs="+",
        type=str,
        help="The path and base filename (without extension) for randomized PAMs.",
    )
    parser.add_argument(
        "--output_pam_filename",
        nargs="+",
        type=str,
        help="The file location to write the randomized PAM(s).",
    )
    parser.add_argument(
        "input_pam_filename",
        type=str,
        help="The file location of the PAM to randomize.",
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
        Exception: on failure to provide output_pam_filename or output_pam_filepattern
        Exception: on failure to provide output_pam_count if output_pam_filepattern
            is specified.
        OSError: on failure to write to report_filename.
        IOError: on failure to write to report_filename.

    Notes:
        TODO: enable Gotelli swap and trial swap methods
    """
    parser = build_parser()
    args = _process_arguments(parser, config_arg="config_file")
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit("\n".join(errs))

    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logger = Logger(
        script_name,
        log_filename=args.log_filename,
        log_console=args.log_console
    )
    if args.output_pam_filename is not None:
        if isinstance(args.output_pam_filename, str):
            output_pam_filenames = [args.output_pam_filename]
    elif args.output_pam_basefilename is not None:
        if args.output_pam_count is not None:
            outbase, _ = os.path.splitext(args.output_pam_basefilename)
            output_pam_filenames = [
                f"{outbase}_{i+1}.lmm" for i in range(args.output_pam_count)]
        else:
            raise Exception(
                f"{script_name} requires output_pam_count if specifying an " +
                "output_pam_filepattern")
    else:
        raise Exception(
            f"{script_name} requires either output_pam_filepattern or at least one " +
            "output_pam_filename")
    logger.log(
        f"\n\n***Randomize {args.input_pam_filename} {len(output_pam_filenames)} " +
        f"times using method {args.randomization_method}",
        refname=script_name)

    in_pam = Matrix.load(args.input_pam_filename)
    logger.log(
        f"Loaded {args.input_pam_filename} for randomization", refname=script_name)
    for out_fn in output_pam_filenames:
        # Create output directory first
        work_dir = os.path.dirname(out_fn)
        if not os.path.exists(work_dir):
            os.makedirs(work_dir)
        # Randomize using "grady" algorithm
        rand_pam = randomize_pam(deepcopy(in_pam), method=args.randomization_method)
        rand_pam.write(out_fn)
        logger.log(f"Wrote randomized PAM to {out_fn}", refname=script_name)

    # If the output report was requested, write it
    if args.report_filename:
        report = {
            "input_pam_filename": args.input_pam_filename,
            "output_pam_filenames": output_pam_filenames
        }
        try:
            with open(args.report_filename, mode="wt") as out_file:
                json.dump(report, out_file, indent=4)
        except OSError:
            raise
        except IOError:
            raise
        logger.log(
            f"Wrote report file to {args.report_filename}", refname=script_name)


# .....................................................................................
__all__ = ["build_parser", "cli", "randomize_pam"]


# .....................................................................................
if __name__ == "__main__":  # pragma: no cover
    cli()
