"""Module containing tools for creating maps."""
import logging
import numpy as np
from osgeo import gdal

from lmpy.matrix import Matrix


# .....................................................................................
def _create_empty_map_matrix_from_matrix(matrix):
    """Creates an empty 2-d matrix to use for mapping.

    Args:
        matrix (lmpy.matrix.Matrix): A matrix containing sites along the y/0 axis
            and species or statistics along the x/1 axis.

    Returns:
        Matrix: A Matrix of zeros for the spatial extent.

    Note:
        axis 0 represents the rows/y coordinate/latitude
        axis 1 represents the columns/x coordinate/longitude
    """
    # Headers are coordinate centroids
    x_headers, y_headers = _get_coordinate_headers(matrix)
    map_matrix = Matrix(
        np.zeros((len(y_headers), len(x_headers)), dtype=int),
        headers={
            "0": y_headers,
            "1": x_headers
        }
    )
    return map_matrix


# .....................................................................................
def _create_empty_map_matrix(min_x, min_y, max_x, max_y, resolution):
    """Creates an empty 2-d matrix to use for mapping.

    Args:
        min_x (numeric): The minimum x value of the map extent.
        min_y (numeric): The minimum y value of the map extent.
        max_x (numeric): The maximum x value of the map extent.
        max_y (numeric): The maximum y value of the map extent.
        resolution (numeric): The size of each matrix cell.

    Returns:
        Matrix: A Matrix of zeros for the spatial extent.

    Note:
        axis 0 represents the rows/y coordinate/latitude
        axis 1 represents the columns/x coordinate/longitude
    """
    x_headers, y_headers = _create_map_matrix_headers_from_extent(
        min_x, min_y, max_x, max_y, resolution)
    map_matrix = Matrix(
        np.zeros((len(y_headers), len(x_headers)), dtype=int),
        headers={
            "0": y_headers,
            "1": x_headers
        }
    )
    return map_matrix


# .....................................................................................
def _get_coordinate_headers(matrix):
    """Get coordinate headers from a matrix with coordinates along one or two axes.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            y centroids in row headers, x centroids in column headers
            OR
            a flattened geospatial matrix with site centroids in row headers.

    Returns:
        x_headers (list): list of x coordinates, centroid of each cell in column
        y_headers (list): list of y coordinates, centroid of each cell in row
    """
    row_headers = matrix.get_row_headers()
    # row/site headers in flattened geospatial matrix are tuples of
    # (siteid, x_coord, y_coord)
    if type(row_headers[0]) is list and len(row_headers[0]) == 3:
        x_headers, y_headers = _get_map_matrix_headers_from_sites(row_headers)
    else:
        x_headers = matrix.get_column_headers()
        y_headers = row_headers

    return x_headers, y_headers


# .....................................................................................
def get_extent_resolution_from_matrix(matrix):
    """Gets x and y extents and resolution of a geospatial matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            y centroids in row headers, x centroids in column headers  OR
            flattened geospatial matrix with site centroids in row headers.

    Returns:
        min_x (numeric): The minimum x value of the map extent.
        min_y (numeric): The minimum y value of the map extent.
        max_x (numeric): The maximum x value of the map extent.
        max_y (numeric): The maximum y value of the map extent.
        x_res (numeric): The width of each matrix cell.
        y_res (numeric): The height of each matrix cell.

    Raises:
        Exception: on matrix of less than 2 columns or rows.
    """
    x_res = y_res = None
    # Headers are coordinate centroids
    y_centers, x_centers = _get_coordinate_headers(matrix)
    # Identify the distance between centroids for resolution
    if len(x_centers) > 1:
        x_res = x_centers[1] - x_centers[0]
    else:
        print("X axis has only one column")
    if len(y_centers) > 1:
        y_res = y_centers[1] - y_centers[0]
    else:
        print("Y axis has only one row")
    if x_res is None and y_res is None:
        raise Exception(
            f"Matrix contains only {len(x_centers)} columns on the x-axis " +
            f"and {len(y_res)} rows on the y-axis")
    elif x_res is None:
        x_res = y_res
    elif y_res is None:
        y_res = x_res
    # Extend to edges by 1/2 resolution
    min_x = x_centers[0] - x_res/2.0
    min_y = y_centers[-1] - y_res/2.0
    max_x = x_centers[-1] + x_res/2.0
    max_y = y_centers[0] + y_res/2.0

    return min_x, min_y, max_x, max_y, x_res, y_res


