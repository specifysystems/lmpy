"""Module containing tools for creating maps."""
import logging
import math

import numpy as np
from osgeo import gdal

from lmpy.log import logit
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
    x_headers, y_headers, resolution = get_coordinate_headers_resolution(matrix)
    map_matrix = Matrix(
        np.zeros((len(y_headers), len(x_headers)), dtype=int),
        headers={
            "0": y_headers,
            "1": x_headers
        }
    )
    return map_matrix


# .....................................................................................
def _create_empty_map_matrix_from_extent(min_x, min_y, max_x, max_y, resolution):
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
def _create_empty_map_matrix_from_centroids(x_centers, y_centers, dtype):
    """Creates an empty 2-d matrix to use for mapping.

    Args:
        x_centers (list of numeric): Center coordinate x values.
        y_centers (list of numeric): Center coordinate y values.
        dtype (numpy.ndarray.dtype): Data type for new matrix

    Returns:
        Matrix: A Matrix of zeros for the coordinate centers.

    Note:
        axis 0 represents the rows/y coordinate/latitude
        axis 1 represents the columns/x coordinate/longitude
    """
    map_matrix = Matrix(
        np.zeros((len(y_centers), len(x_centers)), dtype=dtype),
        headers={
            "0": y_centers,
            "1": x_centers
        }
    )
    return map_matrix


# .....................................................................................
def is_flattened_geospatial_matrix(matrix):
    """Identifies whether matrix has x and y coordinates along 1 and 0 axes.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            y centroids in row headers, x centroids in column headers  OR
            flattened geospatial matrix with site centroids in row headers.

    Returns:
        True if flattened geospatial matrix,
        False if x coordinates in columns, y coordinates in rows
    """
    row_headers = matrix.get_row_headers()
    # row/site headers in flattened geospatial matrix are tuples of
    # (siteid, x_coord, y_coord)
    if type(row_headers[0]) is list and len(row_headers[0]) == 3:
        return True
    else:
        return False


# .....................................................................................
def get_coordinate_headers_resolution(matrix):
    """Get coordinate headers from a matrix with coordinates along one or two axes.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            y centroids in row headers, x centroids in column headers
            OR
            a flattened geospatial matrix with site centroids in row headers.

    Returns:
        x_headers (list): list of x coordinates, centroid of each cell in column
        y_headers (list): list of y coordinates, centroid of each cell in row

    Raises:
        Exception: on matrix contains < 2 columns
        Exception: on matrix contains < 2 rows

    Notes:
        Assume that if the matrix is compressed, there are at least one pair of
            neighboring rows or columns.
        Assumes x and y resolution are equal
    """
    row_headers = matrix.get_row_headers()
    if is_flattened_geospatial_matrix(matrix):
        x_resolution, x_centers, y_centers = _get_map_resolution_headers_from_sites(
            row_headers)
    else:
        # If getting from a map matrix, sites should not be compressed
        x_centers = matrix.get_column_headers()
        y_centers = row_headers
        x_resolution = x_centers[1] - x_centers[0]

    if len(x_centers) <= 1:
        raise Exception(
            f"Matrix contains only {len(x_centers)} columns on the x-axis ")
    if len(y_centers) <= 1:
        raise Exception(
            f"Matrix contains only {len(y_centers)} rows on the y-axis")

    return x_centers, y_centers, x_resolution


# .....................................................................................
def get_extent_resolution_coords_from_matrix(matrix):
    """Gets x and y extents and resolution of an uncompressed geospatial matrix.

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
        height (numeric): the number of rows, axis 0, of the matrix
        width (numeric): the number of columns, axis 1, of the matrix
    """
    # Headers are coordinate centroids
    x_centers, y_centers, resolution = get_coordinate_headers_resolution(matrix)

    # Extend to edges by 1/2 resolution
    min_x = x_centers[0] - resolution/2.0
    min_y = y_centers[-1] - resolution/2.0
    max_x = x_centers[-1] + resolution/2.0
    max_y = y_centers[0] + resolution/2.0

    return min_x, min_y, max_x, max_y, resolution, x_centers, y_centers


