"""Test the accepted_name_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.matrix import Matrix
from lmpy.data_wrangling.matrix.purge_empty_slices_wrangler import (
    PurgeEmptySlicesWrangler,
)


# .....................................................................................
def test_purge_empty_slices_wrangler_2d():
    """Test purging a matrix with empty rows and columns."""
    # Create test matrix
    test_matrix = Matrix(
        np.ones((5, 7)),
        headers={
            '0': [f'Row {i}' for i in range(5)],
            '1': [f'Species {j}' for j in range(7)]
        }
    )
    test_matrix[1] = 0
    test_matrix[3] = 0
    test_matrix[:, 4] = 0
    test_matrix[:, 0] = 0

    # Purge rows
    wrangler_1 = PurgeEmptySlicesWrangler(purge_axes=0)
    wrangled_matrix_1 = wrangler_1.wrangle_matrix(deepcopy(test_matrix))
    # Assert that the rows were removed but nothing else
    assert wrangled_matrix_1.shape == (3, 7)
    report_1 = wrangler_1.get_report()
    assert report_1['changes']['0']['purged'] == 2
    assert list(report_1['changes'].keys()) == ['0']

    # Purge columns
    wrangler_2 = PurgeEmptySlicesWrangler(purge_axes=[1])
    wrangled_matrix_2 = wrangler_2.wrangle_matrix(deepcopy(test_matrix))
    # Assert that the columns were removed but nothing else
    assert wrangled_matrix_2.shape == (5, 5)
    report_2 = wrangler_2.get_report()
    assert report_2['changes']['1']['purged'] == 2
    assert list(report_2['changes'].keys()) == ['1']

    # Purge both
    wrangler_3 = PurgeEmptySlicesWrangler()
    wrangled_matrix_3 = wrangler_3.wrangle_matrix(deepcopy(test_matrix))
    # Assert that the rows and columns were removed but nothing else
    assert wrangled_matrix_3.shape == (3, 5)
    report_3 = wrangler_3.get_report()
    assert report_3['changes']['0']['purged'] == 2
    assert report_3['changes']['1']['purged'] == 2
    assert list(report_3['changes'].keys()) == ['0', '1']


# .....................................................................................
def test_purge_empty_slices_wrangler_3d():
    """Test purging a matrix with more than two dimensions."""
    # Create test matrix
    test_matrix = Matrix(
        np.ones((5, 7, 4)),
        headers={
            '0': [f'Row {i}' for i in range(5)],
            '1': [f'Species {j}' for j in range(7)],
            '2': [f'Plane {k}' for k in range(4)]
        }
    )
    test_matrix[1] = 0
    test_matrix[3] = 0
    test_matrix[:, 4] = 0
    test_matrix[:, 0] = 0
    test_matrix[:, :, 2] = 0

    # Purge
    wrangler = PurgeEmptySlicesWrangler()
    wrangled_matrix = wrangler.wrangle_matrix(deepcopy(test_matrix))

    # We should purge 2 row, 2 columns, 1 plane
    assert wrangled_matrix.shape == (3, 5, 3)

    report = wrangler.get_report()
    assert report['changes']['0']['purged'] == 2
    assert report['changes']['1']['purged'] == 2
    assert report['changes']['2']['purged'] == 1
    assert list(report['changes'].keys()) == ['0', '1', '2']


# .....................................................................................
def test_purge_empty_slices_wrangler_not_empty():
    """Test purging a matrix that has no empty slices."""
    # Create test matrix
    test_matrix = Matrix(
        np.ones((5, 7)),
        headers={
            '0': [f'Row {i}' for i in range(5)],
            '1': [f'Species {j}' for j in range(7)]
        }
    )

    # Attempt to purge
    wrangler = PurgeEmptySlicesWrangler()
    wrangled_matrix = wrangler.wrangle_matrix(deepcopy(test_matrix))

    # No empty rows or columns so shape should be the same and no changes
    assert wrangled_matrix.shape == (5, 7)
    report = wrangler.get_report()
    assert len(report['changes'].keys()) == 2
    assert report['changes']['0']['purged'] == 0
    assert report['changes']['1']['purged'] == 0
