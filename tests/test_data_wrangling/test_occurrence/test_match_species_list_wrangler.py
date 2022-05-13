"""Tests the match_species_list_wrangler module."""
import numpy as np

from lmpy.data_wrangling.occurrence.match_species_list_wrangler import (
    MatchSpeciesListWrangler,
)
from lmpy.species_list import SpeciesList

from tests.data_simulator import (
    generate_points,
    get_random_choice_func,
    get_random_float_func,
    SimulatedField,
)


# .....................................................................................
def test_subset_with_species_list_filter():
    """Tests that subsetting Point lists works correctly from a species list."""
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(all_species), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MatchSpeciesListWrangler(species_list)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) < len(points)

    # Assert report values make sense
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == len(points) - len(wrangled_points)


# .....................................................................................
def test_subset_with_species_list_filter_store():
    """Tests that subsetting Point lists works correctly from a species list."""
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(all_species), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MatchSpeciesListWrangler(species_list, store_attribute='would_filter')
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Assert report values make sense
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(wrangled_points)
    assert report['filtered'] > 0


# .....................................................................................
def test_subset_with_species_list_filename_filter(generate_temp_filename):
    """Tests that subsetting Point lists works correctly from a species list.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture for generating filenames.
    """
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])
    species_list_filename = generate_temp_filename(suffix='.txt')
    species_list.write(species_list_filename)

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(all_species), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MatchSpeciesListWrangler(species_list_filename)
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) < len(points)

    # Assert report values make sense
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == 0
    assert report['filtered'] == len(points) - len(wrangled_points)


# .....................................................................................
def test_subset_with_species_list_filename_filter_store(generate_temp_filename):
    """Tests that subsetting Point lists works correctly from a species list.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture for generating filenames.
    """
    # All species
    all_species = [f'Species {i}' for i in range(100)]
    # Shuffle species for selection in matrix
    np.random.shuffle(all_species)
    species_list = SpeciesList(all_species[:np.random.randint(51, 75)])
    species_list_filename = generate_temp_filename(suffix='.txt')
    species_list.write(species_list_filename)

    points = generate_points(
        1000,
        SimulatedField(
            'species_name', '', get_random_choice_func(all_species), 'str'
        ),
        SimulatedField('x', '', get_random_float_func(-180.0, 180.0, 2, 6), 'float'),
        SimulatedField('y', '', get_random_float_func(-90.0, 90.0, 2, 6), 'float'),
        []
    )
    # Wrangle points
    wrangler = MatchSpeciesListWrangler(
        species_list_filename,
        store_attribute='would_filter'
    )
    wrangled_points = wrangler.wrangle_points(points)

    assert len(wrangled_points) == len(points)

    # Assert report values make sense
    report = wrangler.get_report()
    assert report['assessed'] == len(points)
    assert report['modified'] == len(wrangled_points)
    assert report['filtered'] > 0
