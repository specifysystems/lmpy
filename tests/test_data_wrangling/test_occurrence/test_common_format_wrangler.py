"""Tests the common_format_wrangler module."""
from lmpy.data_wrangling.occurrence.common_format_wrangler import CommonFormatWrangler

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_common_format_instance():
    """Test the CommonFormatWrangler."""
    att_map = {
        'in_name_a': 'out_name_a',
        'in_name_b': 'out_name_b',
        'in_name_c': 'out_name_c',
    }

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        [
            SimulatedField(
                fld_name,
                '',
                get_random_float_func(1, 100, 3, 5),
                'float'
            ) for fld_name in att_map.keys()
        ]
    )

    # Wrangle points
    wrangler = CommonFormatWrangler(att_map)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == 0

    # Check attributes
    for pt in wrangled_points:
        for att in att_map.keys():
            assert att not in pt.attributes.keys()
        for att in att_map.values():
            assert pt.get_attribute(att)


# .....................................................................................
def test_common_format_from_config():
    """Test the CommonFormatWrangler."""
    att_map = {
        'in_name_a': 'out_name_a',
        'in_name_b': 'out_name_b',
        'in_name_c': 'out_name_c',
    }

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(['Species A']), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        [
            SimulatedField(
                fld_name,
                '',
                get_random_float_func(1, 100, 3, 5),
                'float'
            ) for fld_name in att_map.keys()
        ]
    )

    # Wrangle points
    wrangler = CommonFormatWrangler.from_config({'attribute_map': att_map})
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == 0

    # Check attributes
    for pt in wrangled_points:
        for att in att_map.keys():
            assert att not in pt.attributes.keys()
        for att in att_map.values():
            assert pt.get_attribute(att)
