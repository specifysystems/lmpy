"""Tests for the bounding_box_wrangler module."""
from lmpy.data_wrangling.occurrence.bounding_box_wrangler import BoundingBoxFilter

from lmpy.point import Point

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_everything_inside():
    """Test the BoundingBoxFilter when all points should be within the bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            Point.SPECIES_ATTRIBUTE, '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField(
            Point.X_ATTRIBUTE, '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField(
            Point.Y_ATTRIBUTE, '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = BoundingBoxFilter(-180.0, -90.0, 180.0, 90.0)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == 0


# .....................................................................................
def test_everything_outside():
    """Test the BoundingBoxFilter when all points are outside of the bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            Point.SPECIES_ATTRIBUTE, '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField(
            Point.X_ATTRIBUTE, '', get_random_float_func(-180.0, 0.0, 2, 6), 'float'),
        SimulatedField(
            Point.Y_ATTRIBUTE, '', get_random_float_func(-90.0, 0.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = BoundingBoxFilter(1.0, 1.0, 180.0, 90.0)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == 0
    assert len(points) == 1000

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == len(points)


# .....................................................................................
def test_in_and_out():
    """Test the BoundingBoxFilter when points can be inside or outside of bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            Point.SPECIES_ATTRIBUTE, '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField(
            Point.X_ATTRIBUTE, '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField(
            Point.Y_ATTRIBUTE, '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler_config = {
        'min_x': -40.0,
        'min_y': -40.0,
        'max_x': 40.0,
        'max_y': 40.0,
        'store_attribute': 'assessed',
        'pass_value': 0,
        'fail_value': 1,
    }
    wrangler = BoundingBoxFilter.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)
    assert len(points) == 1000
    assert len(wrangled_points) > 0

    num_filtered = 0
    for pt in wrangled_points:
        if pt.get_attribute(
            wrangler_config['store_attribute']
        ) == wrangler_config['fail_value']:
            num_filtered += 1

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] < len(points)
    assert report['filtered'] == num_filtered
