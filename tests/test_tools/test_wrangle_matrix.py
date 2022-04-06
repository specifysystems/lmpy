"""Test the wrangle matrix tool."""
from copy import deepcopy
import json

import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools.wrangle_matrix import cli

from tests.data_simulator import generate_tree


# .....................................................................................
def test_wrangle_matrix(monkeypatch, generate_temp_filename):
    """Test the wrangle_matrix tool.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Generate species set
    all_species = [f'Species {i}' for i in range(100)]
    # Tree species
    np.random.shuffle(all_species)
    tree_species = all_species[:np.random.randint(51, 100)]
    # Subset species
    np.random.shuffle(all_species)
    subset_species = all_species[:np.random.randint(51, 100)]
    # Matrix species
    np.random.shuffle(all_species)
    matrix_species = all_species[:np.random.randint(51, 100)]

    # Generate filenames
    tree_filename = generate_temp_filename(suffix='.tre')
    in_matrix_filename = generate_temp_filename(suffix='.lmm')
    out_matrix_filename = generate_temp_filename(suffix='.lmm')
    num_rows = 100
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    report_filename = generate_temp_filename(suffix='.json')

    # Generate and write tree
    tree = generate_tree(deepcopy(tree_species))
    tree.write(path=tree_filename, schema='newick')

    # Generate and write matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(in_matrix_filename)

    # Generate and write wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'SubsetReorderSlicesWrangler',
            'axes': {
                '0': [f'Row {j}' for j in range(num_rows // 2)],
                '1': subset_species
            }
        },
        {
            'wrangler_type': 'MatchTreeMatrixWrangler',
            'tree': tree_filename,
            'species_axis': 1
        }
    ]
    with open(wrangler_config_filename, mode='wt') as config_out:
        json.dump(wrangler_config, config_out)

    # Wrangle matrix
    params = [
        'wrangle_matrix.py',
        '-r',
        report_filename,
        in_matrix_filename,
        wrangler_config_filename,
        out_matrix_filename,
    ]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Load matrix
    wrangled_matrix = Matrix.load(out_matrix_filename)

    # Check that every taxon name is in tree, subset, and matrix species lists
    for sp in wrangled_matrix.get_column_headers():
        assert sp in tree_species
        assert sp in subset_species
        assert sp in matrix_species

    # Check report
    with open(report_filename, mode='rt') as report_in:
        report = json.load(report_in)
    total_purged = sum(
        int(
            wrangler_report['changes']['1']['purged']
        ) for wrangler_report in report
    )
    assert len(
        wrangled_matrix.get_column_headers()
    ) == len(matrix_species) - total_purged
