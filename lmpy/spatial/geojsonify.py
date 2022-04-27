"""Module containing tools for creating GeoJSON from matrices."""
import json

from osgeo import ogr


# .....................................................................................
def _process_omit_values(omit_values, matrix_dtype):
    """Process the incoming omit values to ensure they match matrix values type.

    Args:
        omit_values (list or None): A list of incoming omit values.
        matrix_dtype (type): The data type of the matrix values

    Returns:
        list: A list of values converted to the same type as the compare matrix.
    """
    if omit_values is None:
        return []
    return [matrix_dtype(val) for val in omit_values]


# .....................................................................................
def _get_geojson_geometry_func(resolution=None):
    """Get a function that will generate GeoJSON geometry sections for an x, y pair.

    Args:
        resolution (Numeric or None): If None, use point geometries, else polygons.

    Returns:
        Method: A function taking x, y pairs and returning dict geometry reference.
    """
    if resolution is not None:
        half_res = resolution / 2

    # .......................
    def _make_point_geojson_geometry(x, y):
        return {
            'type': 'Point',
            'coordinates': [x, y]
        }

    # .......................
    def _make_polygon_geojson_geometry(x, y):
        return {
            'type': 'Polygon',
            'coordinates': [
                [
                    [x - half_res, y - half_res],
                    [x + half_res, y - half_res],
                    [x + half_res, y + half_res],
                    [x - half_res, y + half_res],
                    [x - half_res, y - half_res],
                ]
            ]
        }

    if resolution is None:
        return _make_point_geojson_geometry
    return _make_polygon_geojson_geometry


# .....................................................................................
def geojsonify_matrix(matrix, resolution=None, omit_values=None):
    """Creates GeoJSON for a matrix and matching shapefile.

    Args:
        matrix (Matrix): A (spatial) matrix to create GeoJSON for.
        resolution (Numeric): The size of the grid cells in decimal degrees
        omit_values (list): Omit properties when their value is in this list.

    Returns:
        dict: A GeoJSON compatible dictionary.
    """
    omit_values = _process_omit_values(omit_values, matrix.dtype.type)
    ret = {'type': 'FeatureCollection'}
    features = []

    make_geometry_func = _get_geojson_geometry_func(resolution=resolution)

    row_headers = matrix.get_row_headers()
    column_headers = matrix.get_column_headers()

    column_enum = [(j, str(k)) for j, k in enumerate(column_headers)]

    for i, (site_id, x, y) in enumerate(row_headers):
        ft_json = dict(type='Feature', geometry=make_geometry_func(x, y))
        ft_json['id'] = site_id
        ft_json['properties'] = {
            k: matrix[i, j].item() for j, k in column_enum
            if matrix[i, j].item() not in omit_values
        }
        if len(ft_json['properties'].keys()) > 0:
            features.append(ft_json)

    ret['features'] = features
    return ret


# .....................................................................................
def geojsonify_matrix_with_shapefile(matrix, shapegrid_filename, omit_values=None):
    """Creates GeoJSON for a matrix and matching shapefile.

    Args:
        matrix (Matrix): A (spatial) matrix to create GeoJSON for.
        shapegrid_filename (str): A file path to a shapefile matching the matrix.
        omit_values (list): Omit properties when their value is in this list.

    Returns:
        dict: A GeoJSON compatible dictionary.
    """
    omit_values = _process_omit_values(omit_values, matrix.dtype.type)
    ret = {'type': 'FeatureCollection'}
    features = []

    column_headers = matrix.get_column_headers()

    column_enum = [(j, str(k)) for j, k in enumerate(column_headers)]

    shapegrid_dataset = ogr.Open(shapegrid_filename)
    shapegrid_layer = shapegrid_dataset.GetLayer()

    i = 0
    feat = shapegrid_layer.GetNextFeature()
    while feat is not None:
        ft_json = json.loads(feat.ExportToJson())
        ft_json['properties'] = {
            k: matrix[i, j].item() for j, k in column_enum
            if matrix[i, j].item() not in omit_values
        }
        if len(ft_json['properties'].keys()) > 0:
            features.append(ft_json)
        i += 1
        feat = shapegrid_layer.GetNextFeature()

    ret['features'] = features
    shapegrid_dataset = shapegrid_layer = None
    return ret


# .....................................................................................
__all__ = ['geojsonify_matrix', 'geojsonify_matrix_with_shapefile']
