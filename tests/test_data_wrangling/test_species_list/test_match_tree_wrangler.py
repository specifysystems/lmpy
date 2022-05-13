"""Test the species list match tree wrangler."""
import numpy as np

from lmpy.data_wrangling.species_list.match_tree_wrangler import (
    MatchTreeSpeciesListWrangler,
)
from lmpy.species_list import SpeciesList

from tests.data_simulator import generate_tree


# .....................................................................................
def test_match_tree_species_list_wrangler():
    """Test subsetting a species list based on a tree."""
    # Create species pool
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)
    val_1 = np.random.randint(500, 800)
    val_2 = np.random.randint(200, 500)

    # Create species list
    species_list = SpeciesList(species_pool[:val_1])
    # Create test tree
    tree_species = species_pool[val_2:]
    test_tree = generate_tree(tree_species)
    # Create wrangler
    wrangler = MatchTreeSpeciesListWrangler(test_tree)

    # Wrangle species list
    wrangled_species_list = wrangler.wrangle_species_list(species_list)

    # Check that wrangled list is subset of tree
    assert len(wrangled_species_list) == val_1 - val_2

    # Check report
    report = wrangler.get_report()
    assert report['removed'] == len(species_list) - len(wrangled_species_list)