# .....................................................................................
def _get_map_matrix_headers_from_sites(site_headers):
    """Creates an empty 2-d matrix to use for mapping.

    Args:
        site_headers (list of tuples): A list containing the site headers (siteid, x, y)
            for a flattened geospatial matrix containing sites along the y/0 axis

    Returns:
        x_headers: list of x center coordinates for column headers
        y_headers: list of y center coordinates for row headers
    """
    x_centers = []
    y_centers = []
    for _, x, y in site_headers:
        if x not in x_centers:
            x_centers.append(x)
        if y not in y_centers:
            y_centers.append(y)
    return x_centers, y_centers


# .....................................................................................
def _create_map_matrix_headers_from_extent(min_x, min_y, max_x, max_y, resolution):
    """Gets header values for the x/1 and y/0 axis of a geospatial matrix.

    Args:
        min_x (numeric): The minimum x value of the map extent.
        min_y (numeric): The minimum y value of the map extent.
        max_x (numeric): The maximum x value of the map extent.
        max_y (numeric): The maximum y value of the map extent.
        resolution (numeric): The size of each matrix cell.

    Returns:
        x_headers: list of x center coordinates for column headers
        y_headers: list of y center coordinates for row headers

    Note:
        The function holds UL coordinates (min_x and max_y) static, but LR coordinates
        (max_x, min_y) may change to accommodate the resolution requested.
    """
    # Y upper coordinates
    num_rows = len(np.arange(max_y, min_y, -resolution))
    # X left coordinates
    num_cols = len(np.arange(min_x, max_x, resolution))
    # Center coordinates
    y_headers = [max_y - (j + .5) * resolution for j in range(num_rows)]
    x_headers = [min_x + (i + .5) * resolution for i in range(num_cols)]
    return x_headers, y_headers


