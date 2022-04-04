"""Test the accepted_name_wrangler module."""
import numpy as np

from lmpy.data_wrangling.tree.accepted_name_wrangler import (
    AcceptedNameTreeWrangler,
)

from tests.data_simulator import generate_tree


# .....................................................................................
def test_accepted_name_wrangler_tree():
    """Test the accepted_name_wrangler."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(20)
    }
    tree = generate_tree(list(name_map.keys()))

    # Wrangle points
    wrangler = AcceptedNameTreeWrangler(name_map)
    wrangled_tree = wrangler.wrangle_tree(tree)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['modified'] == len(name_map.keys())
    assert report['purged'] == 0


# .....................................................................................
def test_accepted_name_wrangler_unmatched_names_tree():
    """Test the Accepted Name Wrangler with unmatched names."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(10)
    }
    raw_names = list(name_map.keys())
    raw_names.extend([f'Unmatched {i}' for i in range(10)])

    tree = generate_tree(raw_names)

    # Wrangle points
    wrangler = AcceptedNameTreeWrangler(name_map)
    wrangled_tree = wrangler.wrangle_tree(tree)

    # Test that names are correct
    accepted_names = list(name_map.values())

    # Test that names are correct
    accepted_names = list(name_map.values())

    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['modified'] == len(name_map.keys())
    assert report['purged'] == 10
