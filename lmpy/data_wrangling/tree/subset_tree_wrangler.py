"""Module containing data wranglers for subsetting a tree."""
from lmpy.data_wrangling.tree.base import _TreeDataWrangler


# .....................................................................................
class SubsetTreeWrangler(_TreeDataWrangler):
    """Subsets a tree."""
    name = 'SubsetTreeWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        keep_taxa,
        **params
    ):
        """Constructor for SubsetTreeWrangler class.

        Args:
            keep_taxa (list of str): A list of taxon names to keep.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _TreeDataWrangler.__init__(self, **params)
        self.keep_taxon_names = keep_taxa

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
        self._purged += (original_taxa_count - len(tree.taxon_namespace))
        self.log(f'removed {self._purged} tips.')
        return tree
