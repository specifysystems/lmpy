"""This tool encodes a phylogenetic tree into a matrix that can be used for MCPA."""
import argparse

from lmpy.data_preparation.tree_encoder import TreeEncoder
from lmpy.matrix import Matrix
from lmpy.tools._config_parser import _process_arguments, test_files
from lmpy.tree import TreeWrapper


DESCRIPTION = 'This tool encodes a phylogenetic tree into a matrix for use with MCPA.'


# .....................................................................................
def build_parser():
    """Build an argparse.ArgumentParser object for the tool.

    Returns:
        argparse.ArgumentParser: An argument parser for the tool's parameters.
    """
    parser = argparse.ArgumentParser(
        prog='my_prog_name',
        description=DESCRIPTION
    )
    # The '--config_file' argument is used for providing arguments in a configuration
    #     file instead of the command line
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument('tree_filename', type=str, help='Path to tree to encode.')
    parser.add_argument(
        'tree_schema',
        type=str,
        choices=['newick', 'nexus', 'nexml'],
        help='The schema of the provided tree filename.'
    )
    parser.add_argument(
        'pam_filename',
        type=str,
        help='File path to presence-absence matrix to use with the tree.'
    )
    parser.add_argument(
        'output_matrix_filename',
        type=str,
        help='File path where the encoded tree matrix should be written.'
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
    all_missing_inputs = test_files((args.tree_filename, "Tree input"))
    all_missing_inputs.extend(test_files((args.pam_filename, "Matrix input")))

    return all_missing_inputs


# .....................................................................................
def cli():
    """Provide a command-line tool for encoding a tree for MCPA."""
    parser = build_parser()
    args = _process_arguments(parser, config_arg='config_file')
    errs = test_inputs(args)
    if errs:
        print("Errors, exiting program")
        exit('\n'.join(errs))

    tree = TreeWrapper.get(path=args.tree_filename, schema=args.tree_schema)
    pam = Matrix.load(args.pam_filename)
    tree_encoder = TreeEncoder(tree, pam)
    tree_mtx = tree_encoder.encode_phylogeny()
    tree_mtx.write(args.output_matrix_filename)


# .....................................................................................
__all__ = ['build_parser', 'cli']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
