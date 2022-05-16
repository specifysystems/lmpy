"""Module containing data wranglers for subsetting a species list to match a tree."""
from lmpy.tree import TreeWrapper

from lmpy.data_wrangling.species_list.base import _SpeciesListDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class MatchTreeSpeciesListWrangler(_SpeciesListDataWrangler):
    """Subsets a species list to match the species in the tree."""
    name = 'MatchTreeSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        tree,
        **params
    ):
        """Constructor for MatchTreeSpeciesListWrangler class.

        Args:
            tree (TreeWrapper): A tree to match.
            **params (dict): Keyword parameters to pass to _SpeciesListDataWrangler.
        """
        _SpeciesListDataWrangler.__init__(self, **params)
        if isinstance(tree, str):
            tree = TreeWrapper.from_filename(tree)
        self.keep_names = [taxon.label for taxon in tree.taxon_namespace]

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Returns:
            SpeciesList: A species list intersected with the provided tree.
        """
        ret_sl = SpeciesList(species_list.intersection(self.keep_names))
        self.report['removed'] = len(species_list) - len(ret_sl)
        self.log(f'removed {self.report["removed"]} tips.')
        return ret_sl
