"""Test teh coordinate_conversion_wrangler module."""
import numpy as np

from lmpy.data_wrangling.occurrence.coordinate_conversion_wrangler import (
    CoordinateConverterWrangler
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_coordinate_conversion():
    """Test coordinate conversion through multiple EPSGs."""
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-70.0, 70.0, 2, 6), 'float'),
        [SimulatedField('epsg', '', get_random_choice_func([4326]), 'int')]
    )

    wrangler_config = {
        'target_epsg': 3395,
        'epsg_attribute': 'epsg',
        'original_x_attribute': 'original_x',
        'original_y_attribute': 'original_y',
    }

    wrangler_to_3395 = CoordinateConverterWrangler.from_config(wrangler_config)

    wrangler_to_4326 = CoordinateConverterWrangler(4326, source_epsg=3395)

    # Convert to 3395
    wrangled_points_3395 = wrangler_to_3395.wrangle_points(points)

    # Convert back to 4326
    wrangled_points_4326 = wrangler_to_4326.wrangle_points(wrangled_points_3395)

    # Check each point and make sure values are close to the original
    for pt in wrangled_points_4326:
        print((pt.x, pt.get_attribute(wrangler_config['original_x_attribute'])))
        print((pt.y, pt.get_attribute(wrangler_config['original_y_attribute'])))
        assert np.isclose(
            pt.x, pt.get_attribute(wrangler_config['original_x_attribute'])
        )
        assert np.isclose(
            pt.y, pt.get_attribute(wrangler_config['original_y_attribute'])
        )

    assert len(points) == len(wrangled_points_4326)
