"""Module containing methods for creating scatterplots."""
from matplotlib.patches import Ellipse
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np


# .....................................................................................
def confidence_ellipse(x, y, ax, n_std=3.0, facecolor='none', **kwargs):
    """Create a plot of the covariance confidence ellipse of *x* and *y*.

    From: https://matplotlib.org/stable/gallery/statistics/confidence_ellipse.html

    Args:
        x (array-like): Input data for the x dimension.
        y (array-likez): Input data for the y dimension.
        ax (matplotlib.axes.Axes): The axes object to draw the ellipse into.
        n_std (float): The number of standard deviations to determine the ellipse's
            radius.
        facecolor (str): A color argument for the Ellipse.
        **kwargs (dict): Keyword parameters forwarded to Ellipse.

    Returns:
        Ellipse: A matplotlib Ellipse.

    Raises:
        ValueError: Raised if sizes of x and y are not the same.
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    # Using a special case to obtain the eigenvalues of this
    # two-dimensional dataset.
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    ellipse = Ellipse(
        (0, 0),
        width=ell_radius_x * 2,
        height=ell_radius_y * 2,
        facecolor=facecolor,
        **kwargs
    )

    # Calculating the standard deviation of x from
    # the square root of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)


# .....................................................................................
def create_scatter_plot(
    plot_filename,
    x_data,
    y_data,
    title=None,
    x_label=None,
    y_label=None,
    std_dev_styles=None,
    legend=True
):
    """Create a scatter plot for two data vectors with optional std dev ellipses.

    Args:
        plot_filename (str): A file path to write the plot image.
        x_data (array-like): Input data for the x dimension.
        y_data (array-like): Input data for the y dimension.
        title (str): A title to add to the plot.
        x_label (str): A label for the x-axis of the plot.
        y_label (str): A label for the y-axis of the plot.
        std_dev_styles (list of dict): A list of dictionaries of keyword arguments to
            use for stylize each confidence ellipse.  A confidence of ellipse will be
            added for each dictionary.
        legend (bool): Should a legend be added to the image.
    """
    scatter_args = dict(c='#0000ff', zorder=1, s=10)
    fig, axs = plt.subplots(1, 1)

    if std_dev_styles is not None:
        for i, style_dict in enumerate(std_dev_styles):
            confidence_ellipse(
                x_data, y_data, axs, n_std=i+1, label=rf'${i}\sigma$', **style_dict
            )

    axs.scatter(x_data, y_data, **scatter_args)

    if title is not None:
        axs.set_title(title)
    if x_label is not None:
        axs.set_xlabel(x_label)
    if y_label is not None:
        axs.set_ylabel(y_label)

    if legend:
        axs.legend()

    plt.savefig(plot_filename)
    fig.clear()


# .....................................................................................
__all__ = ['confidence_ellipse', 'create_scatter_plot']
