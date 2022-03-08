"""Test the Build Shapegrid tool."""
import glob
import os
import tempfile

import pytest

from lmpy.tools.build_shapegrid import cli


# .....................................................................................
@pytest.fixture(scope='module')
def shapegrid_filename():
    """Get a temporary file location to write shapegrid data and clean it up.

    Yields:
        str: A temporary filename that can be used for creating a shapegrid.
    """
    # Get a temporary file path
    base_filename = tempfile.NamedTemporaryFile().name
    # Return a temporary shapefile file path
    yield f'{base_filename}.shp'
    # Clean up any created temp files for the shapefile
    for fn in glob.glob(f'{base_filename}*'):
        os.remove(fn)


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[
        (500, -3000, 180, 90, 1, 4326),
        (20, 20, 10, 10, .25, 4326)
    ]
)
def invalid_shapegrid_parameters(request):
    """Get a list of invalid shapegrid parameter sets.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        tuple: A tuple of shapegrid parameters.
    """
    yield request.param


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[
        (-180, -90, 180, 90, 1, 4326),
        (-10, -10, 10, 10, .25, 4326),
        (166021, 0, 833978, 9329005, 10000, 32617)
    ]
)
def shapegrid_parameters(request):
    """Get a list of valid shapegrid parameter sets.

    Args:
        request (pytest.Fixture): A pytest fixture requesting valid parameters.

    Yields:
        tuple: A tuple of shapegrid parameters.
    """
    yield request.param


# .....................................................................................
def test_valid(monkeypatch, shapegrid_filename, shapegrid_parameters):
    """Test with valid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        shapegrid_filename (pytest.Fixture): A temporary filename to use for test.
        shapegrid_parameters (pytest.Fixture): A set of shapegrid parameters.
    """
    params = ['build_shapegrid.py', shapegrid_filename]
    params.extend([str(i) for i in shapegrid_parameters])
    monkeypatch.setattr('sys.argv', params)
    cli()


# .....................................................................................
def test_invalid(monkeypatch, shapegrid_filename, invalid_shapegrid_parameters):
    """Test with invalid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        shapegrid_filename (pytest.Fixture): A temporary filename to use for test.
        invalid_shapegrid_parameters (pytest.Fixture): A set of shapegrid parameters.
    """
    params = ['build_shapegrid.py', shapegrid_filename]
    params.extend([str(i) for i in invalid_shapegrid_parameters])
    monkeypatch.setattr('sys.argv', params)
    with pytest.raises(ValueError):
        cli()
