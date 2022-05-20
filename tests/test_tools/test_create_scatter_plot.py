"""Test the create_scatter_plot tool."""
import json
import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools.create_scatter_plot import cli


# .....................................................................................
def test_create_scatter_plot_tool(monkeypatch, generate_temp_filename):
    """Test creating a scatter plot.

    Args:
        monkeypatch (pytest.Fixture): Fixture to monkeypatch running environment.
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    # Matrix to get scatter plot
    stat_matrix = Matrix(
        np.random.random(size=(6, 3),),
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
    matrix_filename = generate_temp_filename(suffix='.lmm')
    stat_matrix.write(matrix_filename)

    params = [
        'create_scatter_plot.py',
        '-t',
        'Some plot title',
        '--x_label',
        'A label for x-axis',
        '--y_label=y-axis label',
        '-s',
        json.dumps(dict(edgecolor='firebrick')),
        '--std_dev_style',
        json.dumps(dict(edgecolor='fuchsia', linestyle='--')),
        '--std_dev_style={"edgecolor": "blue", "linestyle": ":"}',
        plot_filename,
        matrix_filename,
        stat_matrix.get_column_headers()[1],
        stat_matrix.get_column_headers()[2],
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()
