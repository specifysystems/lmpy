"""Test the create rare species model tool."""
import os
import tempfile

import numpy as np
import pytest

from lmpy.point import Point, PointCsvWriter
from lmpy.tools.create_rare_species_model import cli, write_tiff


# .....................................................................................
@pytest.fixture(scope='function')
def filenames_for_test():
    """Get a tuple of filenames to use for testing.

    Yields:
        tuple: A tuple of testing filenames
    """
    base_fn = tempfile.NamedTemporaryFile().name
    fns = (f'{base_fn}.csv', f'{base_fn}_ecoregions.tif', f'{base_fn}_model.tif')
    yield fns
    for fn in fns:
        if os.path.exists(fn):
            os.remove(fn)


# .....................................................................................
@pytest.fixture(scope='function', params=[(10, .5, (-180.0, -90.0, 180.0, 90.0))])
def model_parameters(request):
    """Get parameters for testing rare species model.

    Args:
        request (pytest.Fixture): Pytest request fixture.

    Yields:
        tuple: Point count, resolution, and bounding box
    """
    yield request.param


# .....................................................................................
def generate_test_points(point_filename, count, min_x, min_y, max_x, max_y):
    """Generate test points for a rare species model.

    Args:
        point_filename (str): A file location to write the points to.
        count (int): The number of points to generate.
        min_x (float): The minimum x value possible for the point range.
        min_y (float): The minimum y value possible for the point range.
        max_x (float): The maximum x value possible for the point range.
        max_y (float): The maximum y value possible for the point range.
    """
    with PointCsvWriter(point_filename, ['species_name', 'x', 'y']) as writer:
        writer.write_points(
            [
                Point(
                    'Some species',
                    np.round((max_x - min_x) * np.random.random() + min_x, 4),
                    np.round((max_y - min_y) * np.random.random() + min_y, 4)
                ) for _ in range(count)
            ]
        )


# .....................................................................................
def generate_test_ecoregions(ecoreg_filename, min_x, min_y, max_x, max_y, resolution):
    """Generate test points for a rare species model.

    Args:
        ecoreg_filename (str): The file location to write the test ecoregions.
        min_x (float): The ecoregion bounding box minimum x value.
        min_y (float): The ecoregion bounding box minimum y value.
        max_x (float): The ecoregion bounding box minimum x value.
        max_y (float): The ecoregion bounding box minimum y value.
        resolution (float): The size of each raster cell in map units.
    """
    # Queen dispersion
    disperse_options = np.array(
        [
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [1, -1],
            [1, 0],
            [1, 1]
        ]
    )
    n_cols = int((max_x - min_x) / resolution)
    n_rows = int((max_y - min_y) / resolution)
    ecoregions = np.ones((n_rows, n_cols), dtype=int)
    # Generate a random number of ecoregions
    for i in range(2, max(4, n_cols // 2)):
        # Generate starting position
        pos = np.array([np.random.randint(n_rows), np.random.randint(n_cols)])
        ecoregions[pos[0], pos[1]] = i
        # Dye-dispersion spreading
        for _ in range(n_rows):
            pos = pos + disperse_options[np.random.randint(disperse_options.shape[0])]
            pos[0] = min(max(0, pos[0]), n_rows - 1)
            pos[1] = min(max(0, pos[1]), n_cols - 1)
            ecoregions[pos[0], pos[1]] = i
    write_tiff(ecoreg_filename, ecoregions, resolution, min_x, max_y, 4326, -9999)


# .....................................................................................
def test_valid(monkeypatch, filenames_for_test, model_parameters):
    """Test with valid parameters.

    Args:
        monkeypatch (pytest.Fixture): Fixture for monkeypatching command arguments.
        filenames_for_test (pytest.Fixture): Temporary filenames to use for test.
        model_parameters (tuple): Parameters for creating a test model.
    """
    # Model parameters
    count, resolution, (min_x, min_y, max_x, max_y) = model_parameters
    # Get filenames
    csv_fn, ecoreg_fn, model_fn = filenames_for_test
    # Write points
    generate_test_points(csv_fn, count, min_x, min_y, max_x, max_y)
    # Write ecoregions file
    generate_test_ecoregions(ecoreg_fn, min_x, min_y, max_x, max_y, resolution)

    params = ['create_rare_species_model.py', csv_fn, ecoreg_fn, model_fn]
    monkeypatch.setattr('sys.argv', params)
    cli()
    # Check the created model
