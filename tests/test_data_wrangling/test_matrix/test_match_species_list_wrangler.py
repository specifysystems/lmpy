"""Test the match_tree_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.data_wrangling.matrix.match_species_list_wrangler import (
    MatchSpeciesListMatrixWrangler,
)
from lmpy.matrix import Matrix
from lmpy.species_list import SpeciesList


# .....................................................................................
def test_match_species_list_wrangler_from_filename(generate_temp_filename):
    """Test subsetting and reordering matrix slices to match a species list filename.

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
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])

    num_cols = 100

    # Create test matrix
    test_matrix = Matrix(
        np.ones((len(matrix_species), num_cols)),
        headers={
            '1': [f'Col {i}' for i in range(num_cols)],
            '0': matrix_species
        }
    )

    # Generate test species list
    species_list_filename = generate_temp_filename(suffix='.txt')
    species_list.write(species_list_filename)

    # Wrangle
    wrangler = MatchSpeciesListMatrixWrangler(species_list_filename, 0)
    wrangled_matrix = wrangler.wrangle_matrix(deepcopy(test_matrix))

    # Check that number of rows is less than or equal to len(matrix_species)
    assert wrangled_matrix.shape[0] <= len(matrix_species)

    # Make sure all headers are in matrix and tree species
    for sp in wrangled_matrix.get_row_headers():
        assert sp in matrix_species
        assert sp in species_list

    # Check that we purged between zero and len(matrix_species) - 1
    report = wrangler.get_report()
    assert report['changes']['0']['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['changes']['0']['purged'] <= len(matrix_species) - 1
    assert list(report['changes'].keys()) == ['0']


# .....................................................................................
def test_match_species_list_wrangler_from_species_list():
    """Test subsetting and reordering matrix slices to match a species list."""
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    matrix_species = all_species[:np.random.randint(51, 75)]
    # Shuffle species for selection in tree
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])

    num_cols = 100

    # Create test matrix
    test_matrix = Matrix(
        np.ones((len(matrix_species), num_cols)),
        headers={
            '1': [f'Col {i}' for i in range(num_cols)],
            '0': matrix_species
        }
    )

    # Wrangle
    wrangler = MatchSpeciesListMatrixWrangler(species_list, 0)
    wrangled_matrix = wrangler.wrangle_matrix(deepcopy(test_matrix))

    # Check that number of rows is less than or equal to len(matrix_species)
    assert wrangled_matrix.shape[0] <= len(matrix_species)

    # Make sure all headers are in matrix and tree species
    for sp in wrangled_matrix.get_row_headers():
        assert sp in matrix_species
        assert sp in species_list

    # Check that we purged between zero and len(matrix_species) - 1
    report = wrangler.get_report()
    assert report['changes']['0']['purged'] >= 0
    # The test should ensure that we have at least one common species
    assert report['changes']['0']['purged'] <= len(matrix_species) - 1
    assert list(report['changes'].keys()) == ['0']
