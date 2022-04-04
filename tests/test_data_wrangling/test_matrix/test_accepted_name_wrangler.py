"""Test the accepted_name_wrangler module."""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.data_wrangling.matrix.accepted_name_wrangler import (
    AcceptedNameMatrixWrangler,
)


# .....................................................................................
def test_accepted_name_wrangler_matrix():
    """Test the accepted_name_wrangler."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(20)
    }
    matrix = Matrix(
        np.random.randint(0, 100, size=(10, 20)),
        headers={'0': [str(i) for i in range(10)], '1': list(name_map.keys())}
    )

    # Wrangle points
    wrangler = AcceptedNameMatrixWrangler(name_map)
    wrangled_matrix = wrangler.wrangle_matrix(matrix)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for hdr in wrangled_matrix.get_column_headers():
        assert hdr in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['changes']['1']['modified'] == len(name_map.keys())
    assert report['changes']['1']['purged'] == 0


# .....................................................................................
def test_accepted_name_wrangler_unmatched_names_matrix():
    """Test the Accepted Name Wrangler with unmatched names."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(10)
    }
    raw_names = list(name_map.keys())
    raw_names.extend([f'Unmatched {i}' for i in range(10)])

    matrix = Matrix(
        np.random.randint(0, 100, size=(10, 20)),
        headers={'0': [str(i) for i in range(10)], '1': raw_names}
    )

    # Wrangle points
    wrangler = AcceptedNameMatrixWrangler(name_map)
    wrangled_matrix = wrangler.wrangle_matrix(matrix)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for hdr in wrangled_matrix.get_column_headers():
        assert hdr in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['changes']['1']['modified'] == len(name_map.keys())
    assert report['changes']['1']['purged'] == 10
