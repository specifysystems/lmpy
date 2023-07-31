"""Module containing tools for creating GeoJSON from matrices."""
import json
import os.path

from osgeo import ogr

from lmpy.log import logit


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
            "type": "Point",
            "coordinates": [x, y]
        }

    # .......................
    def _make_polygon_geojson_geometry(x, y):
        return {
            "type": "Polygon",
            "coordinates": [
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
def geojsonify_matrix(matrix, resolution=None, omit_values=None, logger=None):
    """Creates GeoJSON of points or polygons for a compressed or uncompressed matrix.

    Args:
        matrix (Matrix): A (spatial) matrix to create GeoJSON for, with sites
            represented as rows, along the y/0 axis.
        resolution (Numeric): The size of the grid cells in decimal degrees.  If None,
            identify the resolution from the input matrix.  This assumes that for
            compressed matrices, there are at least one adjacent pair of rows or
            columns present in the matrix.
        omit_values (list): Omit properties when their value is in this list.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report: A JSON compatible dictionary with report.
        matrix_geojson: A GeoJSON compatible dictionary of features.
    """
    refname = "geojsonify_matrix"
    matrix_geojson = {"type": "FeatureCollection"}
    row_headers = matrix.get_row_headers()
    column_headers = matrix.get_column_headers()
    logit(
        logger,
        f"Found {len(row_headers)} sites and {len(column_headers)} taxa in matrix.",
        refname=refname)

    _, _, res = matrix.get_coordinate_headers_resolution()
    if resolution is None:
        resolution = res

    omit_values = _process_omit_values(omit_values, matrix.dtype.type)
    if omit_values:
        logit(logger, f"Omit values {omit_values} from geojson.", refname=refname)
    make_geometry_func = _get_geojson_geometry_func(resolution=resolution)

    features = []
    column_enum = [(j, str(k)) for j, k in enumerate(column_headers)]
    for i, (site_id, x, y) in enumerate(row_headers):
        ft_json = dict(type="Feature", geometry=make_geometry_func(x, y))
        ft_json["id"] = site_id
        ft_json["properties"] = {
            k: matrix[i, j].item() for j, k in column_enum
            if matrix[i, j].item() not in omit_values
        }
        if len(ft_json["properties"].keys()) > 0:
            features.append(ft_json)

    matrix_geojson["features"] = features
    logit(logger, f"Added {len(features)} sites to geojson.", refname=refname)

    report = {
        "matrix_species_count": len(column_headers),
        "matrix_site_count": len(row_headers),
        "json_site_count": len(features),
        "feature_type": "point",
    }
    if resolution is not None:
        report["feature_type"] = "polygon"
        report["grid_resolution"] = resolution
    if omit_values:
        ovals = [str(x) for x in omit_values]
        report["ignored_values"] = ovals
    return report, matrix_geojson


# .....................................................................................
def geojsonify_matrix_with_shapefile(
        matrix, grid_filename, omit_values=None, logger=None):
    """Creates GeoJSON for a matrix, compressed or original, and matching shapefile.

    Args:
        matrix (Matrix): A 2 dimensional (spatial) matrix to create GeoJSON for, with
            sites represented as rows, along the y/0 axis..
        grid_filename (str): A file path to a shapefile matching the matrix.
        omit_values (list): Omit properties when their value is in this list.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report: A JSON compatible dictionary with report.
        matrix_geojson: A GeoJSON compatible dictionary of features.

    Raises:
        FileNotFoundError: on missing input shapefile
    """
    refname = "geojsonify_matrix_with_shapefile"

    site_axis = 0
    omit_values = _process_omit_values(omit_values, matrix.dtype.type)
    matrix_geojson = {"type": "FeatureCollection"}
    features = []

    column_headers = matrix.get_column_headers()
    row_headers = matrix.get_headers(axis=site_axis)
    logit(
        logger,
        f"Found {len(row_headers)} sites and {len(column_headers)} taxa in matrix.",
        refname=refname)
    if omit_values:
        logit(logger, f"Omit values {omit_values} from geojson.", refname=refname)

    column_enum = [(j, str(k)) for j, k in enumerate(column_headers)]

    if not os.path.exists(grid_filename):
        raise FileNotFoundError(f"Grid shapefile {grid_filename} does not exist.")
    grid_dataset = ogr.Open(grid_filename)
    grid_layer = grid_dataset.GetLayer()
    logit(
        logger, f"Found {grid_layer.GetFeatureCount()} sites in grid.", refname=refname)
    # Find the feature values to match grid sites with matrix sites
    # TODO: get dynamically?
    id_fld = "siteid"

    # Find row index for feature ids of grid cells in possibly compressed matrix
    fids_in_matrix = {}
    for mtx_row, (mtx_fid, _, _) in enumerate(row_headers):
        fids_in_matrix[mtx_fid] = mtx_row

    feat = grid_layer.GetNextFeature()
    while feat is not None:
        # Make sure this grid site is in the matrix
        site_id = feat.GetField(id_fld)
        if site_id in fids_in_matrix.keys():
            mtx_row = fids_in_matrix[site_id]
            ft_json = json.loads(feat.ExportToJson())
            ft_json["id"] = site_id
            ft_json["properties"] = {}
            for tx_idx, tx_name in column_enum:
                if matrix[mtx_row, tx_idx].item() not in omit_values:
                    ft_json["properties"][tx_name] = matrix[mtx_row, tx_idx].item()
            if len(ft_json["properties"].keys()) > 0:
                features.append(ft_json)
        feat = grid_layer.GetNextFeature()

    matrix_geojson["features"] = features
    logit(logger, f"Added {len(features)} sites to geojson.", refname=refname)

    # Explicitly delete OGR objects
    grid_dataset = grid_layer = None

    report = {
        "grid_filename": grid_filename,
        "matrix_species_count": len(column_headers),
        "matrix_site_count": len(row_headers),
        "json_site_count": len(features),
        "feature_type": "polygon",
    }
    if omit_values:
        ovals = [str(x) for x in omit_values]
        report["ignored_values"] = ovals
    return report, matrix_geojson


# .....................................................................................
__all__ = ["geojsonify_matrix", "geojsonify_matrix_with_shapefile"]