# .....................................................................................
def get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution):
    """Get a function to return a row and column for an x, y.

    Args:
        min_x (numeric): The minimum x value of the heatmap range.
        min_y (numeric): The minimum y value of the heatmap range.
        max_x (numeric): The maximum x value of the heatmap range.
        max_y (numeric): The maximum y value of the heatmap range.
        resolution (numeric): The size of each matrix cell.

    Returns:
        Method: A method to generate row and column indices for an x, y.

    Note:
        Parallels the construction of shapegrid in lmpy.data_preparation.build_grid
    """
    # Get evenly spaced values within min and max values for UL coordinates
    x_headers, y_headers = _create_map_matrix_headers_from_extent(
        min_x, min_y, max_x, max_y, resolution)
    num_rows = len(y_headers)
    num_cols = len(x_headers)

    # .......................
    def get_row_col_func(x, y):
        """Get the row and column where the point is located.

        Args:
            x (numeric): The x value to convert.
            y (numeric): The y value to convert.

        Returns:
            int, int: The row and column where the point is located.
        """
        r = int(min(num_rows - 1, max(0, int((max_y - y) // resolution))))
        c = int(min(num_cols - 1, max(0, int((x - min_x) // resolution))))
        return r, c

    return get_row_col_func


# .....................................................................................
def create_point_heatmap_matrix(readers, min_x, min_y, max_x, max_y, resolution):
    """Create a point heatmap matrix.

    Args:
        readers (PointReader or list of PointReader): A source of point data for
            creating the heatmap.
        min_x (numeric): The minimum x value of the heatmap range.
        min_y (numeric): The minimum y value of the heatmap range.
        max_x (numeric): The maximum x value of the heatmap range.
        max_y (numeric): The maximum y value of the heatmap range.
        resolution (numeric): The size of each matrix cell.

    Returns:
        Matrix: A matrix of point density.
    """
    # Create empty 2-dimensional matrix for the sites as a map
    report = {
        "input_data": []
    }
    heatmap = _create_empty_map_matrix(min_x, min_y, max_x, max_y, resolution)
    get_row_col_func = get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution)

    if not isinstance(readers, list):
        readers = [readers]
    for reader in readers:
        try:
            rdr_rpt = {
                "type": "DWCA",
                "file": reader.archive_filename,
                "x_field": reader.x_term,
                "y_field": reader.y_term,
                "count": 0}
            if reader.geopoint_term is not None:
                rdr_rpt["geopoint_field"] = reader.geopoint_term
        except AttributeError:
            rdr_rpt = {
                "type": "CSV",
                "file": reader.filename,
                "x_field": reader.x_field,
                "y_field": reader.y_field,
                "count": 0}
            if reader.geopoint is not None:
                rdr_rpt["geopoint_field"] = reader.geopoint

        reader.open()
        for points in reader:
            for point in points:
                row, col = get_row_col_func(point.x, point.y)
                heatmap[row, col] += 1
                rdr_rpt["count"] += 1
        reader.close()
        report["input_data"].append(rdr_rpt)
    return heatmap, report


# .....................................................................................
def _get_geotransform(min_x, min_y, max_x, max_y, resolution):
    """Get the geotransform (described below) required for GDAL for the output raster.

    Args:
        min_x (numeric): The minimum x value of the geospatial extent.
        min_y (numeric): The minimum y value of the geospatial extent.
        max_x (numeric): The maximum x value of the geospatial extent.
        max_y (numeric): The maximum y value of the geospatial extent.
        resolution (numeric): The size of each matrix cell.

    Returns:
        tuple of 6 elements, defined as:
            (0) x-coordinate of the upper-left corner of the upper-left pixel.
            (1) w-e pixel resolution / pixel width.
            (2) row rotation (typically zero).
            (3) y-coordinate of the upper-left corner of the upper-left pixel.
            (4) column rotation (typically zero).
            (5) n-s pixel resolution / pixel height (negative value for a north-up
                image).
    """
    # headers contain centroid coordinates
    x_headers, y_headers = _create_map_matrix_headers_from_extent(
        min_x, min_y, max_x, max_y, resolution)
    ul_x = x_headers[0] - (resolution * .5)
    ul_y = y_headers[-1] + (resolution * .5)
    geotransform = (ul_x, resolution, 0, ul_y, 0, -resolution)
    return geotransform


# ...................................................................................
def rasterize_matrix(matrix, out_raster_filename, column=None, logger=None):
    """Create a geotiff raster file from one or all columns in a 2d geospatial matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input flattened geospatial matrix with
            site centroids in row headers.
        out_raster_filename: output filename.
        column (str): header of the column of interest.  If None, all columns will
            be included as bands in a multi-band raster.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report (dict): summary dictionary of inputs and outputs.

    Raises:
        Exception: on GDAL raster dataset creation
    """
    refname = "rasterize_matrix"
    columns = matrix.get_column_headers()
    if column:
        if column not in columns:
            raise Exception(
               f"Column {column} is not present in matrix columns {columns}")
        else:
            columns = [column]

    map_mtx = _create_empty_map_matrix_from_matrix(matrix)
    min_x, min_y, max_x, max_y, x_res, y_res = get_extent_resolution_from_matrix(
        matrix)
    geotransform = _get_geotransform(min_x, min_y, max_x, max_y, x_res)

    height, width = map_mtx.shape
    if matrix.dtype == np.float32:
        arr_type = gdal.GDT_Float32
    else:
        arr_type = gdal.GDT_Int32
    report = {
        "height": height,
        "width": width,
        "matrix_type": matrix.dtype.__name__
    }

    driver = gdal.GetDriverByName("GTiff")
    try:
        out_ds = driver.Create(
            out_raster_filename, width, height, 1, arr_type)
        # out_ds.SetProjection(in_ds.GetProjection())
        # TODO: handle differing x and y resolutions
        # Use only x-resolution for now
        out_ds.SetGeoTransform(geotransform)
    except Exception as e:
        logger.log(
            f"Exception in GDAL function {e}", refname=refname,
            log_level=logging.ERROR)
        raise
    else:
        # band indexes start at 1
        band_idx = 1
        for col in columns:
            col_map_mtx = create_map_matrix_for_column(matrix, column)
            out_band = out_ds.GetRasterBand(band_idx)
            out_band.WriteArray(col_map_mtx, 0, 0)
            out_band.FlushCache()
            out_band.ComputeStatistics(False)
            band_idx += 1
            report[f"band {band_idx}"] = col
    return report


# ...................................................................................
def rasterize_map_matrix(map_matrix, out_raster_filename, logger=None):
    """Create a geotiff raster file from one or all columns in a 2d geospatial matrix.

    Args:
        map_matrix (lmpy.matrix.Matrix object): an input geospatial matrix with
            x coordinates in column headers and y coordinates in row headers.
        out_raster_filename: output filename.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report (dict): summary dictionary of inputs and outputs.

    Raises:
        Exception: on GDAL raster dataset creation
    """
    refname = "rasterize_map_matrix"

    map_mtx = _create_empty_map_matrix_from_matrix(map_matrix)
    min_x, min_y, max_x, max_y, x_res, y_res = get_extent_resolution_from_matrix(
        map_matrix)
    geotransform = _get_geotransform(min_x, min_y, max_x, max_y, x_res)

    height, width = map_mtx.shape
    if map_matrix.dtype == np.float32:
        arr_type = gdal.GDT_Float32
    else:
        arr_type = gdal.GDT_Int32
    report = {
        "height": height,
        "width": width,
        "matrix_type": str(map_matrix.dtype)
    }

    driver = gdal.GetDriverByName("GTiff")
    try:
        out_ds = driver.Create(
            out_raster_filename, width, height, 1, arr_type)
        # TODO: handle differing x and y resolutions
        # Use only x-resolution for now
        out_ds.SetGeoTransform(geotransform)
    except Exception as e:
        logger.log(
            f"Exception in GDAL function {e}", refname=refname,
            log_level=logging.ERROR)
        raise
    else:
        # band indexes start at 1
        band_idx = 1
        out_band = out_ds.GetRasterBand(band_idx)
        out_band.WriteArray(map_matrix, 0, 0)
        out_band.FlushCache()
        out_band.ComputeStatistics(False)
        band_idx += 1
    return report


# .....................................................................................
def create_map_matrix_for_column(matrix, col_header):
    """Create a map matrix from one column in a 2d matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            x,y centroids in row headers, other data attributes in column headers.
        col_header (str): column header for data to map

    Returns:
        map_mtx (lmpy.matrix.Matrix): a 2d geospatial matrix with y centroids in row
            headers, x centroids in column headers.
    """
    # Create empty 2-dimensional matrix, with x/0 = longitude and y/1 = latitude
    map_mtx = _create_empty_map_matrix_from_matrix(matrix)
    min_x, min_y, max_x, max_y, x_res, y_res = get_extent_resolution_from_matrix(
        matrix)
    report = {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "matrix_type": str(matrix.dtype)
    }
    get_row_col_func = get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, x_res)

    # Get index of column of interest
    col_idx = matrix.get_column_headers().index(col_header)
    site_headers = matrix.get_row_headers()
    # Fill matrix with value for each site in the column
    for matrix_row in range(matrix.shape[0]):
        _, x, y = site_headers[matrix_row]
        row, col = get_row_col_func(x, y)
        map_mtx[row, col] += matrix[matrix_row, col_idx]

    return map_mtx, report

# # ...................................................................................
# def vectorize_matrix_with_shapefile(
#         matrix, grid_filename, out_shapefilename, resolution, logger=None):
#     """Create a geotiff raster file of 1+ bands from a 2d geospatial matrix.
#
#     Args:
#         matrix (lmpy.matrix.Matrix object): an input flattened geospatial matrix with
#             site centroids in row headers.
#         grid_filename (str): A file path to a shapefile matching the matrix.
#         out_shapefilename: output filename.
#         logger (lmpy.log.Logger): An optional local logger to use for logging output
#             with consistent options
#     """
#     refname = "vectorize_matrix_with_shapefile"
#     site_axis = 0
#     # Create empty 2-dimensional matrix, with x/0 = longitude and y/1 = latitude
#     column_headers = matrix.get_column_headers()
#     row_headers = matrix.get_headers(axis=site_axis)
#     if logger is not None:
#         logger.log(
#             f"Found {len(row_headers)} sites and {len(column_headers)} taxa.",
#             refname=refname)
#
#     column_enum = [(j, str(k)) for j, k in enumerate(column_headers)]
#
#     if not os.path.exists(grid_filename):
#         raise FileNotFoundError(f"Grid shapefile {grid_filename} does not exist.")
#     driver = ogr.GetDriverByName("ESRI Shapefile")
#     # 0 means read-only. 1 means writeable.
#     grid_dataset = driver.Open(grid_filename, 0)
#     grid_layer = grid_dataset.GetLayer()
#     (min_x, max_x, min_y, max_y) = grid_layer.GetExtent()
#     if logger is not None:
#         logger.log(
#             f"Found {grid_layer.GetFeatureCount()} sites in grid, with extent " +
#             f"(min_x, max_x, min_y, max_y) = ({min_x}, {max_x}, {min_y}, {max_y}).",
#             refname=refname)
#
#     map_mtx = create_empty_map_matrix(min_x, min_y, max_x, max_y, resolution)
#     height, width = map_mtx.shape
#     get_row_col_func = get_row_col_for_x_y_func(
#          min_x, min_y, max_x, max_y, resolution)
#
#     if matrix.dtype == np.float32:
#         arr_type = gdal.GDT_Float32
#     else:
#         arr_type = gdal.GDT_Int32
#
#     out_ds = driver.Create(out_shapefilename, 1)
#     id_fld = "siteid"
#
#     # Find row index for feature ids of grid cells in possibly compressed matrix
#     fids_in_matrix = {}
#     for mtx_row, (mtx_fid, _, _) in enumerate(row_headers):
#         fids_in_matrix[mtx_fid] = mtx_row
#
#     feat = grid_layer.GetNextFeature()
#     while feat is not None:
#         # Make sure this grid site is in the matrix
#         site_id = feat.GetField(id_fld)
#         # ft_json = json.loads(feat.ExportToJson())
#         # ft_json["properties"] = {}
#         if site_id in fids_in_matrix.keys():
#             mtx_row = fids_in_matrix[site_id]
#             ft_json = json.loads(feat.ExportToJson())
#             ft_json["id"] = site_id
#             ft_json["properties"] = {}
#             for tx_idx, tx_name in column_enum:
#                 if matrix[mtx_row, tx_idx].item() not in omit_values:
#                     ft_json["properties"][tx_name] = matrix[mtx_row, tx_idx].item()
#             # ft_json["properties"] = {
#             #     k: matrix[i, j].item() for j, k in column_enum
#             #     if matrix[i, j].item() not in omit_values
#             # }
#             if len(ft_json["properties"].keys()) > 0:
#                 features.append(ft_json)
#         feat = grid_layer.GetNextFeature()
#     # out_ds.SetProjection(in_ds.GetProjection())
#     geotransform = get_geotransform(min_x, min_y, max_x, max_y, resolution)
#     out_ds.SetGeoTransform(geotransform)
#
#     band_num = 0
#     for ch in col_headers:
#         # band indexes start at 1
#         band_num += 1
#         # create 2d geospatial matrix from column
#         map_mtx = create_map_matrix_for_column(
#             matrix, ch, min_x, min_y, max_x, max_y, resolution)
#         # write each column into a separate band
#         out_band = out_ds.GetRasterBand(band_num)
#         out_band.WriteArray(map_mtx, 0, 0)
#         out_band.FlushCache()
#         out_band.ComputeStatistics(False)
#         map_mtx = None
#     # Once we"re done, close properly the dataset
#     out_ds = None


# .....................................................................................
__all__ = [
    "create_map_matrix_for_column",
    "create_point_heatmap_matrix",
    "get_extent_resolution_from_matrix",
    "get_row_col_for_x_y_func",
    "rasterize_matrix"
]
