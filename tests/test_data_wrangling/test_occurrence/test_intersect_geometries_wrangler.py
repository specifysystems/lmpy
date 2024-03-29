"""Tests for the intersect_geometries_wrangler module."""
from lmpy.data_wrangling.occurrence.intersect_geometries_wrangler import (
    IntersectGeometriesFilter,
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_everything_inside():
    """Test the IntersectGeometriesFilter when all points within the bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = IntersectGeometriesFilter(
        [
            'POLYGON ((-180 -90, 180 -90, 180 90, -180 90, -180 -90))'
        ]
    )
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == 0


# .....................................................................................
def test_everything_outside():
    """Test the IntersectGeometriesFilter when all points are outside of the bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 0.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 0.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = IntersectGeometriesFilter(['POLYGON ((1 1, 180 1, 180 90, 1 90, 1 1))'])
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
    """Test the IntersectGeometriesFilter when points inside and outside of bounds."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler_config = {
        'geometry_wkts': [
            'POLYGON ((0 0, 180 0, 180 90, 0 90, 0 0))',
            'POLYGON ((-180 -90, 0 -90, 0 0, -180 0, -180 -90))'
        ],
        'store_attribute': 'assessed',
        'pass_value': 0,
        'fail_value': 1,
    }
    wrangler = IntersectGeometriesFilter.from_config(wrangler_config)
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
