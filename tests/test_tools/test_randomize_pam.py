"""Test the Randomize PAM tool."""
import json
import numpy as np
import pytest

from lmpy import Matrix
from lmpy.tools.randomize_pam import cli


# .....................................................................................
@pytest.fixture(
    scope='function', params=[(0.3, 100, 100), (0.25, 1000, 1000), (0.15, 10000, 10000)]
)
def observed_pam(request):
    """Generate a PAM for testing.

    Args:
        request (pytest.Fixture): Pytest fixture for parameterization.

    Yields:
        Matrix: A Presence Absence Matrix for testing.
    """
    fill, num_rows, num_cols = request.param
    pam = Matrix(
        np.random.choice([1, 0], (num_rows, num_cols), p=[fill, 1 - fill]),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': [f'Col {i}' for i in range(num_cols)],
        },
    )
    yield pam


# .....................................................................................
def test_randomize(monkeypatch, observed_pam, generate_temp_filename):
    """Test that the randomize PAM tool works as expected.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        observed_pam (Matrix): A Presence-Absence Matrix for testing.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Get input marginal totals before randomization
    row_totals = observed_pam.sum(axis=0)
    col_totals = observed_pam.sum(axis=1)
    total = observed_pam.sum()

    obs_pam_filename = generate_temp_filename(suffix='.lmm')
    rand_pam_filename = generate_temp_filename(suffix='.lmm')
    # Write test PAM
    observed_pam.save(obs_pam_filename)

    # Run tool
    params = ['randomize_pam.py', obs_pam_filename, rand_pam_filename]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output PAM
    random_pam = Matrix.load(rand_pam_filename)

    assert np.all(random_pam.sum(axis=0) == row_totals)
    assert np.all(random_pam.sum(axis=1) == col_totals)
    assert np.all(random_pam.sum() == total)
    assert not np.all(random_pam != observed_pam)


# .....................................................................................
def test_randomize_multiple(monkeypatch, observed_pam, generate_temp_filename):
    """Test that the randomize PAM tool works as expected with multiple outputs.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        observed_pam (Matrix): A Presence-Absence Matrix for testing.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Get input marginal totals before randomization
    row_totals = observed_pam.sum(axis=0)
    col_totals = observed_pam.sum(axis=1)
    total = observed_pam.sum()

    obs_pam_filename = generate_temp_filename(suffix='.lmm')
    rand_pam_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(2, 10))
    ]
    # Write test PAM
    observed_pam.save(obs_pam_filename)

    # Run tool
    params = ['randomize_pam.py', obs_pam_filename]
    params.extend(rand_pam_filenames)
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output PAMs
    for rand_pam_filename in rand_pam_filenames:
        random_pam = Matrix.load(rand_pam_filename)

        assert np.all(random_pam.sum(axis=0) == row_totals)
        assert np.all(random_pam.sum(axis=1) == col_totals)
        assert np.all(random_pam.sum() == total)
        assert not np.all(random_pam != observed_pam)


# .....................................................................................
def test_randomize_config_file(monkeypatch, observed_pam, generate_temp_filename):
    """Test that the randomize PAM tool works as expected with a configuration file.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        observed_pam (Matrix): A Presence-Absence Matrix for testing.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Get input marginal totals before randomization
    row_totals = observed_pam.sum(axis=0)
    col_totals = observed_pam.sum(axis=1)
    total = observed_pam.sum()

    obs_pam_filename = generate_temp_filename(suffix='.lmm')
    rand_pam_filename = generate_temp_filename(suffix='.lmm')
    # Write test PAM
    observed_pam.save(obs_pam_filename)

    # Create configuration file
    config_fn = generate_temp_filename(suffix='.json')
    with open(config_fn, mode='wt') as config_out:
        json.dump(
            {
                'input_pam_filename': obs_pam_filename,
                'output_pam_filename': rand_pam_filename,
            },
            config_out
        )
    # Run tool
    params = ['randomize_pam.py', '--config_file', config_fn]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output PAM
    random_pam = Matrix.load(rand_pam_filename)

    assert np.all(random_pam.sum(axis=0) == row_totals)
    assert np.all(random_pam.sum(axis=1) == col_totals)
    assert np.all(random_pam.sum() == total)
    assert not np.all(random_pam != observed_pam)


# .....................................................................................
def test_randomize_config_file_many(monkeypatch, observed_pam, generate_temp_filename):
    """Test that the randomize PAM tool works as expected with a configuration file.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        observed_pam (Matrix): A Presence-Absence Matrix for testing.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Get input marginal totals before randomization
    row_totals = observed_pam.sum(axis=0)
    col_totals = observed_pam.sum(axis=1)
    total = observed_pam.sum()

    obs_pam_filename = generate_temp_filename(suffix='.lmm')
    rand_pam_filenames = [
        generate_temp_filename(suffix='.lmm') for _ in range(np.random.randint(2, 10))
    ]
    # Write test PAM
    observed_pam.save(obs_pam_filename)

    # Create configuration file
    config_fn = generate_temp_filename(suffix='.json')
    with open(config_fn, mode='wt') as config_out:
        json.dump(
            {
                'input_pam_filename': obs_pam_filename,
                'output_pam_filename': rand_pam_filenames,
            },
            config_out
        )
    # Run tool
    params = ['randomize_pam.py', '--config_file', config_fn]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output PAMs
    for rand_pam_filename in rand_pam_filenames:
        random_pam = Matrix.load(rand_pam_filename)

        assert np.all(random_pam.sum(axis=0) == row_totals)
        assert np.all(random_pam.sum(axis=1) == col_totals)
        assert np.all(random_pam.sum() == total)
        assert not np.all(random_pam != observed_pam)
