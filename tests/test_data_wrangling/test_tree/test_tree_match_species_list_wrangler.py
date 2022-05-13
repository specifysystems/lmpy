"""Test the match_species_list_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.species_list import SpeciesList
from lmpy.data_wrangling.tree.match_species_list_wrangler import (
    MatchSpeciesListTreeWrangler,
)

from tests.data_simulator import generate_tree


# .....................................................................................
def test_match_species_list_wrangler_from_filename(generate_temp_filename):
    """Test subsetting a tree from a species list file.

    Args:
        generate_temp_filename (pytest.fixture): A fixture for generating filenames.
    """
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])
    # Shuffle species for selection in tree
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 75)]

    species_list_filename = generate_temp_filename(suffix='.lmm')
    species_list.write(species_list_filename)

    # Generate test tree
    test_tree = generate_tree(deepcopy(tree_species))

    # Wrangle
    wrangler = MatchSpeciesListTreeWrangler(species_list_filename)
    wrangled_tree = wrangler.wrangle_tree(deepcopy(test_tree))

    # Check that the number of taxa is less than or equal to len(tree_species)
    assert len(wrangled_tree.taxon_namespace) <= len(tree_species)

    # Make sure all taxa are in matrix and tree species
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in species_list
        assert taxon.label in tree_species

    # Check that we purged between zero and len(tree_species) - 1
    report = wrangler.get_report()
    assert report['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['purged'] <= len(tree_species) - 1


# .....................................................................................
def test_match_species_list_wrangler_from_species_list():
    """Test subsetting a tree from a species list."""
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])
    # Shuffle species for selection in tree
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 75)]

    # Generate test tree
    test_tree = generate_tree(deepcopy(tree_species))

    # Wrangle
    wrangler = MatchSpeciesListTreeWrangler(species_list)
    wrangled_tree = wrangler.wrangle_tree(deepcopy(test_tree))

    # Check that the number of taxa is less than or equal to len(tree_species)
    assert len(wrangled_tree.taxon_namespace) <= len(tree_species)

    # Make sure all taxa are in matrix and tree species
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in species_list
        assert taxon.label in tree_species

    # Check that we purged between zero and len(tree_species) - 1
    report = wrangler.get_report()
    assert report['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['purged'] <= len(tree_species) - 1
