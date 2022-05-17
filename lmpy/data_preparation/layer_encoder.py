"""This module contains a class for encoding spatial layers into a Matrix.

The 'LayerEncoder' class uses a grid to generate a base matrix structure
and then each layer is encoded as a new column (or columns) for the resulting
encoded matrix.

Todo:
    Consider if we want to support hexagonal cells, if so, we will need to
        mask the resulting data windows and possibly change the minimum
        coverage calculation.

Note:
    Data array is oriented at top left (min x, max y)
"""
import os
from random import shuffle

import numpy as np
from osgeo import gdal, ogr

from lmpy.matrix import Matrix
from lmpy.spatial.geojsonify import geojsonify_matrix_with_shapefile


# Suppress numpy warnings
np.seterr(all='ignore')
# DEFAULT_SCALE is the scale of the layer data array to the grid cell size
#     The number of data array cells in a (square) grid cell is::
#         1.0 / DEFAULT_SCALE^2
DEFAULT_SCALE = 0.1  # Default scale for data array versus grid cells
# DEFAULT_NODATA is the default value to use when no data is present in a
#    raster cell.
DEFAULT_NODATA = -9999


# .............................................................................
# Encoding methods


# .............................................................................
def _get_presence_absence_method(min_presence, max_presence, min_coverage, nodata):
    """Gets the function for determining presence for a data window.

    Args:
        min_presence (numeric): Data cells must have a value greater than or equal to
            this to be considered present.
        max_presence (numeric): Data cells must have a value less than or equal to this
            to be considered present.
        min_coverage (numeric): At least the percentage of the window must be
            classified as present to consider the window present.
        nodata (numeric): This values should be considered nodata.

    Returns:
        Method: A function for getting presence absence of a window.
    """
    if min_coverage >= 1.0:
        min_coverage = min_coverage / 100.0

    # ...............................
    def get_presence_absence(window):
        if window is None:
            return False
        min_num = max(min_coverage * window.size, 1)
        valid_cells = np.logical_and(
            np.logical_and(window >= min_presence, window <= max_presence),
            window != nodata,
        )
        return np.sum(valid_cells) >= min_num

    return get_presence_absence


# .............................................................................
def _get_mean_value_method(nodata):
    """Gets the function to use for determining the mean value of a data window.

    Args:
        nodata (numeric): This value is assumed to be nodata in the array.

    Returns:
        Method: A function for getting the mean value of a window.
    """
    # ...............................
    def get_mean(window):
        if window is None:
            return nodata
        window_mean = np.nanmean(window[np.where(window != nodata)])
        if np.isnan(window_mean):
            return nodata

        return window_mean

    return get_mean


# .............................................................................
def _get_largest_class_method(min_coverage, nodata):
    """Gets the function to use for determining the largest class.

    Args:
        min_coverage (numeric): The minimum percentage of the data window that must be
            covered by the largest class.
        nodata (numeric): This value is assumed to be nodata in the array

    Returns:
        Method: A function for getting the largest class in a window.
    """
    if min_coverage >= 1.0:
        min_coverage = min_coverage / 100.0

    # ...............................
    def get_largest_class(window):
        """Get the largest class for numpy > 1.8.

        Args:
            window (Matrix): A window of layer data.

        Returns:
            ndarray: An array of encoded values.
        """
        if window is None:
            return nodata
        min_num = min_coverage * window.size
        largest_count = 0
        largest_class = nodata
        unique_values = np.column_stack(np.unique(window, return_counts=True))
        for class_, num in unique_values:
            if not np.isclose(class_, nodata) and num > largest_count and num > min_num:
                largest_class = class_
        return largest_class

    return get_largest_class


