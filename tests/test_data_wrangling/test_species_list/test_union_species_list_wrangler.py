"""Tests the species list union wrangler."""
import numpy as np

from lmpy.data_wrangling.species_list.union_species_list_wrangler import (
    UnionSpeciesListWrangler,
)
from lmpy.species_list import SpeciesList


# .....................................................................................
def test_union_species_list():
    """Tests the UnionSpeciesListWrangler with random data."""
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)

    val_1 = np.random.randint(500, 800)
    val_2 = np.random.randint(200, 500)
    species_list_a = SpeciesList(species_pool[:val_1])
    species_list_b = SpeciesList(species_pool[val_2:])

    # Wrangler
    wrangler = UnionSpeciesListWrangler(species_list_b)
    wrangled_list = wrangler.wrangle_species_list(species_list_a)

    # Check that our contents are what we expect
    assert len(wrangled_list) == len(species_pool)
    for name in wrangled_list:
        assert name in species_list_b or name in species_list_a

    # Check report
    report = wrangler.get_report()
    assert report['added'] == len(wrangled_list) - len(species_list_a)


# .....................................................................................
def test_union_species_list_total_overlap():
    """Tests the UnionSpeciesListWrangler with random data."""
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)

    val_2 = np.random.randint(200, 500)
    species_list_b = SpeciesList(species_pool[val_2:])

    # Wrangler
    wrangler = UnionSpeciesListWrangler(species_list_b)
    wrangled_list = wrangler.wrangle_species_list(species_list_b)

    # Check that our contents are what we expect
    assert len(wrangled_list) == len(species_list_b)
    for name in wrangled_list:
        assert name in species_list_b

    # Check report
    report = wrangler.get_report()
    assert report['added'] == 0
