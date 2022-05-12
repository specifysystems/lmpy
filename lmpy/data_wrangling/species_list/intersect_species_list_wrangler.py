"""Module containing species data wranglers for creating a intersect species list."""
from lmpy.data_wrangling.species_list.base import _SpeciesListDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class IntersectionSpeciesListWrangler(_SpeciesListDataWrangler):
    """Modifies a species list by creating an intersection with another."""
    name = 'IntersectionSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        species_list,
        **params
    ):
        """Constructor for IntersectionSpeciesListModifier class.

        Args:
            species_list (SpeciesList): The species list to intersect with.
            **params (dict): Keyword parameters to pass to _TreeDataWrangler.
        """
        self.other_species_list = species_list
        _SpeciesListDataWrangler.__init__(self, **params)

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Returns:
            SpeciesList: A species list intersected with the provided species list.
        """
        return species_list.intersection(self.other_species_list)