# .............................................................................
def _get_encode_hypothesis_method(hypothesis_values, min_coverage, nodata):
    """Gets the function to determine the hypothesis value for each data window.

    Args:
        hypothesis_values (list): A list of possible hypothesis values to look for.
            Each item in the list will be treated as its own column.
        min_coverage (numeric): The minimum percentage of each data window that must be
            covered by the returned hypothesis value.
        nodata (numeric): This value is assumed to be nodata

    Returns:
        Method: A function to encode the values in a window.
    """
    # Build the map
    val_map = {}
    i = 0
    for val in hypothesis_values:
        contrast_values = [-1, 1]
        shuffle(contrast_values)
        try:
            # Pair of values
            val_map[val[0]] = {'val': contrast_values[0], 'index': i}
            val_map[val[1]] = {'val': contrast_values[1], 'index': i}
        except IndexError:
            # Single value
            val_map[val] = {'val': contrast_values[0], 'index': i}
        i += 1
        # Note: 'i' is the number of values, we'll use that later

    if min_coverage >= 1.0:
        min_coverage = min_coverage / 100.0

    # ...............................
    def encode_method(window):
        """Encode method for numpy > 1.8.

        Args:
            window (Matrix): A window of layer data.

        Returns:
            ndarray: An array of encoded values.
        """
        if window is None:  # pragma: no cover
            return nodata
        min_vals = int(min_coverage * window.size)
        # Set default min count to min_vals
        # Note: This will cause last one to win if they are equal, change to
        #     '>' below and set this to * (min_vals - 1) to have first one win
        counts = np.zeros((i,), dtype=int) * min_vals
        ret = np.zeros(i)

        unique_values = np.column_stack(np.unique(window, return_counts=True))

        # Check unique values in window
        for u_val, num in unique_values:
            if (
                not np.isclose(u_val, nodata)
                and u_val in list(val_map.keys())
                and num >= counts[val_map[u_val]['index']]
            ):
                counts[val_map[u_val]['index']] = num
                ret[val_map[u_val]['index']] = val_map[u_val]['val']
        return ret

    return encode_method


