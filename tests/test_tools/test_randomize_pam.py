"""Test the Randomize PAM tool."""
import os
import tempfile

import numpy as np
import pytest

from lmpy import Matrix
from lmpy.tools.randomize_pam import cli


# .....................................................................................
@pytest.fixture(
    scope='function', params=[(.3, 100, 100), (.25, 1000, 1000), (.15, 10000, 10000)]
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
        np.random.choice([1, 0], (num_rows, num_cols), p=[fill, 1-fill]),
        headers={
            '0': [f'Row {j}' for j in range(num_rows)],
            '1': [f'Col {i}' for i in range(num_cols)]
        }
    )
    yield pam


# .....................................................................................
@pytest.fixture(scope='function')
def pam_filenames():
    """Generate temporary file locations for observed and random PAMs.

    Yields:
        tuple of (str, str): Input and output PAM filenames.
    """
    base_fn = tempfile.NamedTemporaryFile().name
    fns = (f'{base_fn}_obs_pam.lmm', f'{base_fn}_random_pam.lmm')
    yield fns
    for fn in fns:
        if os.path.exists(fn):
            os.remove(fn)


# .....................................................................................
def test_randomize(monkeypatch, observed_pam, pam_filenames):
    """Test that the randomize PAM tool works as expected.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        observed_pam (Matrix): A Presence-Absence Matrix for testing.
        pam_filenames (tuple of strings): A tuple of input and output filenames.
    """
    # Get input marginal totals before randomization
    row_totals = observed_pam.sum(axis=0)
    col_totals = observed_pam.sum(axis=1)
    total = observed_pam.sum()

    # Write test PAM
    observed_pam.save(pam_filenames[0])

    # Run tool
    params = ['randomize_pam.py', *pam_filenames]
    monkeypatch.setattr('sys.argv', params)
    cli()

    # Check output PAM
    random_pam = Matrix.load(pam_filenames[1])

    assert np.all(random_pam.sum(axis=0) == row_totals)
    assert np.all(random_pam.sum(axis=1) == col_totals)
    assert np.all(random_pam.sum() == total)
    assert not np.all(random_pam != observed_pam)
