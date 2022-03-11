"""A tool for wrangling phylogenetic trees."""
import argparse
import json

from lmpy.data_wrangling.factory import wrangler_factory
from lmpy.tree import TreeWrapper


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
    """
    wrangled_tree = tree
    return wrangled_tree


# .....................................................................................
def cli():
    """Command-line interface for the tool."""
    parser = argparse.ArgumentParser(description=DESCRIPTION)
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
    args = parser.parse_args()
    tree = TreeWrapper.get(path=args.tree_filename, schema=args.tree_schema)
    with open(args.wrangler_configuration_file, mode='rt') as in_json:
        wranglers = wrangler_factory(json.load(in_json))
    wrangled_tree = wrangle_tree(tree, wranglers)
    wrangled_tree.write(path=args.out_tree_filename, schema=args.out_tree_schema)


# .....................................................................................
__all__ = ['cli', 'wrangle_tree']


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