# .............................................................................
class LayerEncoder:
    """The LayerEncoder class encodes layers into matrix columns.

    Attributes:
        encoded_matrix: A Matrix object with encoded layers.
    """

    # ...............................
    def __init__(self, grid_filename):
        """Constructor for the layer encoder.

        Args:
            grid_filename (str): A file path for the grid.
        """
        # Process sgrid
        self.grid_filename = grid_filename
        self._read_grid(grid_filename)

        self.encoded_matrix = None

    # ...............................
    def _encode_layer(self, window_func, encode_func, column_name, num_columns=1):
        """Encodes the layer using the provided encoding function.

        Args:
            window_func: A function that returns a window of array data for a
                provided x, y pair.
            encode_func: A function that encodes a window of array data.
            column_name: The header name to use for the column in the encoded
                matrix.
            num_columns: The number of columns that will be encoded by
                'encode_func'.  This can be non-zero if we are testing for
                multiple biogeographic hypotheses in a single vector layer for
                example.

        Returns:
            list: A list of column headers for the newly encoded columns.
        """
        grid_dataset = ogr.Open(self.grid_filename)
        grid_layer = grid_dataset.GetLayer()

        encoded_column = np.zeros((self.num_cells, num_columns))
        if num_columns == 1:
            column_headers = [column_name]
        else:  # pragma: no cover
            column_headers = [
                '{}-{}'.format(column_name, val) for val in range(num_columns)
            ]

        row_headers = []

        i = 0

        feat = grid_layer.GetNextFeature()
        while feat is not None:
            geom = feat.GetGeometryRef()
            cent = geom.Centroid()
            x_coord = cent.GetX()
            y_coord = cent.GetY()
            val = encode_func(window_func(x_coord, y_coord))
            encoded_column[i] = val
            row_headers.append((feat.GetFID(), x_coord, y_coord))
            i += 1
            feat = grid_layer.GetNextFeature()

        col = Matrix(encoded_column, headers={'0': row_headers, '1': column_headers})

        if self.encoded_matrix is None:
            self.encoded_matrix = col
        else:
            self.encoded_matrix = Matrix.concatenate([self.encoded_matrix, col], axis=1)
        # Return column headers for added columns
        return column_headers

    # ...............................
    @staticmethod
    def _get_window_function(data, layer_bbox, cell_size, num_cell_sides=4):
        """Gets a windowing function for the data.

        This function generates a function that will return a "window" of array
        data for a given (x, y) pair.

        Args:
            data (np.ndarray): A numpy array with data for a layer
            layer_bbox (tuple): The bounding box of the layer in the map units of the
                layer.
            cell_size (float or tuple): Either a single value or a tuple with two
                values. If it is a single value, it will be used for both x and y cell
                sizes. If a tuple is provided, the first value will be used for the
                size of each cell in the x dimension and the second will be used for
                the size of the cell in the y dimension.
            num_cell_sides (int): The number of sides each grid cell has::
                4 -- square
                6 -- hexagon

        Note:
            The origin (0, 0) of the data array should represent (min x, max y)
                for the layer.

        Raises:
            NotImplementedError: Raised if cell sides does note equal 4.

        Returns:
            Method: A function for processing a window of data.

        Todo:
            CJ - Enable hexagonal windows by masking data.
        """
        if num_cell_sides != 4:  # pragma: no cover
            raise NotImplementedError('Only rectangular cells are currently supported')
        # Compute bounds here to save compute time
        y_size, x_size = data.shape
        min_x, min_y, max_x, max_y = layer_bbox

        # x_res = float(max_x - min_x) / x_size

        y_range = max_y - min_y
        x_range = max_x - min_x

        try:
            # Tuple or list
            x_size_2 = cell_size[0] / 2
            y_size_2 = cell_size[1] / 2
        except TypeError:  # pragma: no cover
            # Single value
            x_size_2 = y_size_2 = cell_size / 2

        # ...............................
        def get_rc(x_coord, y_coord):
            """Get the row and column values for an x and y coordinate pair.

            Args:
                x_coord (numeric): The x coordinate for a position in the layer.
                y_coord (numeric): The y coordinate for a position in the layer.

            Returns:
                tuple of int, int: Row and column values for the specified point.
            """
            x_prop = (1.0 * x_coord - min_x) / x_range
            y_prop = (1.0 * y_coord - min_y) / y_range

            col = int(x_size * x_prop)
            row = y_size - int(y_size * y_prop)
            return row, col

        # ...............................
        def window_function(x_coord, y_coord):
            """Get the array window from the centroid coordinates.

            Args:
                x_coord (numeric): The x coordinate for a position in the layer.
                y_coord (numeric): The y coordinate for a position in the layer.

            Returns:
                numeric: The value of the layer at the specified position.
            """
            # Note: Again, 0 row corresponds to top of map, so bigger y
            #     corresponds to lower row number
            # Upper left corner
            uly, ulx = get_rc(x_coord - x_size_2, y_coord + y_size_2)
            # Lower right corner
            lry, lrx = get_rc(x_coord + x_size_2, y_coord - y_size_2)

            # If entire cell window is outside of layer, return None
            if (
                max([uly, lry]) < 0
                or max([ulx, lrx]) < 0
                or min([uly, lry]) > y_size
                or min([ulx, lrx]) > x_size
            ):
                return None

            return data[max(0, uly):min(y_size, lry), max(0, ulx):min(x_size, lrx)]

        return window_function

    # ...............................
    def _read_layer(
            self,
            layer_filename,
            resolution=None,
            bbox=None,
            nodata=DEFAULT_NODATA,
            attribute_field=None):
        """Reads a layer for processing.

        Args:
            layer_filename (str): The file path for the layer to read.
            resolution (numeric): An optional resolution to use for the input data if
                it is a vector layer.
            bbox (tuple): An optional bounding box in the form
                (min x, min y, max x, max y) to use if the layer is a vector layer.
            nodata (numeric): An optional nodata value to use if the layer is a vector
                layer.
            attribute_field (str): If provided, use this shapefile attribute as the data
                value for a vector layer.

        Returns:
            tuple: A tuple containing a window function for returning a portion of the
                numpy array generated by the layer and the NODATA value to use with
                this layer.
        """
        # Get the file extension for the layer file name
        ext = os.path.splitext(layer_filename)[1]

        if ext == '.shp':
            window_func, nodata_value, attributes = self._read_vector_layer(
                layer_filename,
                resolution=resolution,
                bbox=bbox,
                nodata=nodata,
                attribute_field=attribute_field,
            )
        else:
            window_func, nodata_value = self._read_raster_layer(layer_filename)
            attributes = set()

        return window_func, nodata_value, attributes

    # ...............................
    def _read_raster_layer(self, raster_filename):
        """Reads a raster layer for processing.

        Args:
            raster_filename: The file path for the raster layer.

        Returns:
            tuple: A tuple containing a window function for returning a portion of the
                numpy array generated by the layer and the NODATA value to use with
                this layer.
        """
        dataset = gdal.Open(raster_filename)
        band = dataset.GetRasterBand(1)
        layer_array = band.ReadAsArray().astype(float)
        nodata = band.GetNoDataValue()
        layer_array[np.where(layer_array == nodata)] = np.nan

        num_y, num_x = layer_array.shape
        min_x, x_res, _, max_y, _, y_res = dataset.GetGeoTransform()
        max_x = min_x + (num_x * x_res)
        min_y = max_y + (y_res * num_y)
        layer_bbox = (min_x, min_y, max_x, max_y)
        window_func = self._get_window_function(
            layer_array,
            layer_bbox,
            self.grid_resolution,
            num_cell_sides=self.grid_sides,
        )

        return window_func, nodata

    # ...............................
    def _read_grid(self, grid_filename):
        """Read the grid.

        Args:
            grid_filename: The file location of the grid.
        """
        grid_dataset = ogr.Open(grid_filename)
        self.grid_layer = grid_dataset.GetLayer()
        tmp = self.grid_layer.GetExtent()
        self.grid_bbox = (tmp[0], tmp[2], tmp[1], tmp[3])

        self.num_cells = self.grid_layer.GetFeatureCount()

        feature_0 = self.grid_layer.GetFeature(0)
        geom = feature_0.GetGeometryRef()

        # Get resolution and number of sides
        geom_wkt = geom.ExportToWkt()
        boundary_points = geom_wkt.split(',')
        if len(boundary_points) == 5:
            # Square
            envelope = geom.GetEnvelope()
            self.grid_resolution = (
                envelope[1] - envelope[0],
                envelope[3] - envelope[2],
            )
        else:  # pragma: no cover
            # TODO: Write tests for this when we want full support
            # Hexagon
            center = geom.Centroid()
            x_cent = center.GetX()
            y_cent = center.GetY()
            x_1, y_1 = boundary_points[1].split(' ')
            self.grid_resolution = np.sqrt(
                (x_cent - x_1) ** 2 + (y_cent - y_1) ** 2
            )
        self.grid_sides = len(boundary_points) - 1
        # self.grid_layer.ResetReading()
        self.grid_layer = None

    # ...............................
    def _read_vector_layer(
        self,
        vector_filename,
        resolution=None,
        bbox=None,
        nodata=DEFAULT_NODATA,
        attribute_field=None,
    ):
        """Reads a vector layer for processing.

        Args:
            vector_filename: The vector file path for the layer to read.
            resolution (numeric): An optional resolution to use for the input data if
                it is a vector layer.
            bbox (tuple): An optional bounding box in the form
                (min x, min y, max x, max y) to use if the layer is a vector layer.
            nodata (numeric): An optional nodata value to use if the layer is a vector
                layer.
            attribute_field (str): If provided, use this shapefile attribute as the
                data value for a vector layer.

        Returns:
            tuple: A tuple containing a window function for returning a portion of the
                numpy array generated by the layer, the NODATA value to use with this
                layer, and a set of distinct attributes to be used for processing.
        """
        options = ['ALL_TOUCHED=TRUE']
        if attribute_field is not None:
            options.append('ATTRIBUTE={}'.format(attribute_field))

        if resolution is None:
            resolution = [DEFAULT_SCALE * i for i in self.grid_resolution]
        try:
            # Tuple or list
            x_res = resolution[0]
            y_res = resolution[1]
        except TypeError:  # pragma: no cover
            # Single value
            x_res = y_res = resolution

        if bbox is None:
            bbox = self.grid_bbox

        min_x, min_y, max_x, max_y = bbox
        x_size = int(float(max_x - min_x) / x_res)
        y_size = int(float(max_y - min_y) / y_res)

        vector_ds = ogr.Open(vector_filename)
        vector_layer = vector_ds.GetLayer()

        raster_drv = gdal.GetDriverByName('MEM')
        raster_ds = raster_drv.Create('temp', x_size, y_size, 1, gdal.GDT_Float32)
        raster_ds.SetGeoTransform((min_x, x_res, 0, max_y, 0, -1.0 * y_res))
        band = raster_ds.GetRasterBand(1)
        band.SetNoDataValue(nodata)
        band.FlushCache()
        init_ary = np.empty((y_size, x_size))
        init_ary.fill(nodata)
        band.WriteArray(init_ary)
        gdal.RasterizeLayer(raster_ds, [1], vector_layer, options=options)

        layer_array = raster_ds.ReadAsArray()
        del raster_ds

        layer_bbox = (min_x, min_y, max_x, max_y)
        window_func = self._get_window_function(
            layer_array,
            layer_bbox,
            self.grid_resolution,
            num_cell_sides=self.grid_sides,
        )

        distinct_attributes = list(np.unique(layer_array))
        try:
            # Go through list backwards to safely pop if needed
            for i in range(len(distinct_attributes) - 1, -1, -1):
                if np.isclose(distinct_attributes[i], nodata):
                    distinct_attributes.pop(i)
        except TypeError:  # pragma: no cover
            # This happens if only one value
            if np.isclose(distinct_attributes, nodata):
                distinct_attributes = []
            else:
                distinct_attributes = [distinct_attributes]
        return window_func, nodata, distinct_attributes

    # ...............................
    def encode_biogeographic_hypothesis(
        self,
        layer_filename,
        column_name,
        min_coverage,
        resolution=None,
        bbox=None,
        nodata=DEFAULT_NODATA,
        attribute_field=None,
    ):
        """Encodes a biogeographic hypothesis layer.

        Encodes a biogeographic hypothesis layer by creating a Helmert contrast
        column in the encoded matrix.

        Args:
            layer_filename: The file location of the layer to encode.
            column_name: What to name this column in the encoded matrix.
            min_coverage: The minimum percentage of each data window that must
                be covered.
            resolution: If the layer is a vector, optionally use this as the
                resolution of the data grid.
            bbox: If the layer is a vector, optionally use this bounding box
                for the data grid.
            nodata: If the layer is a vector, optionally use this as the data
                grid nodata value.
            attribute_field: If the layer is a vector and contains multiple
                hypotheses, use this field to separate the vector file.

        Returns:
            list of str: A list of column headers for the newly encoded columns.
        """
        window_func, nodata, distinct_attributes = self._read_layer(
            layer_filename,
            resolution=resolution,
            bbox=bbox,
            nodata=nodata
        )
        if len(distinct_attributes) == 2:
            # Set the attributes to be opposite sides of same hypothesis
            distinct_attributes = [tuple(distinct_attributes)]
        encode_func = _get_encode_hypothesis_method(
            distinct_attributes, min_coverage, nodata
        )
        return self._encode_layer(
            window_func, encode_func, column_name, num_columns=len(distinct_attributes)
        )

    # ...............................
    def encode_presence_absence(
        self,
        layer_filename,
        column_name,
        min_presence,
        max_presence,
        min_coverage,
        resolution=None,
        bbox=None,
        nodata=DEFAULT_NODATA,
        attribute_name=None,
    ):
        """Encodes a distribution layer into a presence absence column.

        Args:
            layer_filename: The file location of the layer to encode.
            column_name: What to name this column in the encoded matrix.
            min_presence: The minimum value that should be treated as presence.
            max_presence: The maximum value to be considered as present.
            min_coverage: The minimum percentage of each data window that must
                be present to consider that cell present.
            resolution: If the layer is a vector, optionally use this as the
                resolution of the data grid.
            bbox: If the layer is a vector, optionally use this bounding box
                for the data grid.
            nodata: If the layer is a vector, optionally use this as the data
                grid nodata value.
            attribute_name: If the layer is a vector, use this field to
                determine presence.

        Returns:
            list of str: A list of column headers for the newly encoded columns.
        """
        window_func, nodata, _ = self._read_layer(layer_filename, resolution=resolution,
                                                  bbox=bbox, nodata=nodata)
        encode_func = _get_presence_absence_method(
            min_presence, max_presence, min_coverage, nodata
        )
        return self._encode_layer(window_func, encode_func, column_name)

    # ...............................
    def encode_mean_value(
        self,
        layer_filename,
        column_name,
        resolution=None,
        bbox=None,
        nodata=DEFAULT_NODATA,
        attribute_name=None,
    ):
        """Encodes a layer based on the mean value for each data window.

        Args:
            layer_filename: The file location of the layer to encode.
            column_name: What to name this column in the encoded matrix.
            resolution: If the layer is a vector, optionally use this as the
                resolution of the data grid.
            bbox: If the layer is a vector, optionally use this bounding box
                for the data grid.
            nodata: If the layer is a vector, optionally use this as the data
                grid nodata value.
            attribute_name: If the layer is a vector, use this field to
                determine value.

        Returns:
            list of str: A list of column headers for the newly encoded columns
        """
        print((layer_filename, nodata, bbox, resolution, attribute_name))
        window_func, nodata, _ = self._read_layer(
            layer_filename,
            resolution=resolution,
            bbox=bbox,
            nodata=nodata
        )
        encode_func = _get_mean_value_method(nodata)
        return self._encode_layer(window_func, encode_func, column_name)

    # ...............................
    def encode_largest_class(
        self,
        layer_filename,
        column_name,
        min_coverage,
        resolution=None,
        bbox=None,
        nodata=DEFAULT_NODATA,
        attribute_name=None,
    ):
        """Encodes a layer based on the largest class in each data window.

        Args:
            layer_filename: The file location of the layer to encode.
            column_name: What to name this column in the encoded matrix.
            min_coverage: The minimum percentage of each data window that must
                be the covered by the largest class.
            resolution: If the layer is a vector, optionally use this as the
                resolution of the data grid.
            bbox: If the layer is a vector, optionally use this bounding box
                for the data grid.
            nodata: If the layer is a vector, optionally use this as the data
                grid nodata value.
            attribute_name: If the layer is a vector, use this field to
                determine the largest class.

        Returns:
            list of str: A list of column headers for the newly encoded columns.
        """
        window_func, nodata, _ = self._read_layer(
            layer_filename,
            resolution=resolution,
            bbox=bbox,
            nodata=nodata
        )
        encode_func = _get_largest_class_method(min_coverage, nodata)
        return self._encode_layer(window_func, encode_func, column_name)

    # ...............................
    def get_encoded_matrix(self):
        """Returns the encoded matrix.

        Returns:
            Matrix: The encoded matrix as a Matrix object
        """
        return self.encoded_matrix

    # ...............................
    def get_geojson(self):
        """Formats the encoded matrix as GeoJSON.

        Returns:
            dict: A JSON dictionary for the encoded matrix.
        """
        return geojsonify_matrix_with_shapefile(
            self.encoded_matrix, self.grid_filename
        )


# .............................................................................
__all__ = ['LayerEncoder']
