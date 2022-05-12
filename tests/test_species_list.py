"""Simple tests for the species_list module."""
import numpy as np

from lmpy.species_list import SpeciesList


# .....................................................................................
def test_species_list():
    """Simple tests of SpeciesList to ensure that it behaves like a set."""
    list_a = SpeciesList([1, 2, 3])
    list_b = SpeciesList({4, 5, 6})
    list_c = SpeciesList([2, 4, 5])
    list_d = SpeciesList({1, 3, 6})
    assert list_a == set([1, 2, 3])
    assert list_b == {4, 5, 6}
    assert list_c == set([2, 4, 5])
    assert list_d == {1, 3, 6}
    assert list_a.union(list_b) == {1, 2, 3, 4, 5, 6}
    assert list_a.intersection(list_b) == set()
    assert list_a.intersection(list_c) == {2}
    assert list_b.union(list_c) == {2, 4, 5, 6}
    assert list_a.union({4, 5, 6}) == {1, 2, 3, 4, 5, 6}


# .....................................................................................
def test_species_list_from_file(generate_temp_filename):
    """Tests that a species list can be created from a file of species.

    Args:
        generate_temp_filename (pytest.Fixture): A fixture to generate filenames.
    """
    num_species = np.random.randint(5, 50)
    species_filename = generate_temp_filename(suffix='.txt')
    in_species_list = SpeciesList([f'Species {i}' for i in range(num_species)])
    in_species_list.write(species_filename)
    species_list = SpeciesList.from_file(species_filename)
    assert len(species_list) == num_species
