"""Tests the occurrence data filters
"""
import pytest

from lmpy import Point
from lmpy.data_preparation.layer_encoder import LayerEncoder


# .............................................................................
class Test_LayerEncoder:
    """Test LayerEncoder."""
    # ................................
    def test_base_constructor(self, shapegrid_filename):
        """Test construction."""
        encoder = LayerEncoder(shapegrid_filename)
        assert encoder.get_encoded_matrix() is None

    # ................................
    def test_encode_biogeographic_hypothesis(self, shapegrid_filename,
                                             bio_geo_filenames):
        """Test encode biogeographic hypothesis."""
        encoder = LayerEncoder(shapegrid_filename)
        for i, filename in enumerate(bio_geo_filenames):
            encoder.encode_biogeographic_hypothesis(
                filename, 'Hypothesis {}'.format(i), 10)
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(bio_geo_filenames)):
            assert col_headers[i] == 'Hypothesis {}'.format(i)
        assert enc_mtx.shape[1] == len(bio_geo_filenames)
        assert enc_mtx.min() >= NODATA_VALUE
        tmp = enc_mtx[enc_mtx > NODATA_VALUE]
        assert tmp.min() >= -1
        assert tmp.max() <= 1
        assert json.loads(json.dumps(enc_mtx.get_geojson()))

    # ................................
    def test_encode_presence_absence(self, shapegrid_filename,
                                     raster_pa_filenames, vector_pa_filenames):
        """Test encode presence absence."""
        encoder = LayerEncoder(shapegrid_filename)

        for i, filename in enumerate(raster_pa_filenames):
            encoder.encode_presence_absence(
                filename, 'Raster {}'.format(i), 1, 99, 25)
        for i, filename in enumerate(vector_pa_filenames):
            encoder.encode_presence_absence(
                filename, 'Vector {}'.format(i), 1, 99, 25,
                attribute_name='value')
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_pa_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_pa_filenames)):
            assert col_headers[
                i + len(raster_pa_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(
            raster_pa_filenames) + len(vector_pa_filenames)
        assert enc_mtx.min() >= NODATA_VALUE
        tmp = enc_mtx[enc_mtx > NODATA_VALUE]
        assert tmp.min() >= 0
        assert tmp.max() <= 1
        assert json.loads(json.dumps(enc_mtx.get_geojson()))

    # ................................
    def test_encode_mean_value(self, shapegrid_filename, raster_env_filenames,
                               vector_env_filenames):
        """Test encode mean value."""
        encoder = LayerEncoder(shapegrid_filename)

        for i, filename in enumerate(raster_env_filenames):
            encoder.encode_mean_value(
                filename, 'Raster {}'.format(i), 1, 99, 25)
        for i, filename in enumerate(vector_env_filenames):
            encoder.encode_mean_value(
                filename, 'Vector {}'.format(i), 1, 99, 25,
                attribute_name='value')
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_env_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_env_filenames)):
            assert col_headers[
                i + len(raster_env_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(
            raster_env_filenames) + len(vector_env_filenames)
        assert enc_mtx.min() >= NODATA_VALUE
        tmp = enc_mtx[enc_mtx > NODATA_VALUE]
        assert json.loads(json.dumps(enc_mtx.get_geojson()))

    # ................................
    def test_encode_largest_class(self, shapegrid_filename,
                                  raster_env_filenames, vector_env_filenames):
        """Test encode largest class."""
        encoder = LayerEncoder(shapegrid_filename)

        for i, filename in enumerate(raster_env_filenames):
            encoder.encode_largest_class(
                filename, 'Raster {}'.format(i), 1, 99, 25)
        for i, filename in enumerate(vector_env_filenames):
            encoder.encode_largest_class(
                filename, 'Vector {}'.format(i), 1, 99, 25,
                attribute_name='value')
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_env_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_env_filenames)):
            assert col_headers[
                i + len(raster_env_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(
            raster_env_filenames) + len(vector_env_filenames)
        assert enc_mtx.min() >= NODATA_VALUE
        tmp = enc_mtx[enc_mtx > NODATA_VALUE]
        assert json.loads(json.dumps(enc_mtx.get_geojson()))
