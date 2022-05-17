"""Tests for layer encoding."""
import json

import numpy as np
from osgeo import ogr, osr

from lmpy.data_preparation.build_grid import build_grid
from lmpy.data_preparation.layer_encoder import LayerEncoder, DEFAULT_NODATA


# .....................................................................................
class Test_LayerEncoder:
    """Test LayerEncoder."""

    # ................................
    def test_base_constructor(self, grid_filename):
        """Test construction.

        Args:
            grid_filename (str): File path to grid.
        """
        encoder = LayerEncoder(grid_filename)
        assert encoder.get_encoded_matrix() is None

    # ................................
    def test_encode_biogeographic_hypothesis(
        self, grid_filename, bio_geo_filenames
    ):
        """Test encode biogeographic hypothesis.

        Args:
            grid_filename (str): File path to grid.
            bio_geo_filenames (list of str): List of file paths to biogeographic
                hypothesis layer files.
        """
        encoder = LayerEncoder(grid_filename)
        for i, filename in enumerate(bio_geo_filenames):
            if filename.find('_attribute_') > 0:
                attribute_field = filename.split('_attribute_')[1].split('.shp')[0]
            else:
                attribute_field = None
            encoder.encode_biogeographic_hypothesis(
                filename, 'Hypothesis {}'.format(i), 10, attribute_field=attribute_field
            )
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(bio_geo_filenames)):
            assert col_headers[i] == 'Hypothesis {}'.format(i)
        assert enc_mtx.shape[1] == len(bio_geo_filenames)
        assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
        tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
        assert tmp.min() >= -1
        assert tmp.max() <= 1
        assert json.loads(json.dumps(encoder.get_geojson()))

    # ................................
    def test_encode_presence_absence(
        self, grid_filename, raster_pa_filenames, vector_pa_filenames
    ):
        """Test encode presence absence.

        Args:
            grid_filename (str): File path to grid.
            raster_pa_filenames (list of str): List of file paths to raster files.
            vector_pa_filenames (list of str): List of file paths to vector files.
        """
        encoder = LayerEncoder(grid_filename)

        for i, filename in enumerate(raster_pa_filenames):
            encoder.encode_presence_absence(filename, 'Raster {}'.format(i), 1, 99, 25)
        for i, filename in enumerate(vector_pa_filenames):
            encoder.encode_presence_absence(
                filename, 'Vector {}'.format(i), 1, 99, 25, attribute_name='value'
            )
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_pa_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_pa_filenames)):
            assert col_headers[i + len(raster_pa_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(raster_pa_filenames) + len(vector_pa_filenames)
        assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
        tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
        assert tmp.min() >= 0
        assert tmp.max() <= 1
        assert json.loads(json.dumps(encoder.get_geojson()))

    # ................................
    def test_encode_mean_value(
        self, grid_filename, raster_env_filenames, vector_env_filenames
    ):
        """Test encode mean value.

        Args:
            grid_filename (str): File path to grid.
            raster_env_filenames (list of str): List of file paths to raster files.
            vector_env_filenames (list of str): List of file paths to vector files.
        """
        encoder = LayerEncoder(grid_filename)

        for i, filename in enumerate(raster_env_filenames):
            encoder.encode_mean_value(filename, 'Raster {}'.format(i))
        for i, filename in enumerate(vector_env_filenames):
            encoder.encode_mean_value(
                filename, 'Vector {}'.format(i), attribute_name='value'
            )
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_env_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_env_filenames)):
            assert col_headers[i + len(raster_env_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(raster_env_filenames) + len(vector_env_filenames)
        assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
        tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
        # Test that nodata values aren't being mixed in windows
        assert tmp.min() >= -100
        assert json.loads(json.dumps(encoder.get_geojson()))

    # ................................
    def test_encode_largest_class(
        self, grid_filename, raster_env_filenames, vector_env_filenames
    ):
        """Test encode largest class.

        Args:
            grid_filename (str): File path to grid.
            raster_env_filenames (list of str): List of file paths to raster files.
            vector_env_filenames (list of str): List of file paths to vector files.
        """
        encoder = LayerEncoder(grid_filename)

        for i, filename in enumerate(raster_env_filenames):
            encoder.encode_largest_class(filename, 'Raster {}'.format(i), 10)
        for i, filename in enumerate(vector_env_filenames):
            encoder.encode_largest_class(
                filename, 'Vector {}'.format(i), 10, attribute_name='value'
            )
        enc_mtx = encoder.get_encoded_matrix()
        col_headers = enc_mtx.get_column_headers()
        for i in range(len(raster_env_filenames)):
            assert col_headers[i] == 'Raster {}'.format(i)
        for i in range(len(vector_env_filenames)):
            assert col_headers[i + len(raster_env_filenames)] == 'Vector {}'.format(i)
        assert enc_mtx.shape[1] == len(raster_env_filenames) + len(vector_env_filenames)
        assert np.nanmin(enc_mtx) >= DEFAULT_NODATA
        tmp = enc_mtx[enc_mtx > DEFAULT_NODATA]
        # Test that nodata values aren't being mixed in windows
        assert tmp.min() >= -100
        assert json.loads(json.dumps(encoder.get_geojson()))

    # ................................
    def test_min_coverage_encode_presence_absence(self, generate_temp_filename):
        """Test encode presence absence minimum coverage parameter.

        Args:
            generate_temp_filename (pytest.fixture): A fixture for generating filenames.
        """
        # Create grid (10 x 10 1 degree cells)
        temp_grid_filename = generate_temp_filename(suffix='.shp')
        layer_filename = generate_temp_filename(suffix='.asc')

        build_grid(temp_grid_filename, 0, 0, 10, 10, 1, 4326, 4)

        encoder = LayerEncoder(temp_grid_filename)

        # Create layer
        with open(layer_filename, mode='wt') as layer_out:
            layer_out.write('ncols    40\n')
            layer_out.write('nrows    40\n')
            layer_out.write('xllcorner    0\n')
            layer_out.write('yllcorner    0\n')
            layer_out.write('cellsize    0.25\n')
            for i in range(40):
                vals = ['0'] * 40
                j = i
                while j < 40:
                    vals[j] = '5'
                    j += 1
                layer_out.write('{}\n'.format(' '.join(vals)))

        # Encode layer with multiple coverages
        encoder.encode_presence_absence(layer_filename, 'Layer 1 percent', 1, 100, 1)
        encoder.encode_presence_absence(layer_filename, 'Layer 2 percent', 1, 100, 2)
        encoder.encode_presence_absence(layer_filename, 'Layer 10 percent', 1, 100, 10)
        encoder.encode_presence_absence(layer_filename, 'Layer 40 percent', 1, 100, 40)
        encoder.encode_presence_absence(layer_filename, 'Layer 70 percent', 1, 100, 70)
        encoder.encode_presence_absence(layer_filename, 'Layer 90 percent', 1, 100, 90)
        encoder.encode_presence_absence(
            layer_filename, 'Layer 100 percent', 1, 100, 100
        )

        enc_matrix = encoder.get_encoded_matrix()

        # Check encoding
        assert np.all(enc_matrix.sum(axis=0) == np.array([55, 55, 55, 55, 45, 45, 45]))

    # ................................
    def test_bigger_grid(self, generate_temp_filename):
        """Test encode methods with a larger grid than layers.

        Args:
            generate_temp_filename (pytest.fixture): A fixture for generating filenames.
        """
        # File names
        temp_grid_filename = generate_temp_filename(suffix='.shp')
        layer_filename = generate_temp_filename(suffix='.asc')
        biogeo_filename = generate_temp_filename(suffix='.bg.shp')

        # Create a grid (50 x 50 1 degree cells)
        build_grid(temp_grid_filename, 0, 0, 50, 50, 1, 4326, 4)

        encoder = LayerEncoder(temp_grid_filename)

        # Create layer
        with open(layer_filename, mode='wt') as layer_out:
            layer_out.write('ncols    40\n')
            layer_out.write('nrows    40\n')
            layer_out.write('xllcorner    10\n')
            layer_out.write('yllcorner    10\n')
            layer_out.write('cellsize    0.25\n')
            layer_out.write('NODATA_VALUE    0\n')
            for _ in range(40):
                vals = []
                for _ in range(40):
                    vals.append(str(np.random.randint(0, 10)))
                layer_out.write('{}\n'.format(' '.join(vals)))

        # Create hypothesis layer
        target_srs = osr.SpatialReference()
        target_srs.ImportFromEPSG(4326)
        drv = ogr.GetDriverByName('ESRI Shapefile')
        data_set = drv.CreateDataSource(biogeo_filename)
        layer = data_set.CreateLayer(
            data_set.GetName(), geom_type=ogr.wkbPolygon, srs=target_srs
        )
        hyp_wkt = 'POLYGON ((15 11, 19 19, 15 11, 11 11, 15 11))'
        geom = ogr.CreateGeometryFromWkt(hyp_wkt)
        feat = ogr.Feature(feature_def=layer.GetLayerDefn())
        feat.SetGeometry(geom)
        layer.CreateFeature(feat)
        feat.Destroy()
        data_set.Destroy()

        # Encode layer with multiple coverages
        encoder.encode_presence_absence(layer_filename, 'PA Layer', 5, 10, 25)
        encoder.encode_mean_value(layer_filename, 'Mean Layer')
        encoder.encode_largest_class(layer_filename, 'Largest class', 25, nodata=10)
        encoder.encode_biogeographic_hypothesis(biogeo_filename, 'Hypothesis', 10)

        enc_geojson = encoder.get_geojson()

        # Check that encoding is zero outside of layer region
        for feat in enc_geojson['features']:
            xs = []
            ys = []
            for x, y in feat['geometry']['coordinates'][0]:
                xs.append(float(x))
                ys.append(float(y))
            x_val = (min(xs) + max(xs)) / 2.0
            y_val = (min(ys) + max(ys)) / 2.0
            # Assert that coordinate is inside of layer range
            if sum(feat['properties'].values()) > 0:
                assert 10 < x_val < 20 and 10 < y_val < 20
