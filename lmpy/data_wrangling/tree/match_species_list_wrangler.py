"""Module containing data wranglers for subsetting a tree to match a species list."""
from lmpy.species_list import SpeciesList

from lmpy.data_wrangling.tree.base import _TreeDataWrangler


# .....................................................................................
class MatchSpeciesListTreeWrangler(_TreeDataWrangler):
    """Subsets a tree to match the species in the species list."""
    name = 'MatchSpeciesListTreeWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        species_list,
        **params
    ):
        """Constructor for MatchSpeciesListTreeWrangler class.

        Args:
            species_list (SpeciesList): A species list to match.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _TreeDataWrangler.__init__(self, **params)
        if isinstance(species_list, str):
            species_list = SpeciesList.from_file(species_list)
        self.keep_taxon_names = list(species_list)

    # .......................
    def wrangle_tree(self, tree):
        """Wrangle a tree.

        Args:
            tree (TreeWrapper): A tree to wrangle.

        Returns:
            TreeWrapper: The subsetted tree.
        """
        original_taxa_count = len(tree.taxon_namespace)
        tree.retain_taxa_with_labels(self.keep_taxon_names)
        tree.purge_taxon_namespace()
        num_purged = original_taxa_count - len(tree.taxon_namespace)
        self._purged += num_purged
        self.log(f'removed {self._purged} tips.')
        return tree
