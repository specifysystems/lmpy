"""Tests for the plots.scatter module."""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.plots.scatter import create_scatter_plot


# .....................................................................................
def test_create_stat_scatter_plot(generate_temp_filename):
    """Test creating a scatter plot.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    # Matrix to get scatter plot
    stat_matrix = Matrix(
        np.array(
            [
                [1, 2, 3],
                [1, 2, 3],
                [1, 2, 3],
                [1, 2, 3],
                [4, 5, 6],
                [7, 8, 9],
            ]
        ),
        headers={
            '0': [
                (0, 0.5, 0.5),
                (1, 0.5, 1.5),
                (2, 1.5, 0.5),
                (3, 1.5, 1.5),
                (4, 0.5, 0.5),
                (5, 0.5, 0.5),
            ],
            '1': ['stat_1', 'stat_2', 'stat_3']
        }
    )
    plot_filename = generate_temp_filename(suffix='.png')
    create_scatter_plot(
        plot_filename,
        stat_matrix[:, 1],
        stat_matrix[:, 2],
        title='Test Title',
        x_label='x label',
        y_label='y label',
        std_dev_styles=[
            dict(edgecolor='firebrick'),
            dict(edgecolor='fuchsia', linestyle='--'),
            dict(edgecolor='blue', linestyle=':'),
        ],
    )
