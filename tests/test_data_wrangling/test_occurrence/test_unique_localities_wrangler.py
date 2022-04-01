"""Test the unique_localities_wrangler module."""
from copy import deepcopy

import numpy as np

from lmpy.data_wrangling.occurrence.unique_localities_wrangler import (
    UniqueLocalitiesFilter,
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_unique_localities_filter():
    """Test the UniqueLocalitiesFilter and remove duplicates."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Make some duplicates
    for idx in np.random.choice(range(len(points)), size=np.random.randint(10, 100)):
        points.append(deepcopy(points[idx]))

    # Wrangle points
    wrangler = UniqueLocalitiesFilter()
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) < len(points)
    assert len(wrangled_points) <= 1000  # Could be less if random duplicates

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] >= len(points) - len(wrangled_points)


# .....................................................................................
def test_unique_localities_filter_no_reset():
    """Test the UniqueLocalitiesFilter and remove duplicates with no reset."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Make some duplicates
    for idx in np.random.choice(range(len(points)), size=np.random.randint(10, 100)):
        points.append(deepcopy(points[idx]))

    # Wrangle points
    wrangler = UniqueLocalitiesFilter(do_reset=False)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) < len(points)
    assert len(wrangled_points) <= 1000  # Could be less if random duplicates

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] >= len(points) - len(wrangled_points)

    # Wrangle again without resetting (should return zero points)
    wrangled_points_2 = wrangler.wrangle_points(points)

    # Make sure no points are returned since they were already seen
    assert len(wrangled_points_2) == 0


# .....................................................................................
def test_unique_localities_assess():
    """Test the UniqueLocalitiesFilter and keep assessment of records."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Make some duplicates
    for idx in np.random.choice(range(len(points)), size=np.random.randint(10, 100)):
        points.append(deepcopy(points[idx]))

    # Wrangle points
    wrangler_config = {
        'store_attribute': 'assessed',
        'pass_value': 0,
        'fail_value': 1,
    }
    wrangler = UniqueLocalitiesFilter.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] >= len(points) - len(wrangled_points)
    assert report['filtered'] >= len(points) - len(wrangled_points)

    num_filtered = 0
    for pt in wrangled_points:
        if pt.get_attribute(
            wrangler_config['store_attribute']
        ) == wrangler_config['fail_value']:
            num_filtered += 1
