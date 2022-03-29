"""Test the attribute_modifier_wrangler module."""
import numpy as np

from lmpy.data_wrangling.occurrence.attribute_modifier_wrangler import (
    AttributeModifierWrangler,
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_attribute_modifier_wrangler():
    """Test the AttributeModifierWrangler class."""
    # Test points
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # .......................
    def euclidean_distance_from_origin(point):
        """Return the Euclidean distance from the origin (0, 0) for the point.

        Args:
            point (Point): A point object to get distance for.

        Returns:
            float: The Euclidean distance from the origin.
        """
        return np.sqrt(pt.x**2 + pt.y**2)

    wrangler = AttributeModifierWrangler('distance', euclidean_distance_from_origin)
    wrangled_points = wrangler.wrangle_points()

    # Check that each point has the distance attribute and that it is correc
    for pt in wrangled_points:
        dist = pt.get_attribute('distance')
        assert np.isclose(dist, np.sqrt(pt.x**2 + pt.y**2))
