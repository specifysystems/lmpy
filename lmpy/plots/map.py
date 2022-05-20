"""Module containing tools for creating maps."""
import math

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from lmpy.matrix import Matrix


# .....................................................................................
def create_map_matrix(min_x, min_y, max_x, max_y, resolution):
    """Creates an empty matrix to use for mapping.

    Args:
        min_x (numeric): The minimum x value of the heatmap range.
        min_y (numeric): The minimum y value of the heatmap range.
        max_x (numeric): The maximum x value of the heatmap range.
        max_y (numeric): The maximum y value of the heatmap range.
        resolution (numeric): The size of each matrix cell.

    Returns:
        Matrix: A Matrix of zeros for the spatial extent.
    """
    num_rows = math.ceil((max_y - min_y) / resolution)
    num_cols = math.ceil((max_x - min_x) / resolution)
    map_matrix = Matrix(
        np.zeros((num_rows, num_cols), dtype=int),
        headers={
            '0': [max_y - (j + .5) * resolution for j in range(num_rows)],
            '1': [min_x + (i + .5) * resolution for i in range(num_cols)]
        }
    )
    return map_matrix


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
    """
    num_rows = (max_y - min_y) // resolution
    num_cols = (max_x - min_x) // resolution

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
    heatmap = create_map_matrix(min_x, min_y, max_x, max_y, resolution)
    get_row_col_func = get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution)

    if not isinstance(readers, list):
        readers = [readers]
    for reader in readers:
        reader.open()
        for points in reader:
            for point in points:
                row, col = get_row_col_func(point.x, point.y)
                heatmap[row, col] += 1
        reader.close()
    return heatmap


# .....................................................................................
def create_stat_heatmap_matrix(matrix, stat, min_x, min_y, max_x, max_y, resolution):
    """Create a matrix stat heatmap matrix.

    Args:
        matrix (Matrix): A matrix containing site rows and stat columns.
        stat (str): The column header of the stat to create the map for.
        min_x (numeric): The minimum x value of the heatmap range.
        min_y (numeric): The minimum y value of the heatmap range.
        max_x (numeric): The maximum x value of the heatmap range.
        max_y (numeric): The maximum y value of the heatmap range.
        resolution (numeric): The size of each matrix cell.

    Returns:
        Matrix: A matrix of point density.
    """
    heatmap = create_map_matrix(min_x, min_y, max_x, max_y, resolution)
    num_hits = Matrix(np.zeros(heatmap.shape))
    get_row_col_func = get_row_col_for_x_y_func(min_x, min_y, max_x, max_y, resolution)

    matrix_column = matrix.get_column_headers().index(stat)
    site_headers = matrix.get_row_headers()
    for matrix_row in range(matrix.shape[0]):
        _, x, y = site_headers[matrix_row]
        row, col = get_row_col_func(x, y)
        heatmap[row, col] += matrix[matrix_row, matrix_column]
        num_hits[row, col] += 1

    # Get the mean value by dividing by the number of hits
    return np.divide(heatmap, num_hits, where=num_hits > 0)


# .....................................................................................
def plot_matrix(
    plot_filename,
    heatmap_matrix,
    base_layer=None,
    extent=None,
    mask_val=0,
    title=None,
    cmap=None,
    vmin=None,
    vmax=None,
):
    """Plot the heatmap.

    Args:
        plot_filename (str): A file path to write the figure image.
        heatmap_matrix (Matrix): A matrix of heatmap data (ordered like map grid).
        base_layer (str): A file location of a base layer map to add.
        extent (tuple): Image extent as (min_x, max_x, min_y, max_y) tuple.
        mask_val (numeric): A numeric value in the heatmap to ignore when mapping.
        title (str): A title to add to the image.
        cmap (str or colormap): The color map to use for the heat map.
        vmin (numeric): The minimum value to use when scaling color.
        vmax (numeric): The maximum value to use when scaling color.
    """
    if vmax == -1:
        vmax = int(heatmap_matrix.max())
        vmin = 0
    base_layer_params = {k: v for k, v in dict(extent=extent).items() if v is not None}
    heatmap_layer_params = {
        k: v for k, v in dict(
            extent=extent,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
        ).items() if v is not None
    }
    fig = plt.figure()
    ax = fig.add_subplot()
    if title is not None:
        ax.axes.set_title(title)
    ax.axes.xaxis.set_visible(False)
    ax.axes.yaxis.set_visible(False)

    if base_layer is not None:
        if isinstance(base_layer, str):
            ax.imshow(mpimg.imread(base_layer), **base_layer_params)

    ax.imshow(
        np.ma.masked_where(heatmap_matrix == mask_val, heatmap_matrix),
        **heatmap_layer_params
    )
    plt.savefig(plot_filename)


# .....................................................................................
__all__ = [
    'create_map_matrix',
    'create_point_heatmap_matrix',
    'create_stat_heatmap_matrix',
    'get_row_col_for_x_y_func',
    'plot_matrix',
]
