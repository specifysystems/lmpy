"""A tool for wrangling phylogenetic trees."""
import argparse
from copy import deepcopy
import json

from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.tree import TreeWrapper
from lmpy.tools._config_parser import _process_arguments


# .....................................................................................
DESCRIPTION = '''A tool to wrangle phylogenetic trees as needed for processing.'''


# .....................................................................................
def wrangle_tree(tree, wranglers):
    """Wrangle the tree as configured.

    Args:
        tree (TreeWrapper): A phylogenetic tree to wrangle.
        wranglers (list): A list of tree data wranglers.

    Returns:
        TreeWrapper: The modified tree object.
        dict: Wrangler reporting information
    """
    report = []
    for wrangler in wranglers:
        tree = wrangler.wrangle_tree(tree)
        report.append(deepcopy(wrangler.get_report()))
    return tree, report


# .....................................................................................
def cli():
    """Command-line interface for the tool."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('--config_file', type=str, help='Path to configuration file.')
    parser.add_argument(
        '-r', '--report_filename', type=str, help='Path to write report.'
    )
    parser.add_argument('tree_filename', type=str, help='Path to phylogenetic tree.')
    parser.add_argument(
        'tree_schema',
        type=str,
        choices=['newick', 'nexus'],
        help='The schema of the input phylogenetic tree.',
    )
    parser.add_argument(
        'wrangler_configuration_file',
        type=str,
        help='Path to phylogenetic tree wrangler configuration.',
    )
    parser.add_argument(
        'out_tree_filename',
        type=str,
        help='Path to write the wrangled phylogenetic tree.',
    )
    parser.add_argument(
        'out_tree_schema',
        type=str,
        choices=['newick', 'nexus'],
        help='The schema of the output phylogenetic tree.',
    )
    args = _process_arguments(parser, config_arg='config_file')
    tree = TreeWrapper.get(path=args.tree_filename, schema=args.tree_schema)
    with open(args.wrangler_configuration_file, mode='rt') as in_json:
        wrangler_factory = WranglerFactory()
        wranglers = wrangler_factory.get_wranglers(json.load(in_json))
    wrangled_tree, report = wrangle_tree(tree, wranglers)
    wrangled_tree.write(path=args.out_tree_filename, schema=args.out_tree_schema)
    if args.report_filename:
        with open(args.report_filename, mode='wt') as report_out:
            json.dump(report, report_out)


# .....................................................................................
__all__ = ['cli', 'wrangle_tree']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
