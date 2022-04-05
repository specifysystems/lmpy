"""Test the accepted_name_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.matrix import Matrix
from lmpy.data_wrangling.matrix.subset_reorder_slices_wrangler import (
    SubsetReorderSlicesWrangler,
)


# .....................................................................................
def test_subset_reorder_slices_wrangler():
    """Test subsetting and reordering matrix slices."""
    # Create test matrix
    test_matrix = Matrix(
        np.ones((5, 7)),
        headers={
            '0': [f'Row {i}' for i in range(5)],
            '1': [f'Species {j}' for j in range(7)]
        }
    )

    # Subset rows
    wrangler_1 = SubsetReorderSlicesWrangler({'0': ['Row 3', 'Row 2', 'Row 4']})
    wrangled_matrix_1 = wrangler_1.wrangle_matrix(deepcopy(test_matrix))

    # Assert that the rows were removed but nothing else
    assert wrangled_matrix_1.shape == (3, 7)
    report_1 = wrangler_1.get_report()
    assert report_1['changes']['0']['purged'] == 2
    assert list(report_1['changes'].keys()) == ['0']
    assert wrangled_matrix_1.get_row_headers() == ['Row 3', 'Row 2', 'Row 4']
    assert wrangled_matrix_1.get_column_headers() == [f'Species {j}' for j in range(7)]

    # Subset columns and include one that isn't present
    wrangler_2 = SubsetReorderSlicesWrangler(
        {
            '1': ['Species 0', 'Species 3', 'Species 5', 'Species 2', 'Species 99999']
        }
    )
    wrangled_matrix_2 = wrangler_2.wrangle_matrix(deepcopy(test_matrix))
    # Assert that the columns were removed but nothing else
    assert wrangled_matrix_2.shape == (5, 4)
    report_2 = wrangler_2.get_report()
    assert report_2['changes']['1']['purged'] == 3
    assert list(report_2['changes'].keys()) == ['1']
    assert wrangled_matrix_2.get_row_headers() == [f'Row {i}' for i in range(5)]
    assert wrangled_matrix_2.get_column_headers() == [
        'Species 0',
        'Species 3',
        'Species 5',
        'Species 2',
    ]

    # Purge both
    wrangler_3 = SubsetReorderSlicesWrangler(
        {
            '0': ['Row 3', 'Row 2', 'Row 4'],
            '1': ['Species 0', 'Species 3', 'Species 5', 'Species 2', 'Species 99999']
        }
    )
    wrangled_matrix_3 = wrangler_3.wrangle_matrix(deepcopy(test_matrix))
    # Assert that the rows and columns were removed but nothing else
    assert wrangled_matrix_3.shape == (3, 4)
    report_3 = wrangler_3.get_report()
    assert report_3['changes']['0']['purged'] == 2
    assert report_3['changes']['1']['purged'] == 3
    assert list(report_3['changes'].keys()) == ['0', '1']
    assert wrangled_matrix_3.get_row_headers() == ['Row 3', 'Row 2', 'Row 4']
    assert wrangled_matrix_3.get_column_headers() == [
        'Species 0',
        'Species 3',
        'Species 5',
        'Species 2',
    ]
