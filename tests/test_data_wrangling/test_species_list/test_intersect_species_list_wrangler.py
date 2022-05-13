"""Tests the species list intersect wrangler."""
import numpy as np

from lmpy.data_wrangling.species_list.intersect_species_list_wrangler import (
    IntersectionSpeciesListWrangler,
)
from lmpy.species_list import SpeciesList


# .....................................................................................
def test_intersect_species_list():
    """Tests the IntersectionSpeciesListWrangler with random data."""
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)

    val_1 = np.random.randint(500, 800)
    val_2 = np.random.randint(200, 500)
    species_list_a = SpeciesList(species_pool[:val_1])
    species_list_b = SpeciesList(species_pool[val_2:])

    # Wrangler
    wrangler = IntersectionSpeciesListWrangler(species_list_b)
    wrangled_list = wrangler.wrangle_species_list(species_list_a)

    # Check that our contents are what we expect
    assert len(wrangled_list) == val_1 - val_2
    for name in wrangled_list:
        assert name in species_list_b
        assert name in species_list_a

    # Check report
    report = wrangler.get_report()
    assert report['removed'] == len(species_list_a) - len(wrangled_list)


# .....................................................................................
def test_intersect_species_list_disjoint():
    """Tests the IntersectionSpeciesListWrangler with random data."""
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)

    val_1 = np.random.randint(501, 800)
    val_2 = np.random.randint(200, 499)
    species_list_a = SpeciesList(species_pool[:val_2])
    species_list_b = SpeciesList(species_pool[val_1:])

    # Wrangler
    wrangler = IntersectionSpeciesListWrangler(species_list_b)
    wrangled_list = wrangler.wrangle_species_list(species_list_a)

    # Check that our contents are what we expect
    assert len(wrangled_list) == 0

    # Check report
    report = wrangler.get_report()
    assert report['removed'] == len(species_list_a)
