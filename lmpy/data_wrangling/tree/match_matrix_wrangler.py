"""Module containing data wranglers for subsetting a tree to match a matrix."""
from lmpy.matrix import Matrix

from lmpy.data_wrangling.tree.base import _TreeDataWrangler


# .....................................................................................
class MatchMatrixTreeWrangler(_TreeDataWrangler):
    """Subsets a tree to match the species in the matrix."""
    name = 'MatchMatrixTreeWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        matrix,
        species_axis,
        **params
    ):
        """Constructor for SubsetTreeWrangler class.

        Args:
            matrix (Matrix): A matrix to get taxon names to match.
            species_axis (int): The matrix axis with taxon names.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _TreeDataWrangler.__init__(self, **params)
        if isinstance(matrix, str):
            matrix = Matrix.load(matrix)
        self.keep_taxon_names = matrix.get_headers(axis=str(species_axis))

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
