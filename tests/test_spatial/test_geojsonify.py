import json

import numpy as np
from osgeo import ogr

from lmpy.data_preparation.layer_encoder import LayerEncoder
from lmpy.matrix import Matrix
from lmpy.spatial.geojsonify import (
    geojsonify_matrix,
    geojsonify_matrix_with_shapefile,
)


# .....................................................................................
def _validate_geojson(geojson, generate_temp_filename):
    """Validate a geojson dictionary.

    Args:
        geojson (dict): A geojson dictionary to validate.
        generate_temp_filename (pytest.Fixture): A fixture to get temp filenames.

    Returns:
        bool: A boolean value indicating if the provided geojson is valid.
    """
    checks = []
    fn = generate_temp_filename(suffix='.geojson')
    with open(fn, mode='wt') as out_json:
        json.dump(geojson, out_json)
    ds = ogr.Open(fn)
    lyr = ds.GetLayer()
    feat = lyr.GetNextFeature()
    while feat is not None:
        json_feat = json.loads(feat.ExportToJson())
        checks.append('properties' in json_feat.keys())
        feat_geom = feat.GetGeometryRef()
        checks.append(feat_geom.IsValid())
        feat = lyr.GetNextFeature()

    ds = lyr = None
    return all(checks)


# .....................................................................................
def test_make_geojson_from_matrix(generate_temp_filename):
    """Test getting geojson from a matrix.

    Args:
        generate_temp_filename (pytest.Fixture): Fixture for generating filenames.
    """
    num_rows = np.random.randint(3, 20)
    num_cols = np.random.randint(3, 20)
    matrix = Matrix(
        np.random.randint(0, 2, (num_rows, num_cols)),
        headers={
            '0': [[i, np.random.randint(-179, 179), np.random.randint(-89, 89)] for i in range(num_rows)],
            '1': ['Species A', 'Species B', 'Species C']
        }
    )
    # Check with point geojson
    assert _validate_geojson(geojsonify_matrix(matrix, omit_values=[0]), generate_temp_filename)

    # Check with polygon geojson
    assert _validate_geojson(
        geojsonify_matrix(matrix, resolution=0.5, omit_values=[0]), generate_temp_filename
    )


# .....................................................................................
def test_make_geojson_from_matrix_and_shapefile(
    shapegrid_filename,
    raster_pa_filenames,
    vector_pa_filenames,
    generate_temp_filename,
):
    """Test getting geojson from a matrix and matching shapefile.

    Args:
        shapegrid_filename (str): File path to shapegrid.
        raster_pa_filenames (list of str): List of file paths to raster files.
        vector_pa_filenames (list of str): List of file paths to vector files.
        generate_temp_filename (pytest.Fixture): Fixture for generating filenames.
    """
    encoder = LayerEncoder(shapegrid_filename)

    for i, filename in enumerate(raster_pa_filenames):
        encoder.encode_presence_absence(filename, 'Raster {}'.format(i), 1, 99, 25)
    for i, filename in enumerate(vector_pa_filenames):
        encoder.encode_presence_absence(
            filename, 'Vector {}'.format(i), 1, 99, 25, attribute_name='value'
        )
    enc_mtx = encoder.get_encoded_matrix()
    # Validate GeoJSON
    assert _validate_geojson(
        geojsonify_matrix_with_shapefile(enc_mtx, shapegrid_filename, omit_values=[0]),
        generate_temp_filename,
    )
