"""Test the minimum_points_wrangler module."""
from lmpy.data_wrangling.occurrence.minimum_points_wrangler import MinimumPointsFilter

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_minimum_points_filter_all():
    """Test the MinimumPointsFilter when there are less than the minimum."""
    points = generate_points(
        10,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MinimumPointsFilter(100)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == 0

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == len(points)


# .....................................................................................
def test_minimum_points_return_all():
    """Test the MinimumPointsFilter when there are more than the minimum."""
    points = generate_points(
        100,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler_config = {
        'minimum_count': 10
    }
    wrangler = MinimumPointsFilter.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == 0


# .....................................................................................
def test_minimum_points_assess_all_pass():
    """Test the MinimumPointsFilter when there are more than the minimum (assess)."""
    points = generate_points(
        100,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MinimumPointsFilter(10, store_attribute='assessed')
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == 0


# .....................................................................................
def test_minimum_points_assess_all_fail():
    """Test the MinimumPointsFilter when there are less than the minimum (assess)."""
    points = generate_points(
        10,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler_config = {
        'minimum_count': 100,
        'store_attribute': 'assessed',
        'pass_value': 0,
        'fail_value': 1,
    }
    wrangler = MinimumPointsFilter.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    num_filtered = 0
    for pt in wrangled_points:
        if pt.get_attribute(
            wrangler_config['store_attribute']
        ) == wrangler_config['fail_value']:
            num_filtered += 1

    # Get the report
    report = wrangler.get_report()
    assert num_filtered == report['filtered']
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == len(points)
