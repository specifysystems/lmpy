"""Module containing data wranglers for matching a matrix to a tree."""
from lmpy.tree import TreeWrapper

from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class MatchTreeMatrixWrangler(_MatrixDataWrangler):
    """Subset and reorder a matrix to match a tree."""
    name = 'MatchTreeMatrixWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        tree,
        species_axis,
        **params
    ):
        """Constructor for MatchTreeMatrixWrangler class.

        Args:
            tree (TreeWrapper or str): A tree object or file path to a tree.
            species_axis (int): The matrix axis with species names to match.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)

        if isinstance(tree, str):
            tree = TreeWrapper.from_filename(tree)
        self.tree = tree
        self.species_axis = species_axis
        self.report['changes'] = {}

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix subset to tree tip names.
        """
        slices = []
        for axis in range(matrix.ndim):
            if axis == self.species_axis:
                axis_slice = []
                axis_headers = matrix.get_headers(axis=str(axis))

                for taxon in self.tree.taxon_namespace:
                    if taxon.label in axis_headers:
                        axis_slice.append(axis_headers.index(taxon.label))

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report[
                    'changes'
                ][str(axis)]['purged'] += (len(axis_headers) - len(axis_slice))
            else:
                axis_slice = list(range(matrix.shape[axis]))

            slices.append(axis_slice)

        return matrix.slice(*slices)
