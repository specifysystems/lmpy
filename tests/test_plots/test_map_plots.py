"""Tests for the plots.map module."""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.plots.map import (
    create_point_heatmap_matrix,
    create_stat_heatmap_matrix,
    plot_matrix,
)
from lmpy.point import Point, PointCsvReader, PointCsvWriter


# .....................................................................................
def test_create_point_heatmap_matrix_known_data(generate_temp_filename):
    """Test creating a matrix heatmap from a point reader.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    # Generate and write points
    point_filename = generate_temp_filename(suffix='.csv')
    points = [
        Point('Species A', 1, 3),
        Point('Species A', 2, 3),
        Point('Species A', 1.25, 3.5),
        Point('Species A', 3, 2),
        Point('Species A', 4, 1),
        Point('Species A', 5, 0.3),
        Point('Species A', 5.9, 5.4),
        Point('Species A', 0.1, 4.5),
        Point('Species A', 1.1, 5),
        Point('Species A', 2.3, 3.5),
        Point('Species A', 1, 3),
    ]
    with PointCsvWriter(point_filename, ['species_name', 'x', 'y']) as writer:
        writer.write_points(points)

    # Open point reader
    reader = PointCsvReader(point_filename, 'species_name', 'x', 'y')
    reader.open()

    # Create heat map
    heatmap = create_point_heatmap_matrix(reader, 0, 0, 6, 6, 2)
    reader.close()

    # Test that the heat map looks like what we expect
    test_heatmap = Matrix(
        np.array(
            [
                [2, 0, 1],
                [3, 2, 0],
                [0, 1, 2]
            ]
        ),
        headers={
            '0': [1, 3, 5],
            '1': [1, 3, 5]
        }
    )
    assert np.all(test_heatmap == heatmap)


# .....................................................................................
def test_create_point_heatmap_matrix_random_data(generate_temp_filename):
    """Test creating a matrix heatmap from a point reader.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    # Generate and write points
    point_filename = generate_temp_filename(suffix='.csv')
    num_points = np.random.randint(20, 1000)
    with PointCsvWriter(point_filename, ['species_name', 'x', 'y']) as writer:
        for _ in range(num_points):
            writer.write_points(
                [
                    Point(
                        'Species A',
                        np.random.randint(1, 99),
                        np.random.randint(1, 99)
                    )
                ]
            )

    # Open point reader
    reader = PointCsvReader(point_filename, 'species_name', 'x', 'y')
    reader.open()

    # Create heat map
    heatmap = create_point_heatmap_matrix(reader, 0, 0, 100, 100, 2)
    reader.close()

    assert heatmap.sum() == num_points


# .....................................................................................
def test_create_stat_heatmap_matrix():
    """Test creating a statistic heatmap."""
    # Matrix to get heatmap for
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
    stat_heatmap = create_stat_heatmap_matrix(stat_matrix, 'stat_2', 0, 0, 2, 2, 1)
    test_heatmap_matrix = Matrix(
        np.array(
            [
                [2, 2],
                [5, 2]
            ],
        ),
        headers={
            '0': [0.5, 1.5],
            '1': [0.5, 1.5]
        }
    )

    assert np.all(stat_heatmap == test_heatmap_matrix)


# .....................................................................................
def test_plot_matrix_points(generate_temp_filename):
    """Test the plot_matrix function with points.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    # Generate and write points
    point_filename = generate_temp_filename(suffix='.csv')
    num_points = np.random.randint(20, 1000)
    with PointCsvWriter(point_filename, ['species_name', 'x', 'y']) as writer:
        for _ in range(num_points):
            writer.write_points(
                [
                    Point(
                        'Species A',
                        np.random.randint(1, 99),
                        np.random.randint(1, 99)
                    )
                ]
            )

    # Open point reader
    reader = PointCsvReader(point_filename, 'species_name', 'x', 'y')
    reader.open()

    # Create heat map
    heatmap = create_point_heatmap_matrix(reader, 0, 0, 100, 100, 2)
    reader.close()

    plot_filename = generate_temp_filename(suffix='.png')
    plot_matrix(plot_filename, heatmap)
