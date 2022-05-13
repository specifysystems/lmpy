"""Test the species list match matrix wrangler."""
import numpy as np

from lmpy.data_wrangling.species_list.match_matrix_wrangler import (
    MatchMatrixSpeciesListWrangler,
)
from lmpy.matrix import Matrix
from lmpy.species_list import SpeciesList


# .....................................................................................
def test_match_matrix_species_list_wrangler():
    """Test subsetting a species list based on matrix data."""
    # Create species pool
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)
    val_1 = np.random.randint(500, 800)
    val_2 = np.random.randint(200, 500)
    num_rows = 100

    # Create species list
    species_list = SpeciesList(species_pool[:val_1])
    # Create test matrix
    matrix_species = species_pool[val_2:]
    test_matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    # Create wrangler
    wrangler = MatchMatrixSpeciesListWrangler(test_matrix, 1)

    # Wrangle species list
    wrangled_species_list = wrangler.wrangle_species_list(species_list)

    # Check that wrangled list is subset of matrix
    assert len(wrangled_species_list) == val_1 - val_2

    # Check report
    report = wrangler.get_report()
    assert report['removed'] == len(species_list) - len(wrangled_species_list)