# .....................................................................................
def _get_map_resolution_headers_from_sites(site_headers):
    """Creates an empty 2-d matrix to use for mapping.

    Args:
        site_headers (list of tuples): A list containing the site headers (siteid, x, y)
            for a flattened geospatial matrix containing sites along the y/0 axis

    Returns:
        x_headers: list of x center coordinates for column headers
        y_headers: list of y center coordinates for row headers

    Notes:
        If the matrix is compressed, with empty rows (sites) and columns removed, the
        missing site coordinates will be filled in to the map matrix headers
        so the map will represent the geospatial region without holes.  If all sites
        are missing from an edge (upper, lower, right, left boundary) of the area
        of interest, those will not be retained, the extent of the map will be smaller.
    """
    # Second and third sites along the upper boundary - first siteid could be 0
    site_2, x_2, y_2 = site_headers[1]
    site_3, x_3, y_3 = site_headers[2]
    # Find resolution in a regular or compressed matrix by dividing
    # map distance by number of cells between sites
    x_resolution = (x_3 - x_2)/(site_3 - site_2)

    # Extent of matrix, using centroid coordinate values (not cell edges)
    minx = maxx = x_2
    miny = maxy = y_2
    for _, x, y in site_headers:
        if x < minx:
            minx = x
        if x > maxx:
            maxx = x
        if y < miny:
            miny = y
        if y > maxy:
            maxy = y
    # Fill in any x or y centroids missing from the input site_headers/matrix
    x_centers = list(np.arange(minx, (maxx + x_resolution), x_resolution))
    y_centers = list(np.arange(maxy, (miny - x_resolution), (x_resolution * -1)))
    return x_resolution, x_centers, y_centers


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
    # Y upper coordinates, goes from North to south
    num_rows = len(np.arange(max_y, min_y, -resolution))
    # X left coordinates
    num_cols = len(np.arange(min_x, max_x, resolution))
    # Center coordinates
    y_headers = [max_y - (j + .5) * resolution for j in range(num_rows)]
    x_headers = [min_x + (i + .5) * resolution for i in range(num_cols)]
    return x_headers, y_headers


