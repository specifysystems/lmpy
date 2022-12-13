"""Module containing tools for creating plots."""
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np

from lmpy.spatial.map import get_extent_resolution_from_matrix


# .....................................................................................
def plot_matrix(
    matrix,
    plot_filename,
    base_layer=None,
    mask_val=0,
    title=None,
    cmap=None,
    vmin=None,
    vmax=None,
):
    """Plot the heatmap.

    Args:
        matrix (Matrix): A matrix of data (ordered like map grid)
            with latitude along the y/0 axis and longitude along the x/1 axis.
        plot_filename (str): A file path to write the output image.
        base_layer (str): A file location of a base layer map to add.
        mask_val (numeric): A numeric value in the heatmap to ignore when mapping.
        title (str): A title to add to the image.
        cmap (str or colormap): The color map to use for the heat map.
        vmin (numeric): The minimum value to use when scaling color.
        vmax (numeric): The maximum value to use when scaling color.
    """
    if vmax == -1:
        vmax = matrix.max()
    if vmin == -9999:
        vmin = matrix.min()
    min_x, min_y, max_x, max_y, x_res, y_res = get_extent_resolution_from_matrix(
        matrix)
    extent = (min_x, max_x, min_y, max_y)

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
        np.ma.masked_where(matrix == mask_val, matrix),
        **heatmap_layer_params
    )
    plt.savefig(plot_filename)


# .....................................................................................
__all__ = [
    'plot_matrix',
]
