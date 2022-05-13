"""Test the accepted_name_wrangler module."""
import numpy as np

from lmpy.data_wrangling.species_list.accepted_name_wrangler import (
    AcceptedNameSpeciesListWrangler,
)
from lmpy.species_list import SpeciesList

from tests.data_simulator import generate_tree


# .....................................................................................
def test_accepted_name_wrangler():
    """Tests the accepted name wrangler for species list."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(20)
    }
    species_list = SpeciesList(list(name_map.keys()))

    # Wrangle points
    wrangler = AcceptedNameSpeciesListWrangler(name_map=name_map)
    wrangled_species_list = wrangler.wrangle_species_list(species_list)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for name in wrangled_species_list:
        assert name in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['unresolved'] >= 0
    assert report['duplicates'] >= 0
