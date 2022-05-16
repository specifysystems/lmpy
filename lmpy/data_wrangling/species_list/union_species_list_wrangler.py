"""Module containing species data wranglers for creating a union species list."""
from lmpy.data_wrangling.species_list.base import _SpeciesListDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class UnionSpeciesListWrangler(_SpeciesListDataWrangler):
    """Modifies a species list by creating a union with another."""
    name = 'UnionSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        species_list,
        **params
    ):
        """Constructor for UnionSpeciesListModifier class.

        Args:
            species_list (SpeciesList): The species list to union with.
            **params (dict): Keyword parameters to pass to _TreeDataWrangler.
        """
        if isinstance(species_list, str):
            species_list = SpeciesList.from_file(species_list)
        self.other_species_list = species_list
        _SpeciesListDataWrangler.__init__(self, **params)

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Returns:
            SpeciesList: A species list union with the provided species list.
        """
        ret_sl = SpeciesList(species_list.union(self.other_species_list))
        self.report['added'] = len(ret_sl) - len(species_list)
        self.log(f'added {self.report["added"]} tips.')
        return ret_sl
