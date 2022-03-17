"""Tests for layer encoding."""
import numpy as np

from lmpy import Matrix
from lmpy.data_preparation.layer_encoder import DEFAULT_NODATA
from lmpy.tools.encode_layers import cli


# .....................................................................................
def test_encode_biogeographic_hypotheses(
    monkeypatch,
    generate_temp_filename,
    shapegrid_filename,
    bio_geo_filenames
):
    """Test encode biogeographic hypotheses through tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
        shapegrid_filename (str): File path to shapegrid.
        bio_geo_filenames (list of str): List of file paths to biogeographic
            hypothesis layer files.
    """
    # Output filename
    matrix_filename = generate_temp_filename(suffix='.lmm')

    # Set params
    params = [
        'encode_layers.py',
        '-m',
        'biogeo',
        '--min_coverage',
        '10',
        shapegrid_filename,
        matrix_filename,
    ]
    # Add layers
    for i, filename in enumerate(bio_geo_filenames):
        params.extend(['--layer', filename, f'Hypothesis {i}'])
        # Add event field if present in filename
        if filename.find('_event_') > 0:
            params.append(filename.split('_event_')[1].split('.shp')[0])

    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check output
    enc_mtx = Matrix.load(matrix_filename)
    col_headers = enc_mtx.get_column_headers()
    for i in range(len(bio_geo_filenames)):
        assert f'Hypothesis {i}' in col_headers
    assert enc_mtx.shape[1] == len(bio_geo_filenames)
    assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
    tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
    assert tmp.min() >= -1
    assert tmp.max() <= 1


# .....................................................................................
def test_encode_presence_absence(
    monkeypatch,
    generate_temp_filename,
    shapegrid_filename,
    raster_pa_filenames,
    vector_pa_filenames
):
    """Test encode presence absence through tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
        shapegrid_filename (str): File path to shapegrid.
        raster_pa_filenames (list of str): List of file paths to raster files.
        vector_pa_filenames (list of str): List of file paths to vector files.
    """
    # Output filename
    matrix_filename = generate_temp_filename(suffix='.lmm')

    # Set params
    params = [
        'encode_layers.py',
        '-m',
        'presence_absence',
        '--min_coverage',
        '25',
        '--min_presence',
        '1',
        '--max_presence',
        '99',
        shapegrid_filename,
        matrix_filename,
    ]
    # Add layers
    for i, filename in enumerate(raster_pa_filenames):
        params.extend(['--layer', filename, f'Raster {i}'])
    for i, filename in enumerate(vector_pa_filenames):
        params.extend(['--layer', filename, f'Vector {i}', 'value'])

    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check output
    enc_mtx = Matrix.load(matrix_filename)
    col_headers = enc_mtx.get_column_headers()
    for i in range(len(raster_pa_filenames)):
        assert f'Raster {i}' in col_headers
    for i in range(len(vector_pa_filenames)):
        assert f'Vector {i}' in col_headers

    assert enc_mtx.shape[1] == len(raster_pa_filenames) + len(vector_pa_filenames)
    assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
    tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
    assert tmp.min() >= -1
    assert tmp.max() <= 1


# .....................................................................................
def test_encode_largest_class(
    monkeypatch,
    generate_temp_filename,
    shapegrid_filename,
    raster_env_filenames,
    vector_env_filenames
):
    """Test encode largest class through tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
        shapegrid_filename (str): File path to shapegrid.
        raster_env_filenames (list of str): List of file paths to raster files.
        vector_env_filenames (list of str): List of file paths to vector files.
    """
    # Output filename
    matrix_filename = generate_temp_filename(suffix='.lmm')

    # Set params
    params = [
        'encode_layers.py',
        '-m',
        'largest_class',
        '--min_coverage',
        '10',
        shapegrid_filename,
        matrix_filename,
    ]
    # Add layers
    for i, filename in enumerate(raster_env_filenames):
        params.extend(['--layer', filename, f'Raster {i}'])
    for i, filename in enumerate(vector_env_filenames):
        params.extend(['--layer', filename, f'Vector {i}', 'value'])

    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check output
    enc_mtx = Matrix.load(matrix_filename)
    col_headers = enc_mtx.get_column_headers()
    for i in range(len(raster_env_filenames)):
        assert f'Raster {i}' in col_headers
    for i in range(len(vector_env_filenames)):
        assert f'Vector {i}' in col_headers

    assert enc_mtx.shape[1] == len(raster_env_filenames) + len(vector_env_filenames)
    assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
    tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
    assert tmp.min() >= -1


# .....................................................................................
def test_encode_mean_value(
    monkeypatch,
    generate_temp_filename,
    shapegrid_filename,
    raster_env_filenames,
    vector_env_filenames
):
    """Test encode mean value through tool.

    Args:
        monkeypatch (pytest.fixture): A fixture for monkeypatching code.
        generate_temp_filename (pytest.fixture): A fixture for making temp filenames.
        shapegrid_filename (str): File path to shapegrid.
        raster_env_filenames (list of str): List of file paths to raster files.
        vector_env_filenames (list of str): List of file paths to vector files.
    """
    # Output filename
    matrix_filename = generate_temp_filename(suffix='.lmm')

    # Set params
    params = [
        'encode_layers.py',
        '-m',
        'mean_value',
        shapegrid_filename,
        matrix_filename,
    ]
    # Add layers
    for i, filename in enumerate(raster_env_filenames):
        params.extend(['--layer', filename, f'Raster {i}'])
    for i, filename in enumerate(vector_env_filenames):
        params.extend(['--layer', filename, f'Vector {i}', 'value'])

    monkeypatch.setattr('sys.argv', params)

    # Call script
    cli()

    # Check output
    enc_mtx = Matrix.load(matrix_filename)
    col_headers = enc_mtx.get_column_headers()
    for i in range(len(raster_env_filenames)):
        assert f'Raster {i}' in col_headers
    for i in range(len(vector_env_filenames)):
        assert f'Vector {i}' in col_headers

    assert enc_mtx.shape[1] == len(raster_env_filenames) + len(vector_env_filenames)
    assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
    tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
    assert tmp.min() >= -1
