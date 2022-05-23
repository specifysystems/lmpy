"""Test the wrangle_species_list tool."""
import json

import numpy as np

from lmpy.matrix import Matrix
from lmpy.species_list import SpeciesList
from lmpy.tools.wrangle_species_list import cli

from tests.data_simulator import generate_tree


# .....................................................................................
def test_wrangle_species_list(monkeypatch, generate_temp_filename):
    """Test the wrangle_species_list tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
    """
    # Generate filenames
    in_species_list_filename = generate_temp_filename(suffix='.txt')
    species_list_second_half_filename = generate_temp_filename(suffix='.txt')
    species_pool_subset_filename = generate_temp_filename(suffix='.txt')
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    out_species_list_filename = generate_temp_filename(suffix='.txt')
    report_filename = generate_temp_filename(suffix='.json')
    matrix_filename = generate_temp_filename(suffix='.lmm')
    tree_filename = generate_temp_filename(suffix='.tre')
    log_filename = generate_temp_filename(suffix='.log')
    tree_schema = 'newick'
    num_rows = 100

    # Generate species lists
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)
    list_break = np.random.randint(50, len(species_pool) - 50)

    species_list = SpeciesList(species_pool[:list_break])
    species_list.write(in_species_list_filename)

    second_half_species_list = SpeciesList(species_pool[list_break:])
    second_half_species_list.write(species_list_second_half_filename)

    subset_pool = SpeciesList(
        species_pool[np.random.randint(100, 450):np.random.randint(550, 900)]
    )
    subset_pool.write(species_pool_subset_filename)

    # Get tree and matrix species sets
    val_1 = np.random.randint(20, len(subset_pool) - 20)
    val_2 = np.random.randint(0, val_1)
    matrix_species = list(subset_pool)[:val_1]
    tree_species = list(subset_pool)[val_2:]
    tree_species.append('Removethis species')  # Ensure 1+ will be removed
    common_species = set(matrix_species).intersection(set(tree_species))

    # Create matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Create tree
    tree = generate_tree(tree_species)
    tree.write(path=tree_filename, schema=tree_schema)

    # Generate wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'UnionSpeciesListWrangler',
            'species_list': species_list_second_half_filename,
        },
        {
            'wrangler_type': 'IntersectionSpeciesListWrangler',
            'species_list': species_pool_subset_filename,
        },
        {
            'wrangler_type': 'MatchMatrixSpeciesListWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        },
        {
            'wrangler_type': 'MatchTreeSpeciesListWrangler',
            'tree': tree_filename,
        }
    ]
    with open(wrangler_config_filename, mode='wt') as out_json:
        json.dump(wrangler_config, out_json)

    # Run encoding tool
    params = [
        'wrangle_species_list.py',
        '-r',
        report_filename,
        '--log_filename',
        log_filename,
        in_species_list_filename,
        wrangler_config_filename,
        out_species_list_filename,
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()

    # Load the output species list
    out_species_list = SpeciesList.from_file(out_species_list_filename)

    assert len(out_species_list) < len(species_pool)
    for name in out_species_list:
        assert name in species_pool

    # Check that log was created and has contents
    num_log_lines = 0
    with open(log_filename, mode='rt') as log_in:
        for _ in log_in:
            num_log_lines += 1
    assert num_log_lines > 0

    # Load report
    with open(report_filename, mode='rt') as in_json:
        report = json.load(in_json)

    for wrangler_report in report:
        if wrangler_report['name'] == 'UnionSpeciesListWrangler':
            assert wrangler_report['added'] > 0
            assert wrangler_report['added'] == len(second_half_species_list)
        elif wrangler_report['name'] == 'IntersectionSpeciesListWrangler':
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == (
                len(species_list) + len(second_half_species_list)
            ) - len(subset_pool)
        elif wrangler_report['name'] == 'MatchMatrixSpeciesListWrangler':
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == len(subset_pool) - len(matrix_species)
        else:
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == \
                   len(matrix_species) - len(common_species)


# .....................................................................................
def test_wrangle_species_list_script(script_runner, generate_temp_filename):
    """Test the wrangle_species_list tool.

    Args:
        script_runner (pytest.Fixture): A fixture for running a script.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
    """
    # Generate filenames
    in_species_list_filename = generate_temp_filename(suffix='.txt')
    species_list_second_half_filename = generate_temp_filename(suffix='.txt')
    species_pool_subset_filename = generate_temp_filename(suffix='.txt')
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    out_species_list_filename = generate_temp_filename(suffix='.txt')
    report_filename = generate_temp_filename(suffix='.json')
    matrix_filename = generate_temp_filename(suffix='.lmm')
    tree_filename = generate_temp_filename(suffix='.tre')
    log_filename = generate_temp_filename(suffix='.log')
    tree_schema = 'newick'
    num_rows = 100

    # Generate species lists
    species_pool = [f'Species {i}' for i in range(1000)]
    np.random.shuffle(species_pool)
    list_break = np.random.randint(50, len(species_pool) - 50)

    species_list = SpeciesList(species_pool[:list_break])
    species_list.write(in_species_list_filename)

    second_half_species_list = SpeciesList(species_pool[list_break:])
    second_half_species_list.write(species_list_second_half_filename)

    subset_pool = SpeciesList(
        species_pool[np.random.randint(100, 450):np.random.randint(550, 900)]
    )
    subset_pool.write(species_pool_subset_filename)

    # Get tree and matrix species sets
    val_1 = np.random.randint(20, len(subset_pool) - 20)
    val_2 = np.random.randint(0, val_1)
    matrix_species = list(subset_pool)[:val_1]
    tree_species = list(subset_pool)[val_2:]
    tree_species.append('Removethis species')  # Ensure 1+ will be removed
    common_species = set(matrix_species).intersection(set(tree_species))

    # Create matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Create tree
    tree = generate_tree(tree_species)
    tree.write(path=tree_filename, schema=tree_schema)

    # Generate wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'UnionSpeciesListWrangler',
            'species_list': species_list_second_half_filename,
        },
        {
            'wrangler_type': 'IntersectionSpeciesListWrangler',
            'species_list': species_pool_subset_filename,
        },
        {
            'wrangler_type': 'MatchMatrixSpeciesListWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        },
        {
            'wrangler_type': 'MatchTreeSpeciesListWrangler',
            'tree': tree_filename,
        }
    ]
    with open(wrangler_config_filename, mode='wt') as out_json:
        json.dump(wrangler_config, out_json)

    # Run encoding tool
    params = [
        '-r',
        report_filename,
        '--log_filename',
        log_filename,
        in_species_list_filename,
        wrangler_config_filename,
        out_species_list_filename,
    ]

    script_runner('wrangle_species_list', 'lmpy.tools.wrangle_species_list', params)

    # Load the output species list
    out_species_list = SpeciesList.from_file(out_species_list_filename)

    assert len(out_species_list) < len(species_pool)
    for name in out_species_list:
        assert name in species_pool

    # Check that log was created and has contents
    num_log_lines = 0
    with open(log_filename, mode='rt') as log_in:
        for _ in log_in:
            num_log_lines += 1
    assert num_log_lines > 0

    # Load report
    with open(report_filename, mode='rt') as in_json:
        report = json.load(in_json)

    for wrangler_report in report:
        if wrangler_report['name'] == 'UnionSpeciesListWrangler':
            assert wrangler_report['added'] > 0
            assert wrangler_report['added'] == len(second_half_species_list)
        elif wrangler_report['name'] == 'IntersectionSpeciesListWrangler':
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == (
                len(species_list) + len(second_half_species_list)
            ) - len(subset_pool)
        elif wrangler_report['name'] == 'MatchMatrixSpeciesListWrangler':
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == len(subset_pool) - len(matrix_species)
        else:
            assert wrangler_report['removed'] > 0
            assert wrangler_report['removed'] == \
                   len(matrix_species) - len(common_species)
