"""Test the decimal_precision_wrangler module."""
from lmpy.data_wrangling.occurrence.decimal_precision_wrangler import (
    DecimalPrecisionFilter,
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_decimal_precision_filter():
    """Test DecimalPrecisionFilter and filter out low-precision records."""
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
    wrangler_config = {'decimal_places': 4}
    wrangler = DecimalPrecisionFilter.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) < len(points)
    assert len(points) == 1000

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] < len(points)
    assert report['filtered'] > 0


# .....................................................................................
def test_decimal_precision_filter_assess():
    """Test DecimalPrecisionFilter and assess all records."""
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
    pass_value = 0
    fail_value = 1
    wrangler = DecimalPrecisionFilter(
        4, store_attribute='assessed', pass_value=pass_value, fail_value=fail_value
    )
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)
    assert len(points) == 1000

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] < len(points)
    assert report['filtered'] > 0

    num_filtered = 0
    for pt in wrangled_points:
        if pt.get_attribute('assessed') == fail_value:
            num_filtered += 1
    assert num_filtered == report['filtered']
