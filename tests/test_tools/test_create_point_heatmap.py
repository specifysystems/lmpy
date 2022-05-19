"""Test the create_point_heatmap tool."""
import numpy as np

from lmpy.point import Point, PointCsvReader, PointCsvWriter
from lmpy.tools.create_point_heatmap import cli


# .....................................................................................
def test_create_point_heatmap(monkeypatch, generate_temp_filename):
    """Test the create_point_heatmap cli tool.

    Args:
        monkeypatch (pytest.Fixture): A pytest fixture for monkeypatching.
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    points_filename = generate_temp_filename(suffix='.csv')
    plot_filename = generate_temp_filename(suffix='.png')

    num_points = 100000
    min_x, min_y, max_x, max_y = (-180.0, -90.0, 180.0, 90.0)
    resolution = .5
    buffer = 3
    img_extent = (min_x, max_x, min_y, max_y)

    # Simulate some data
    last_x = np.random.random() * (max_x - min_x) + min_x
    last_y = np.random.random() * (max_y - min_y) + min_y
    with PointCsvWriter(points_filename, ['species_name', 'x', 'y']) as writer:
        for _ in range(num_points):
            writer.write_points(
                [
                    Point(
                        'Species A',
                        last_x,
                        last_y,
                    )
                ]
            )
            last_x = max(min_x, min(np.random.random() * (2 * buffer) + (last_x - buffer), max_x))
            last_y = max(min_y, min(np.random.random() * (2 * buffer) + (last_y - buffer), max_y))

    params = [
        'create_point_heatmap.py',
        '--csv',
        points_filename,
        'species_name',
        'x',
        'y',
        '--title',
        'Some plot title',
        plot_filename,
        str(min_x),
        str(min_y),
        str(max_x),
        str(max_y),
        str(resolution),
    ]

    monkeypatch.setattr('sys.argv', params)
    cli()
