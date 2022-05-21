"""Test the wrangle tree tool."""
from copy import deepcopy
import json

import numpy as np

from lmpy.matrix import Matrix
from lmpy.tree import TreeWrapper
from lmpy.tools.wrangle_tree import cli

from tests.data_simulator import generate_tree


# .....................................................................................
def test_wrangle_tree(monkeypatch, generate_temp_filename):
    """Test the wrangle_tree tool.

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
    in_tree_filename = generate_temp_filename(suffix='.tre')
    in_tree_format = 'newick'
    out_tree_filename = generate_temp_filename(suffix='.nexus')
    out_tree_format = 'nexus'
    matrix_filename = generate_temp_filename(suffix='.lmm')
    num_rows = 100
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    report_filename = generate_temp_filename(suffix='.json')

    # Generate and write tree
    in_tree = generate_tree(deepcopy(tree_species))
    in_tree.write(path=in_tree_filename, schema=in_tree_format)

    # Generate and write matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Generate and write wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'SubsetTreeWrangler',
            'keep_taxa': subset_species
        },
        {
            'wrangler_type': 'MatchMatrixTreeWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        }
    ]
    with open(wrangler_config_filename, mode='wt') as config_out:
        json.dump(wrangler_config, config_out)

    # Wrangle tree
    params = [
        'wrangle_tree.py',
        '-r',
        report_filename,
        in_tree_filename,
        in_tree_format,
        wrangler_config_filename,
        out_tree_filename,
        out_tree_format,
    ]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Load tree
    wrangled_tree = TreeWrapper.get(path=out_tree_filename, schema=out_tree_format)

    # Check that every taxon name is in tree, subset, and matrix species lists
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in tree_species
        assert taxon.label in subset_species
        assert taxon.label in matrix_species

    # Check report
    with open(report_filename, mode='rt') as report_in:
        report = json.load(report_in)
    total_purged = sum(int(wrangler_report['purged']) for wrangler_report in report)
    assert len(wrangled_tree.taxon_namespace) == len(tree_species) - total_purged


# .....................................................................................
def test_wrangle_tree_script(script_runner, generate_temp_filename):
    """Test the wrangle_tree tool.

    Args:
        script_runner (pytest.Fixture): A fixture for running a script.
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
    in_tree_filename = generate_temp_filename(suffix='.tre')
    in_tree_format = 'newick'
    out_tree_filename = generate_temp_filename(suffix='.nexus')
    out_tree_format = 'nexus'
    matrix_filename = generate_temp_filename(suffix='.lmm')
    num_rows = 100
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    report_filename = generate_temp_filename(suffix='.json')

    # Generate and write tree
    in_tree = generate_tree(deepcopy(tree_species))
    in_tree.write(path=in_tree_filename, schema=in_tree_format)

    # Generate and write matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Generate and write wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'SubsetTreeWrangler',
            'keep_taxa': subset_species
        },
        {
            'wrangler_type': 'MatchMatrixTreeWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        }
    ]
    with open(wrangler_config_filename, mode='wt') as config_out:
        json.dump(wrangler_config, config_out)

    # Wrangle tree
    params = [
        '-r',
        report_filename,
        in_tree_filename,
        in_tree_format,
        wrangler_config_filename,
        out_tree_filename,
        out_tree_format,
    ]
    script_runner('wrangle_tree', 'lmpy.tools.wrangle_tree', params)

    # Load tree
    wrangled_tree = TreeWrapper.get(path=out_tree_filename, schema=out_tree_format)

    # Check that every taxon name is in tree, subset, and matrix species lists
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in tree_species
        assert taxon.label in subset_species
        assert taxon.label in matrix_species

    # Check report
    with open(report_filename, mode='rt') as report_in:
        report = json.load(report_in)
    total_purged = sum(int(wrangler_report['purged']) for wrangler_report in report)
    assert len(wrangled_tree.taxon_namespace) == len(tree_species) - total_purged


