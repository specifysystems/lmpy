"""Test the Build Grid tool."""
import json
import pytest

from lmpy.tools.build_grid import cli


# .....................................................................................
@pytest.fixture(
    scope='function',
    params=[(500, -3000, 180, 90, 1, 4326), (20, 20, 10, 10, 0.25, 4326)],
)
def invalid_grid_parameters(request):
    """Get a list of invalid grid parameter sets.

    Args:
        request (pytest.Fixture): A pytest fixture requesting invalid parameters.

    Yields:
        tuple: A tuple of grid parameters.
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
def grid_parameters(request):
    """Get a list of valid grid parameter sets.

    Args:
        request (pytest.Fixture): A pytest fixture requesting valid parameters.

    Yields:
        tuple: A tuple of grid parameters.
    """
    yield request.param


# .....................................................................................
def test_valid(monkeypatch, generate_temp_filename, grid_parameters):
    """Test with valid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): A fixture for generating temporary
            filenames.
        grid_parameters (pytest.Fixture): A set of grid parameters.
    """
    params = ['build_grid.py', generate_temp_filename(suffix='.shp')]
    params.extend([str(i) for i in grid_parameters])
    monkeypatch.setattr('sys.argv', params)
    cli()


# .....................................................................................
def test_valid_config_file(monkeypatch, generate_temp_filename, grid_parameters):
    """Test with valid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): A fixture for generating temporary
            filenames.
        grid_parameters (pytest.Fixture): A set of grid parameters.
    """
    params = ['build_grid.py']
    config = {
        'grid_filename': generate_temp_filename(suffix='.shp'),
        'min_x': grid_parameters[0],
        'min_y': grid_parameters[1],
        'max_x': grid_parameters[2],
        'max_y': grid_parameters[3],
        'cell_size': grid_parameters[4],
        'epsg': grid_parameters[5]
    }
    config_fn = generate_temp_filename(suffix='.json')
    with open(config_fn, mode='wt') as json_out:
        json.dump(config, json_out)
    params.extend(['--config_file', config_fn])
    monkeypatch.setattr('sys.argv', params)
    cli()


# .....................................................................................
def test_invalid(monkeypatch, generate_temp_filename, invalid_grid_parameters):
    """Test with invalid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        generate_temp_filename (pytest.Fixture): A fixture for generating temporary
            filenames.
        invalid_grid_parameters (pytest.Fixture): A set of grid parameters.
    """
    params = ['build_grid.py', generate_temp_filename(suffix='.shp')]
    params.extend([str(i) for i in invalid_grid_parameters])
    monkeypatch.setattr('sys.argv', params)
    with pytest.raises(ValueError):
        cli()
