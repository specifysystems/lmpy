"""Encode a tree into matrix for faster statistics computations."""
import argparse

import numpy as np

from lmpy import Matrix, TreeWrapper
from lmpy.tools._config_parser import _process_arguments


# .....................................................................................
def encode_tree(tree):
    """Encode a tree into a binary matrix and two data arrays for node and tips.

    Args:
        tree (TreeWrapper): A tree object to encode.

    Returns:
        (Matrix, Matrix, Matrix): The encoded tree matrix, node heights, tip lengths.
    """
    num_tips = len(tree.taxon_namespace)
    num_nodes = len(tree.nodes()) - num_tips

    tip_lengths = Matrix(np.zeros((num_tips,)))
    node_heights = Matrix(np.zeros((num_nodes,)))

    ordered_taxa = [taxon.label for taxon in tree.taxon_namespace]
    node_labels = ['Node {}'.format(i) for i in range(num_nodes)]

    taxon_index_map = {val: idx for idx, val in enumerate(ordered_taxa)}

    tree_mtx = Matrix(
        np.zeros((num_tips, num_nodes), dtype=np.bool),
        headers={'0': ordered_taxa, '1': node_labels},
    )

    def process_node(node, node_idx):
        node_taxa = []
        node_height = 0
        next_node_idx = node_idx + 1
        for child in node.child_nodes():
            if child.is_leaf():
                if child.edge_length < 1e-05:
                    print(
                        'Short branch length {:.6f} child.edge_length)'.format(
                            child.edge_length
                        )
                    )
                try:
                    tax_index = taxon_index_map[child.taxon.label]
                    node_taxa.append(tax_index)
                    tip_lengths[tax_index] = child.edge_length
                    tree_mtx[tax_index, node_idx] = 1
                    node_height = child.edge_length
                except Exception as err:
                    print(err)
                    print(child.__dict__)
                    print(child.annotations)
                    raise err
            else:
                child_taxa, next_node_idx, child_node_height = process_node(
                    child, next_node_idx
                )
                node_height = child_node_height + child.edge_length

                node_taxa.extend(child_taxa)

                for child_tax in child_taxa:
                    tree_mtx[child_tax, node_idx] = 1

        node_heights[node_idx] = node_height

        return node_taxa, next_node_idx, node_height

    process_node(tree.seed_node, 0)

    return tree_mtx, node_heights, tip_lengths


# .....................................................................................
def cli():
    """Main controlling method for script."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'tree_filename', type=str, help='File path to a phylogenetic tree.'
    )
    parser.add_argument(
        'tree_schema',
        type=str,
        help='The format of the tree file (ex. newick or nexus).',
    )
    parser.add_argument(
        'out_tree_matrix_filename',
        type=str,
        help='File path to write encoded tree matrix (tip rows by node columns).',
    )
    parser.add_argument(
        'out_node_heights_filename',
        type=str,
        help='File path to write node heights matrix.',
    )
    parser.add_argument(
        'out_tip_lengths_filename',
        type=str,
        help='File path to write tip lengths matrix.',
    )
    args = _process_arguments(parser)

    tree = TreeWrapper.get(path=args.tree_filename, schema=args.tree_schema)
    tree_mtx, node_heights, tip_lengths = encode_tree(tree)
    tree_mtx.write(args.out_tree_matrix_filename)
    node_heights.write(args.out_node_heights_filename)
    tip_lengths.write(args.out_tip_lengths_filename)


# .....................................................................................
__all__ = []


# .....................................................................................
if __name__ == '__main__':  # pragma: no cover
    cli()
