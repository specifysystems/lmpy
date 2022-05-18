"""Module containing tools for creating maps."""
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
    num_rows = (max_y - min_y) // resolution
    num_cols = (max_x - min_x) // resolution
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
        r = min(num_rows - 1, max(0, int((max_y - y) // resolution)))
        c = min(num_cols - 1, max(0, int((x - min_x) // resolution)))
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
        for points in reader:
            for point in points:
                row, col = get_row_col_func(point.x, point.y)
                heatmap[row, col] += 1
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
def plot_matrix(plot_filename, heatmap_matrix, base_layer=None):
    """Plot the heatmap.
    """
    fig = plt.figure()
    if base_layer is not None:
        plt.imshow(base_layer)
    plt.imshow(heatmap_matrix)
    plt.savefig(plot_filename)


# .....................................................................................
__all__ = [
    'create_map_matrix',
    'create_point_heatmap_matrix',
    'create_stat_heatmap_matrix',
    'get_row_col_for_x_y_func',
]
