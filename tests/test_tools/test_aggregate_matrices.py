"""Tests for the aggregate_matrices tool."""
import json

import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools.aggregate_matrices import cli


# .....................................................................................
def test_add_matrices_simple(monkeypatch, generate_temp_filename):
    """Simple test to check basic functionality of aggregate matrices (add).

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): Fixture to generate temp filenames.
    """
    num_rows = np.random.randint(1, 10)
    num_cols = np.random.randint(1, 10)
    total_depth = 0
    matrix_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(1, 10))
    ]
    # Generate some test matrices
    for fn in matrix_filenames:
        mtx_depth = np.random.randint(0, 10)
        # If depth is zero, add 2d array
        if mtx_depth == 0:
            total_depth += 1
            test_mtx = Matrix(np.ones((num_rows, num_cols), dtype=int))
        else:
            # add 3d array
            total_depth += mtx_depth
            test_mtx = Matrix(np.ones((num_rows, num_cols, mtx_depth), dtype=int))
        test_mtx.write(fn)

    out_matrix_filename = generate_temp_filename(suffix='.lmm')
    params = [
        'aggregate_matrices.py',
        '--ndim',
        '2',
        'add',
        '2',
        out_matrix_filename,
    ]
    params.extend(matrix_filenames)
    monkeypatch.setattr('sys.argv', params)
    cli()
    # Check that the aggregated matrix is what we expect
    # We expect that we'll have a matrix with shape (num_rows, num_cols) with
    #     total_depth as every value.
    test_output_matrix = Matrix.load(out_matrix_filename)
    assert test_output_matrix.shape == (num_rows, num_cols)
    test_vals = total_depth * np.ones((num_rows, num_cols), dtype=int)
    assert np.all(test_vals == test_output_matrix)


# .....................................................................................
def test_add_matrices_simple_config(monkeypatch, generate_temp_filename):
    """Simple test to check basic functionality of aggregate matrices (add).

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): Fixture to generate temp filenames.
    """
    num_rows = np.random.randint(1, 10)
    num_cols = np.random.randint(1, 10)
    total_depth = 0
    matrix_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(1, 10))
    ]
    # Generate some test matrices
    for fn in matrix_filenames:
        mtx_depth = np.random.randint(0, 10)
        # If depth is zero, add 2d array
        if mtx_depth == 0:
            total_depth += 1
            test_mtx = Matrix(np.ones((num_rows, num_cols), dtype=int))
        else:
            # add 3d array
            total_depth += mtx_depth
            test_mtx = Matrix(np.ones((num_rows, num_cols, mtx_depth), dtype=int))
        test_mtx.write(fn)

    out_matrix_filename = generate_temp_filename(suffix='.lmm')
    config_fn = generate_temp_filename(suffix='.json')
    script_config = {
        'method': 'add',
        'axis': 2,
        'ndim': 2,
        'input_matrix_filename': matrix_filenames,
        'output_matrix_filename': out_matrix_filename
    }
    with open(config_fn, mode='wt') as out_config:
        json.dump(script_config, out_config)

    params = [
        'aggregate_matrices.py',
        '--config_file',
        config_fn
    ]
    monkeypatch.setattr('sys.argv', params)
    cli()
    # Check that the aggregated matrix is what we expect
    # We expect that we'll have a matrix with shape (num_rows, num_cols) with
    #     total_depth as every value.
    test_output_matrix = Matrix.load(out_matrix_filename)
    assert test_output_matrix.shape == (num_rows, num_cols)
    test_vals = total_depth * np.ones((num_rows, num_cols), dtype=int)
    assert np.all(test_vals == test_output_matrix)


# .....................................................................................
def test_concatenate_matrices_simple(monkeypatch, generate_temp_filename):
    """Simple test to check basic functionality of aggregate matrices (concatenate).

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): Fixture to generate temp filenames.
    """
    num_rows = np.random.randint(1, 10)
    num_cols = np.random.randint(1, 10)
    total_depth = 0
    matrix_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(1, 10))
    ]
    # Generate some test matrices
    for fn in matrix_filenames:
        mtx_depth = np.random.randint(0, 10)
        # If depth is zero, add 2d array
        if mtx_depth == 0:
            total_depth += 1
            test_mtx = Matrix(np.ones((num_rows, num_cols), dtype=int))
        else:
            # add 3d array
            total_depth += mtx_depth
            test_mtx = Matrix(np.ones((num_rows, num_cols, mtx_depth), dtype=int))
        test_mtx.write(fn)

    out_matrix_filename = generate_temp_filename(suffix='.lmm')
    params = [
        'aggregate_matrices.py',
        'concatenate',
        '2',
        out_matrix_filename,
    ]
    params.extend(matrix_filenames)
    monkeypatch.setattr('sys.argv', params)
    cli()
    # Check that the aggregated matrix has the correct shape:
    #     (num_rows, num_cols, total_depth)
    test_output_matrix = Matrix.load(out_matrix_filename)
    assert test_output_matrix.shape == (num_rows, num_cols, total_depth)


# .....................................................................................
def test_concatenate_matrices_simple_config(monkeypatch, generate_temp_filename):
    """Simple test to check basic functionality of aggregate matrices (concatenate).

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): Fixture to generate temp filenames.
    """
    num_rows = np.random.randint(1, 10)
    num_cols = np.random.randint(1, 10)
    total_depth = 0
    matrix_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(2, 10))
    ]
    # Generate some test matrices
    for fn in matrix_filenames:
        mtx_depth = np.random.randint(0, 10)
        # If depth is zero, add 2d array
        if mtx_depth == 0:
            total_depth += 1
            test_mtx = Matrix(np.ones((num_rows, num_cols), dtype=int))
        else:
            # add 3d array
            total_depth += mtx_depth
            test_mtx = Matrix(np.ones((num_rows, num_cols, mtx_depth), dtype=int))
        test_mtx.write(fn)

    out_matrix_filename = generate_temp_filename(suffix='.lmm')
    config_fn = generate_temp_filename(suffix='.json')
    script_config = {
        'method': 'concatenate',
        'axis': 2,
        'input_matrix_filename': matrix_filenames,
        'output_matrix_filename': out_matrix_filename
    }
    with open(config_fn, mode='wt') as out_config:
        json.dump(script_config, out_config)

    params = [
        'aggregate_matrices.py',
        '--config_file',
        config_fn
    ]
    monkeypatch.setattr('sys.argv', params)
    cli()
    # Check that the aggregated matrix has the correct shape:
    #     (num_rows, num_cols, total_depth)
    test_output_matrix = Matrix.load(out_matrix_filename)
    assert test_output_matrix.shape == (num_rows, num_cols, total_depth)
