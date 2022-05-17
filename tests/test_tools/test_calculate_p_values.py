"""Tests the calculate_p_values module."""
import json
import numpy as np
import pytest

from lmpy.matrix import Matrix
from lmpy.tools.calculate_p_values import cli


# .....................................................................................
@pytest.fixture(scope='function', params=['raw', 'fdr', 'bonferroni', None])
def significance_method(request):
    """A fixture providing a significance method to use for p-value correction.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        str: The name of a signficance method.
    """
    yield request.param


# .....................................................................................
@pytest.fixture(scope='function', params=[True, False])
def use_abs_value(request):
    """A fixture providing a boolean indicating if absolute value should be used.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        bool: Should absolute value be used.
    """
    yield request.param


# .....................................................................................
@pytest.fixture(scope='function', params=[True, False])
def use_config_file(request):
    """A fixture providing a boolean indicating if a config file should be used.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        bool: Should config file be used.
    """
    yield request.param


# .....................................................................................
@pytest.fixture(scope='function', params=[True, False])
def use_permutations(request):
    """A fixture providing a boolean indicating if extra permutations should be used.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        bool: Should extra permutations be used.
    """
    yield request.param


# .....................................................................................
def test_calculate_p_values(
        monkeypatch,
        generate_temp_filename,
        significance_method,
        use_abs_value,
        use_config_file,
        use_permutations
):
    """Test the calculate_p_values tool.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): Fixture for generating temp files.
        significance_method (pytest.Fixture): Fixture providing a significance method
            identifer string.
        use_abs_value (pytest.Fixture): Fixture providing boolean indicating if
            absolute value comparison should be used.
        use_config_file (pytest.Fixture): Fixture providing boolean indicating if
            config file should be used.
        use_permutations (pytest.Fixture): Fixture providing boolean indicating if
            extra permutations should be used.
    """
    min_rand, max_rand = (10, 100)
    if use_abs_value:
        obs_min, obs_max = (-40, 40)
        rand_min, rand_max = (-20, 20)
    else:
        obs_min, obs_max = (5, 40)
        rand_min, rand_max = (0, 20)
    num_rows, num_cols = (np.random.randint(5, 10), np.random.randint(5, 10))
    params = ['calculate_p_values.py']

    p_value_matrix_filename = generate_temp_filename(suffix='.lmm')

    # Generate observed data
    obs_matrix_filename = generate_temp_filename(suffix='.lmm')
    obs_mtx = Matrix(
        np.random.randint(obs_min, obs_max, size=(num_rows, num_cols))
    )
    obs_mtx.write(obs_matrix_filename)

    rand_matrix_filename = []
    for _ in range(np.random.randint(min_rand, max_rand)):
        fn = generate_temp_filename(suffix='.lmm')
        rand_mtx = Matrix(
            np.random.randint(rand_min, rand_max, size=(num_rows, num_cols))
        )
        rand_mtx.write(fn)
        rand_matrix_filename.append(fn)

    significance_matrix_filename = None
    if significance_method is not None:
        significance_matrix_filename = generate_temp_filename(suffix='.lmm')

    if use_config_file:
        script_config = {
            'abs': use_abs_value,
            'p_values_matrix': p_value_matrix_filename,
            'observed_matrix': obs_matrix_filename,
            'random_matrix': rand_matrix_filename,
        }
        if significance_method is not None:
            script_config['significance_method'] = significance_method
        if use_permutations:
            script_config['num_permutations'] = 100
        if significance_method is not None:
            script_config[
                'significance_matrix_filename'
            ] = significance_matrix_filename
        config_fn = generate_temp_filename(suffix='.json')
        with open(config_fn, mode='wt') as out_config:
            json.dump(script_config, out_config)
        params.extend(['--config_file', config_fn])

    else:
        if significance_method is not None:
            params.extend(['--significance_method', significance_method])
        if use_permutations:
            params.extend(['-n', '100'])
        if use_abs_value:
            params.append('--abs')
        if significance_method is not None:
            params.extend(['-s', significance_matrix_filename])
        params.extend([p_value_matrix_filename, obs_matrix_filename])
        params.extend(rand_matrix_filename)

    monkeypatch.setattr('sys.argv', params)
    cli()

    # Test p-values matrix
    p_values_matrix = Matrix.load(p_value_matrix_filename)
    assert p_values_matrix.max() <= 1.0
    assert p_values_matrix.min() >= 0
    assert p_values_matrix.max() > 0

    # Test significance matrix (if created)
    if significance_matrix_filename is not None:
        sig_mtx = Matrix.load(significance_matrix_filename)
        assert sig_mtx.sum() > 0
        assert sig_mtx.sum() < num_rows * num_cols
