"""Test the subset_tree_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.data_wrangling.tree.subset_tree_wrangler import SubsetTreeWrangler

from tests.data_simulator import generate_tree


# .....................................................................................
def test_subset_tree_wrangler():
    """Test subsetting a tree from taxa."""
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle and get taxa for tree
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 100)]
    # Shuffle and get taxa for subsetting
    np.random.shuffle(all_species)
    subset_species = all_species[:np.random.randint(51, 100)]

    # Generate a tree
    tree = generate_tree(deepcopy(tree_species))

    # Wrangle!
    wrangler = SubsetTreeWrangler(subset_species)
    wrangled_tree = wrangler.wrangle_tree(deepcopy(tree))

    # Assert that we removed 0 to len(tree_species) - 1
    report = wrangler.get_report()
    assert report['purged'] >= 0
    assert report['purged'] <= len(tree_species) - 1

    # Assert that all taxa are in tree_species and subset_species
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in tree_species
        assert taxon.label in subset_species
