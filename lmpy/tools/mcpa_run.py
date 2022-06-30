"""Tool for performing a single MCPA run."""
import argparse

from lmpy.matrix import Matrix
from lmpy.statistics.mcpa import mcpa
from lmpy.tools._config_parser import _process_arguments, test_files


DESCRIPTION = 'Compute a single run of MCPA metric.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(prog='mcpa_run', description=DESCRIPTION)

    parser.add_argument('pam_filename', type=str, help='Path to PAM file.')
    parser.add_argument(
        'tree_matrix_filename', type=str, help='Path to encoded phylogeny.'
    )
    parser.add_argument(
        'env_matrix_filename', type=str, help='Path to environment matrix.'
    )
    parser.add_argument(
        'biogeo_matrix_filename', type=str, help='Path to biogeography matrix.'
    )
    parser.add_argument(
        'mcpa_matrix_filename',
        type=str,
        help='Path to write computed MCPA values matrix.'
    )
    parser.add_argument('f_matrix_filename', type=str, help='Path to write F-Matrix.')
    return parser


# .....................................................................................
def test_inputs(args):
    """Test input data and configuration files for existence.

    Args:
        args: arguments pre-processed for this tool.

    Returns:
        all_missing_inputs: Error messages for display on exit.
    """
    all_missing_inputs = test_files((args.pam_filename, "PAM input"))
    all_missing_inputs.extend(test_files((args.tree_matrix_filename, "Tree Matrix")))
    all_missing_inputs.extend(
        test_files((args.env_matrix_filename, "Environmental Matrix")))
    all_missing_inputs.extend(
        test_files((args.biogeo_matrix_filename, "Biogeographic Hypothesis Matrix")))
    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for computing statistics."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    pam = Matrix.load(args.pam_filename)
    tree_mtx = Matrix.load(args.tree_matrix_filename)
    env_mtx = Matrix.load(args.env_matrix_filename)
    bg_mtx = Matrix.load(args.biogeo_matrix_filename)

    mcpa_vals, f_mtx = mcpa(pam, tree_mtx, env_mtx, bg_mtx)

    # Write outputs
    mcpa_vals.write(args.mcpa_matrix_filename)
    f_mtx.write(args.f_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
