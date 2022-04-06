"""Module containing Matrix Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _MatrixDataWrangler(_DataWrangler):
    """Matrix data wrangler base class."""
    name = '_MatrixDataWrangler'

    # .......................
    def __init__(self, **params):
        """Constructor for _MatrixDataWrangler base class.

        Args:
            **params (dict): Named parameters to pass to _DataWrangler base class.
        """
        _DataWrangler.__init__(self, **params)
        self.report['changes'] = {}

    # .......................
    def _report_slice(self, axis, idx, modified=False, purged=False):
        """Report what is done on a matrix slice.

        Args:
            axis (int): The axis of the interaction.
            idx (int): The index of the interaction.
            modified (bool): Was the slice modified.
            purged (bool): Was the slice purged.
        """
        if str(axis) not in self.report['changes']:
            self.report['changes'][str(axis)] = {
                'axis': axis,
                'modified': 0,
                'purged': 0
            }
        if modified:
            self.report['changes'][str(axis)]['modified'] += 1

        if purged:
            self.report['changes'][str(axis)]['purged'] += 1

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Raises:
            NotImplementedError: This method is not implemeneted for the base class.
        """
        raise NotImplementedError('wrangle_matrix not implemented on base class.')

    # .......................
    def reorder(self, matrix, *axes_order):
        """Reorder / subset a matrix for a number of dimensions.

        Args:
            matrix (Matrix): A matrix to reorder.
            *axes_order (list of iterables): Iterables for each dimension of a matrix
                to reorder / subset.

        Returns:
            Matrix: A reordered and / or subset matrix.
        """
        return matrix.slice(*axes_order)