# .....................................................................................
def test_wrangle_tree_config_file(monkeypatch, generate_temp_filename):
    """Test the wrangle_tree tool using a configuration file.

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
    in_tree_filename = generate_temp_filename(suffix='.tre')
    in_tree_format = 'newick'
    out_tree_filename = generate_temp_filename(suffix='.nexus')
    out_tree_format = 'nexus'
    matrix_filename = generate_temp_filename(suffix='.lmm')
    num_rows = 100
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    report_filename = generate_temp_filename(suffix='.json')

    # Generate and write tree
    in_tree = generate_tree(deepcopy(tree_species))
    in_tree.write(path=in_tree_filename, schema=in_tree_format)

    # Generate and write matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Generate and write wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'SubsetTreeWrangler',
            'keep_taxa': subset_species
        },
        {
            'wrangler_type': 'MatchMatrixTreeWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        }
    ]
    with open(wrangler_config_filename, mode='wt') as config_out:
        json.dump(wrangler_config, config_out)

    # Create configuration file
    config_fn = generate_temp_filename(suffix='.json')
    with open(config_fn, mode='wt') as config_out:
        json.dump(
            {
                'report_filename': report_filename,
                'tree_filename': in_tree_filename,
                'tree_schema': in_tree_format,
                'wrangler_configuration_file': wrangler_config_filename,
                'out_tree_filename': out_tree_filename,
                'out_tree_schema': out_tree_format
            },
            config_out
        )
    # Wrangle tree
    params = [
        'wrangle_tree.py',
        '--config_file',
        config_fn,
    ]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Load tree
    wrangled_tree = TreeWrapper.get(path=out_tree_filename, schema=out_tree_format)

    # Check that every taxon name is in tree, subset, and matrix species lists
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in tree_species
        assert taxon.label in subset_species
        assert taxon.label in matrix_species

    # Check report
    with open(report_filename, mode='rt') as report_in:
        report = json.load(report_in)
    total_purged = sum(int(wrangler_report['purged']) for wrangler_report in report)
    assert len(wrangled_tree.taxon_namespace) == len(tree_species) - total_purged


# .....................................................................................
def test_wrangle_tree_config_file_script(script_runner, generate_temp_filename):
    """Test the wrangle_tree tool using a configuration file and script_runner.

    Args:
        script_runner (pytest.Fixture): A fixture for running scripts.
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
    in_tree_filename = generate_temp_filename(suffix='.tre')
    in_tree_format = 'newick'
    out_tree_filename = generate_temp_filename(suffix='.nexus')
    out_tree_format = 'nexus'
    matrix_filename = generate_temp_filename(suffix='.lmm')
    num_rows = 100
    wrangler_config_filename = generate_temp_filename(suffix='.json')
    report_filename = generate_temp_filename(suffix='.json')

    # Generate and write tree
    in_tree = generate_tree(deepcopy(tree_species))
    in_tree.write(path=in_tree_filename, schema=in_tree_format)

    # Generate and write matrix
    matrix = Matrix(
        np.ones((num_rows, len(matrix_species))),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': matrix_species
        }
    )
    matrix.write(matrix_filename)

    # Generate and write wrangler configuration
    wrangler_config = [
        {
            'wrangler_type': 'SubsetTreeWrangler',
            'keep_taxa': subset_species
        },
        {
            'wrangler_type': 'MatchMatrixTreeWrangler',
            'matrix': matrix_filename,
            'species_axis': 1
        }
    ]
    with open(wrangler_config_filename, mode='wt') as config_out:
        json.dump(wrangler_config, config_out)

    # Create configuration file
    config_fn = generate_temp_filename(suffix='.json')
    with open(config_fn, mode='wt') as config_out:
        json.dump(
            {
                'report_filename': report_filename,
                'tree_filename': in_tree_filename,
                'tree_schema': in_tree_format,
                'wrangler_configuration_file': wrangler_config_filename,
                'out_tree_filename': out_tree_filename,
                'out_tree_schema': out_tree_format
            },
            config_out
        )

    # Wrangle tree
    params = [
        '--config_file',
        config_fn,
    ]
    script_runner('wrangle_tree', 'lmpy.tools.wrangle_tree', params)

    # Load tree
    wrangled_tree = TreeWrapper.get(path=out_tree_filename, schema=out_tree_format)

    # Check that every taxon name is in tree, subset, and matrix species lists
    for taxon in wrangled_tree.taxon_namespace:
        assert taxon.label in tree_species
        assert taxon.label in subset_species
        assert taxon.label in matrix_species

    # Check report
    with open(report_filename, mode='rt') as report_in:
        report = json.load(report_in)
    total_purged = sum(int(wrangler_report['purged']) for wrangler_report in report)
    assert len(wrangled_tree.taxon_namespace) == len(tree_species) - total_purged
