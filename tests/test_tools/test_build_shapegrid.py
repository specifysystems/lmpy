"""Test the Build Shapegrid tool."""
import pytest

from lmpy.tools.build_shapegrid import cli


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[(500, -3000, 180, 90, 1, 4326), (20, 20, 10, 10, 0.25, 4326)],
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
        (-10, -10, 10, 10, 0.25, 4326),
        (166021, 0, 833978, 9329005, 10000, 32617),
    ],
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
def test_valid(monkeypatch, generate_temp_filename, shapegrid_parameters):
    """Test with valid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): A fixture for generating temporary
            filenames.
        shapegrid_parameters (pytest.Fixture): A set of shapegrid parameters.
    """
    params = ['build_shapegrid.py', generate_temp_filename(suffix='.shp')]
    params.extend([str(i) for i in shapegrid_parameters])
    monkeypatch.setattr('sys.argv', params)
    cli()


# .....................................................................................
def test_invalid(monkeypatch, generate_temp_filename, invalid_shapegrid_parameters):
    """Test with invalid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): A fixture for generating temporary
            filenames.
        invalid_shapegrid_parameters (pytest.Fixture): A set of shapegrid parameters.
    """
    params = ['build_shapegrid.py', generate_temp_filename(suffix='.shp')]
    params.extend([str(i) for i in invalid_shapegrid_parameters])
    monkeypatch.setattr('sys.argv', params)
    with pytest.raises(ValueError):
        cli()
