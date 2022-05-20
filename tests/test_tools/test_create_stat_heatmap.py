"""Test the create_stat_heatmap tool."""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.tools.create_stat_heatmap import cli


# .....................................................................................
def test_create_stat_heatmap(monkeypatch, generate_temp_filename):
    """Test the create_stat_heatmap cli tool.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    plot_filename = generate_temp_filename(suffix='.png')
    matrix_filename = generate_temp_filename(suffix='.lmm')

    min_x, min_y, max_x, max_y = (-180.0, -90.0, 180.0, 90.0)
    resolution = .5

    # Simulate some data
    num_rows = 1000
    stats = ['Stat_1', 'Stat_2', 'Stat_3']
    matrix = Matrix(
        np.random.randint(0, 100, size=(num_rows, len(stats))),
        headers={
            '0': [
                (
                    i,
                    np.random.random() * (max_x - min_x) + min_x,
                    np.random.random() * (max_y - min_y) + min_y
                ) for i in range(num_rows)],
            '1': stats
        }
    )
    matrix.write(matrix_filename)
    stat = matrix.get_column_headers()[1]

    params = [
        'create_stat_heatmap.py',
        '--title',
        'Some plot title',
        plot_filename,
        matrix_filename,
        stat,
        str(min_x),
        str(min_y),
        str(max_x),
        str(max_y),
        str(resolution),
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()
