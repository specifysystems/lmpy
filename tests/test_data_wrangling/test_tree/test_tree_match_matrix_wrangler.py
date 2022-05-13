"""Test the match_tree_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.matrix import Matrix
from lmpy.data_wrangling.tree.match_matrix_wrangler import MatchMatrixTreeWrangler

from tests.data_simulator import generate_tree


# .....................................................................................
def test_match_matrix_wrangler_from_filename(generate_temp_filename):
    """Test subsetting and reordering matrix slices to match a tree filename.

    Args:
        generate_temp_filename (pytest.fixture): A fixture for generating filenames.
    """
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    matrix_species = all_species[:np.random.randint(51, 75)]
    # Shuffle species for selection in tree
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 75)]

    num_cols = 100

    # Create test matrix
    test_matrix = Matrix(
        np.ones((len(matrix_species), num_cols)),
        headers={
            '1': [f'Col {i}' for i in range(num_cols)],
            '0': matrix_species
        }
    )
    matrix_filename = generate_temp_filename(suffix='.lmm')
    test_matrix.write(matrix_filename)

    # Generate test tree
    test_tree = generate_tree(deepcopy(tree_species))

    # Wrangle
    wrangler = MatchMatrixTreeWrangler(matrix_filename, 0)
    wrangled_tree = wrangler.wrangle_tree(deepcopy(test_tree))

    # Check that the number of taxa is less than or equal to len(tree_species)
    assert len(wrangled_tree.taxon_namespace) <= len(tree_species)

    # Make sure all taxa are in matrix and tree species
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in matrix_species
        assert taxon.label in tree_species

    # Check that we purged between zero and len(tree_species) - 1
    report = wrangler.get_report()
    assert report['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['purged'] <= len(tree_species) - 1


# .....................................................................................
def test_match_matrix_wrangler_from_matrix():
    """Test subsetting and reordering matrix slices to match a tree object."""
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    matrix_species = all_species[:np.random.randint(51, 75)]
    # Shuffle species for selection in tree
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 75)]

    num_rows = 100

    # Create test matrix
    test_matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {i}' for i in range(num_rows)],
            '1': matrix_species
        }
    )

    # Generate test tree
    test_tree = generate_tree(deepcopy(tree_species))

    # Wrangle
    wrangler = MatchMatrixTreeWrangler(test_matrix, 1)
    wrangled_tree = wrangler.wrangle_tree(deepcopy(test_tree))

    # Check that the number of taxa is less than or equal to len(tree_species)
    assert len(wrangled_tree.taxon_namespace) <= len(tree_species)

    # Make sure all taxa are in matrix and tree species
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in matrix_species
        assert taxon.label in tree_species

    # Check that we purged between zero and len(tree_species) - 1
    report = wrangler.get_report()
    assert report['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['purged'] <= len(tree_species) - 1