# .....................................................................................
def _get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution):
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
    def xy_to_rc_func(x, y):
        """Get the row and column where the point is located.

        Args:
            x (numeric): The x value to convert.
            y (numeric): The y value to convert.

        Returns:
            int, int: The row and column where the point is located.
        """
        row_calc = int((max_y - y) // resolution)
        col_calc = int((x - min_x) // resolution)

        out_of_range = False
        if row_calc not in range(0, num_rows) or col_calc not in range(0, num_cols):
            out_of_range = True

        if out_of_range:
            r = c = -1
        else:
            r = row_calc
            c = col_calc

        return r, c

    return xy_to_rc_func


# .....................................................................................
def create_point_heatmap_matrix(
        readers, min_x, min_y, max_x, max_y, resolution, logger=None):
    """Create a point heatmap matrix.

    Args:
        readers (PointReader or list of PointReader): A source of point data for
            creating the heatmap.
        min_x (numeric): The minimum x value of the heatmap range.
        min_y (numeric): The minimum y value of the heatmap range.
        max_x (numeric): The maximum x value of the heatmap range.
        max_y (numeric): The maximum y value of the heatmap range.
        resolution (numeric): The size of each matrix cell.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        Matrix: A matrix of point density.
    """
    refname = "create_point_heatmap_matrix"
    # Create empty 2-dimensional matrix for the sites as a map
    report = {
        "input_data": [],
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "resolution": resolution
    }
    heatmap = _create_empty_map_matrix_from_extent(
        min_x, min_y, max_x, max_y, resolution)
    xy_2_rc = _get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution)
    logit(
        logger, "Created map matrix with min_x, min_y, max_x, max_y, resolution " +
        f"values min_x {min_x}, min_y {min_y}, max_x {max_x}, max_y {max_y}, " +
        f"resolution {resolution}", refname=refname)

    if not isinstance(readers, list):
        readers = [readers]
    for reader in readers:
        try:
            rdr_rpt = {
                "type": "DWCA",
                "file": reader.archive_filename,
                "x_field": reader.x_term,
                "y_field": reader.y_term,
                "out_of_range": 0,
                "count": 0}
            if reader.geopoint_term is not None:
                rdr_rpt["geopoint_field"] = reader.geopoint_term
        except AttributeError:
            rdr_rpt = {
                "type": "CSV",
                "file": reader.filename,
                "x_field": reader.x_field,
                "y_field": reader.y_field,
                "out_of_range": 0,
                "count": 0}
            if reader.geopoint is not None:
                rdr_rpt["geopoint_field"] = reader.geopoint

        reader.open()
        for points in reader:
            for point in points:
                row, col = xy_2_rc(point.x, point.y)
                if -1 in (row, col):
                    rdr_rpt["out_of_range"] += 1
                else:
                    heatmap[row, col] += 1
                    rdr_rpt["count"] += 1
        reader.close()
        logit(
            logger, f"Read {rdr_rpt['count']} points within extent, and " +
            f"{rdr_rpt['out_of_range']} out of range, from {rdr_rpt['type']} " +
            f"file {rdr_rpt['file']}.", refname=refname)

        report["input_data"].append(rdr_rpt)
    report["min_cell_point_count"] = int(heatmap.min())
    report["max_cell_point_count"] = int(heatmap.max())
    logit(
        logger, "Populated map matrix with point counts for each cell ranging from " +
        f"{report['min_cell_point_count']} to {report['max_cell_point_count']}",
        refname=refname)
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
    ul_y = y_headers[0] + (resolution * .5)
    geotransform = (ul_x, resolution, 0, ul_y, 0, -resolution)
    return geotransform


# ...................................................................................
def rasterize_flattened_matrix(
        matrix, out_raster_filename, columns=None, is_pam=False, nodata=-9999,
        logger=None):
    """Create a geotiff raster file from one or all columns in a 2d geospatial matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input flattened geospatial matrix with
            site centroids in row headers.
        out_raster_filename: output filename.
        columns (list of str): headers of the columns to be included as bands.  If None,
            all columns will be included as bands.
        is_pam (bool): If true, input matrix is binary, and output raster will be
            written with values stored as bytes
        nodata (numeric): value for cells with no data in them
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report (dict): summary dictionary of inputs and outputs.

    Raises:
        Exception: on GDAL raster dataset creation
    """
    refname = "rasterize_flattened_matrix"
    column_headers = matrix.get_column_headers()
    if columns is not None:
        for col in columns:
            if col not in column_headers:
                raise Exception(
                   f"Column {col} is not present in matrix columns")
    else:
        columns = column_headers

    # Get geotransform elements and datatype from input matrix
    (min_x, min_y, max_x, max_y, resolution, x_centers,
     y_centers) = get_extent_resolution_coords_from_matrix(matrix)
    logit(
        logger, f"Found bounding box {min_x}, {min_y}, {max_x}, {max_y} for matrix",
        refname=refname, log_level=logging.DEBUG)
    # TODO: handle differing x and y resolutions
    geotransform = _get_geotransform(min_x, min_y, max_x, max_y, resolution)
    if is_pam is True:
        arr_type = gdal.GDT_Byte
        rst_type_str = "gdal.GDT_Byte"
        # modify the nodata value to fit within a byte
        nodata = 255
    elif matrix.dtype == np.float32:
        arr_type = gdal.GDT_Float32
        rst_type_str = "gdal.GDT_Float32"
    elif matrix.dtype == np.float64:
        arr_type = gdal.GDT_Float64
        rst_type_str = "gdal.GDT_Float64"
    else:
        arr_type = gdal.GDT_Int32
        rst_type_str = "gdal.GDT_Int32"

    report = {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "resolution": resolution,
        "height": len(y_centers),
        "width": len(x_centers),
        "nodata": nodata,
        "raster_data_type": rst_type_str,
        "matrix_type": str(matrix.dtype)
    }

    # Create raster dataset
    driver = gdal.GetDriverByName("GTiff")
    try:
        out_ds = driver.Create(
            out_raster_filename, len(x_centers), len(y_centers), len(columns), arr_type)
        # Add nodata to metadata
        # out_ds.SetMetadata({"TIFFTAG_GDAL_NODATA": f"{nodata}"})
        # out_ds.SetProjection(in_ds.GetProjection())
        out_ds.SetGeoTransform(geotransform)
    except Exception as e:
        logit(
            logger, f"Exception in GDAL function {e}", refname=refname,
            log_level=logging.ERROR)
        raise
    else:
        # band indexes start at 1
        band_idx = 1
        # Create band for each column
        for col in columns:
            empty_map_mtx = _create_empty_map_matrix_from_centroids(
                x_centers, y_centers, matrix.dtype)
            col_map_mtx = _fill_map_matrix_with_column(
                matrix, col, empty_map_mtx, is_pam=is_pam, nodata=nodata)
            out_band = out_ds.GetRasterBand(band_idx)
            out_band.WriteArray(col_map_mtx, 0, 0)
            out_band.FlushCache()
            out_band.ComputeStatistics(False)
            # Add band/column to metadata and report
            out_band.SetMetadata({f"band {band_idx}": f"{col}"})
            report[f"band {band_idx}"] = col
            logit(
                logger, f"Added {col} as band {band_idx}", refname=refname,
                log_level=logging.INFO)
            band_idx += 1
        logit(
            logger, f"Wrote raster with {len(columns)} bands to {out_raster_filename}",
            refname=refname, log_level=logging.INFO)
    return report


# ...................................................................................
def rasterize_map_matrices(map_matrix_dict, out_raster_filename, logger=None):
    """Create a multi-band geotiff raster file from a 2-d long/lat geospatial matrix.

    Args:
        map_matrix_dict (list of lmpy.matrix.Matrix): a list of input geospatial
            matrices with x coordinates in column headers and y coordinates in
            row headers.  All matrices must be of the same shape, extent, and data type.
        out_raster_filename: output filename.
        logger (lmpy.log.Logger): An optional local logger to use for logging output
            with consistent options

    Returns:
        report (dict): summary dictionary of inputs and outputs.

    Raises:
        Exception: on GDAL raster dataset creation
    """
    refname = "rasterize_map_matrix"

    # Use the first matrix for the shape, datatype
    stat_names = list(map_matrix_dict.keys())
    mmtx = map_matrix_dict[stat_names[0]]
    (min_x, min_y, max_x, max_y, resolution, x_centers,
     y_centers) = get_extent_resolution_coords_from_matrix(mmtx)
    geotransform = _get_geotransform(min_x, min_y, max_x, max_y, resolution)
    if mmtx.dtype == np.float32:
        arr_type = gdal.GDT_Float32
    else:
        arr_type = gdal.GDT_Int32
    report = {
        "height": len(y_centers),
        "width": len(x_centers),
        "matrix_type": str(mmtx.dtype)
    }

    driver = gdal.GetDriverByName("GTiff")
    try:
        out_ds = driver.Create(
            out_raster_filename, len(x_centers), len(y_centers), len(stat_names),
            arr_type)
        # TODO: handle differing x and y resolutions
        # Use only x-resolution for now
        out_ds.SetGeoTransform(geotransform)
    except Exception as e:
        logit(
            logger, f"Exception in GDAL function {e}", refname=refname,
            log_level=logging.FATAL)
        raise
    else:
        # band indexes start at 1
        band_idx = 1
        for stat, mtx in map_matrix_dict.items():
            out_band = out_ds.GetRasterBand(band_idx)
            out_band.WriteArray(mtx, 0, 0)
            out_band.FlushCache()
            out_band.ComputeStatistics(False)
            report[f"band{band_idx}"] = stat
            logit(
                logger, f"Added {stat} as band {band_idx}", refname=refname,
                log_level=logging.INFO)
            band_idx += 1
        logit(
            logger, f"Wrote raster with {len(stat_names)} bands to " +
            f"{out_raster_filename}", refname=refname, log_level=logging.INFO)

    return report


# .....................................................................................
def _fill_map_matrix_with_column(
        matrix, col_header, map_matrix, is_pam=False, nodata=-9999):
    """Create a map matrix from one column in a 2d matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            x,y centroids in row headers, other data attributes in column headers.
        col_header (str): column header for data to map
        map_matrix (lmpy.matrix.Matrix object): an empty 2d geospatial matrix with
            y centroids in row headers (0 axis) and x centroids in
            column headers (1 axis)
        is_pam (bool): If true, input matrix is binary, will be written as byte data,
            and nodata value is 255
        nodata (numeric): value for cells with no data in them

    Returns:
        map_mtx (lmpy.matrix.Matrix): a 2d geospatial matrix with y centroids in row
            headers, x centroids in column headers.
    """
    # Create empty 2-dimensional matrix, with x/0 = longitude and y/1 = latitude
    if is_pam:
        nodata = 255

    y_centers = map_matrix.get_row_headers()
    x_centers = map_matrix.get_column_headers()

    # Get index of column of interest
    orig_col_idx = matrix.get_column_headers().index(col_header)
    site_headers = matrix.get_row_headers()
    # Fill matrix with value for each site in the column
    for orig_row_idx, (_, x, y) in enumerate(site_headers):
        # Find the site column value in the original matrix
        site_val = matrix[orig_row_idx, orig_col_idx]
        # Find the x and y coordinates in the map_matrix
        col = x_centers.index(x)
        row = y_centers.index(y)
        # Some stats contain NaN for a cell, change to nodata value
        if math.isnan(site_val):
            val = nodata
        elif matrix.dtype in (np.float32, np.float64):
            val = float(site_val)
        else:
            val = int(site_val)
        map_matrix[row, col] = val

    return map_matrix


# .....................................................................................
def _create_map_matrix_for_column(matrix, col_header, is_pam=False, nodata=-9999):
    """Create a map matrix from one column in a 2d matrix.

    Args:
        matrix (lmpy.matrix.Matrix object): an input 2d geospatial matrix with
            x,y centroids in row headers, other data attributes in column headers.
        col_header (str): column header for data to map
        is_pam (bool): If true, input matrix is binary, will be written as byte data,
            and nodata value is 255
        nodata (numeric): value for cells with no data in them

    Returns:
        map_mtx (lmpy.matrix.Matrix): a 2d geospatial matrix with y centroids in row
            headers, x centroids in column headers.
    """
    # Create empty 2-dimensional matrix, with x/0 = longitude and y/1 = latitude
    if is_pam:
        nodata = 255
    map_mtx = _create_empty_map_matrix_from_matrix(matrix)
    num_cols = map_mtx.shape[1]
    (min_x, min_y, max_x, max_y, resolution, x_centers,
     y_centers) = get_extent_resolution_coords_from_matrix(matrix)
    report = {
        "min_x": min_x,
        "min_y": min_y,
        "max_x": max_x,
        "max_y": max_y,
        "height": len(y_centers),
        "width": len(x_centers),
        "resolution": resolution,
        "matrix_type": str(matrix.dtype)
    }

    # Get index of column of interest
    col_idx = matrix.get_column_headers().index(col_header)
    # Fill matrix with value for each site in the column
    for matrix_row in range(matrix.shape[0]):
        # Convert geospatial 1d matrix index to 2d indices
        row, col = divmod(matrix_row, num_cols)
        site_val = matrix[matrix_row, col_idx]
        # Some stats contain NaN for a cell, change to nodata value
        try:
            val = int(site_val)
        except Exception:
            val = nodata
        map_mtx[row, col] = val

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
#     logit(logger,
#         f"Found {len(row_headers)} sites and {len(column_headers)} taxa.",
#         refname=refname)
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
#     logit(logger,
#         f"Found {grid_layer.GetFeatureCount()} sites in grid, with extent " +
#         f"(min_x, max_x, min_y, max_y) = ({min_x}, {max_x}, {min_y}, {max_y}).",
#         refname=refname)
#
#     map_mtx = create_empty_map_matrix(min_x, min_y, max_x, max_y, resolution)
#     height, width = map_mtx.shape
#     xy_to_rc = _get_row_col_for_x_y_func(
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
#         map_mtx = _create_map_matrix_for_column(
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
    "create_point_heatmap_matrix",
    "get_coordinate_headers_resolution",
    "get_extent_resolution_coords_from_matrix",
    "is_flattened_geospatial_matrix",
    "rasterize_flattened_matrix",
    "rasterize_map_matrices"
]
