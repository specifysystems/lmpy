"""Test the accepted_name_wrangler module."""
import numpy as np

from lmpy.data_wrangling.occurrence.accepted_name_wrangler import (
    AcceptedNameOccurrenceWrangler,
)

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_accepted_name_wrangler():
    """Test the accepted_name_wrangler."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(20)
    }
    # Generate points
    points = generate_points(
        100,
        SimulatedField(
            'species_name', '', get_random_choice_func(list(name_map.keys())), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Wrangle points
    wrangler = AcceptedNameOccurrenceWrangler(name_map)
    wrangled_points = wrangler.wrangle_points(points)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for pt in wrangled_points:
        assert pt.species_name in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == 0


# .....................................................................................
def test_accepted_name_wrangler_unmatched_names():
    """Test the Accepted Name Wrangler with unmatched names."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(10)
    }
    raw_names = list(name_map.keys())
    raw_names.extend([f'Unmatched {i}' for i in range(10)])
    # Generate points
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(raw_names), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Wrangle points
    wrangler = AcceptedNameOccurrenceWrangler(name_map)
    wrangled_points = wrangler.wrangle_points(points)

    # Check that we removed some points
    assert len(wrangled_points) < len(points)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for pt in wrangled_points:
        assert pt.species_name in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] > 0


# .....................................................................................
def test_accepted_name_wrangler_store_original():
    """Test the accepted_name_wrangler while storing original name values."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(10)
    }
    raw_names = list(name_map.keys())
    raw_names.extend([f'Unmatched {i}' for i in range(10)])
    # Generate points
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(raw_names), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Wrangle points
    wrangler = AcceptedNameOccurrenceWrangler(
        name_map, store_original_attribute='original_name'
    )
    wrangled_points = wrangler.wrangle_points(points)

    # Check that we removed some points
    assert len(wrangled_points) < len(points)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for pt in wrangled_points:
        assert pt.species_name in accepted_names
        assert pt.get_attribute('original_name') in raw_names

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] > 0


# .....................................................................................
def test_accepted_name_wrangler_unmatched_names_dont_remove():
    """Test the accepted_name_wrangler with unmatched names, but don't remove them."""
    # Name map
    name_map = {
        f'Oldname {i}': 'Accepted {}'.format(np.random.randint(50)) for i in range(10)
    }
    raw_names = list(name_map.keys())
    raw_names.extend([f'Unmatched {i}' for i in range(10)])
    # Generate points
    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(raw_names), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Wrangle points
    wrangler = AcceptedNameOccurrenceWrangler(
        name_map, store_attribute='assessed', pass_value=0, fail_value=1
    )
    wrangled_points = wrangler.wrangle_points(points)

    # Check that we removed some points
    assert len(wrangled_points) == len(points)

    # Test that names are correct
    accepted_names = list(name_map.values())

    for pt in wrangled_points:
        # Check assessed value
        assessed_value = pt.get_attribute('assessed')
        if assessed_value == 1:
            assert pt.species_name is None or pt.species_name == ''
        else:
            assert pt.species_name in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] > 0


# .....................................................................................
def test_accepted_name_wrangler_from_config(generate_temp_filename):
    """Test the accepted_name_wrangler from a configuration dictionary.

    Args:
        generate_temp_filename (pytest.fixture): Fixture to generate filenames.
    """
    # Name map
    name_pairs = [
        ('Oldname a1', 'Newname a'),
        ('Oldname a2', 'Newname a'),
        ('Newname a', 'Newname a')
    ]
    raw_names = [i for i, _ in name_pairs]
    accepted_names = [j for _, j in name_pairs]

    temp_filename = generate_temp_filename(suffix='.csv')
    with open(temp_filename, mode='wt') as temp_out:
        temp_out.write('Name,Accepted name\n')
        for old_name, new_name in name_pairs:
            temp_out.write(f'{old_name},{new_name}\n')

    # Generate points
    points = generate_points(
        100,
        SimulatedField('species_name', '', get_random_choice_func(raw_names), 'str'),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )

    # Wrangler config
    wrangler_config = {
        'name_map': temp_filename,
        'store_original_attribute': 'original_name'
    }

    # Wrangle points
    wrangler = AcceptedNameOccurrenceWrangler.from_config(wrangler_config)
    wrangled_points = wrangler.wrangle_points(points)

    # Test that names are correct
    for pt in wrangled_points:
        assert pt.species_name in accepted_names

    # Get the report
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(points)
    assert report['filtered'] == 0
