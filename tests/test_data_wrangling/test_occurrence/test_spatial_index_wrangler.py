"""Test the spatial_index_wrangler module."""
from lmpy.data_wrangling.occurrence.spatial_index_wrangler import SpatialIndexFilter
from lmpy.spatial.spatial_index import create_geometry_from_bbox, SpatialIndex

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_sptial_index_filter():
    """Test the SptailIndexFilter occurrence data wrangler."""
    sp_index = SpatialIndex()
    sp_index.add_feature(
        1, create_geometry_from_bbox(-10, -10, 10, 10), {'att_1': 'val_1'}
    )

    species_choices = [f'Species {i}' for i in range(10)]

    intersections_map = {species: ['any'] for species in species_choices}

    # .......................
    def get_true(*args):
        """A dummy function that always returns True.

        Args:
            *args: A list of positional parameters.

        Returns:
            bool: Always return True.
        """
        return True

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(species_choices), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    wrangler = SpatialIndexFilter(sp_index, intersections_map, get_true)
    wrangled_points = wrangler.wrangle_points(points)

    # Only points within the (-10, -10, 10, 10) bounding box should be kept
    for pt in wrangled_points:
        assert -10 <= pt.x <= 10
        assert -10 <= pt.y <= 10
    assert len(wrangled_points) < len(points)
