"""Module containing occurrence data wranglers for purging empty matrix slices."""
import numpy as np

from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class PurgeEmptySlicesWrangler(_MatrixDataWrangler):
    """Removes empty slices (rows, columns, other) from a matrix."""
    name = 'PurgeEmptySlicesWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        purge_axes=None,
        **params
    ):
        """Constructor for PurgeEmptySlicesWrangler class.

        Args:
            purge_axes (None, int, or list of int): Matrix axes to be processed.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)
        # Make purge_axes a list if it is not None
        if isinstance(purge_axes, int):
            purge_axes = [purge_axes]
        self.purge_axes = purge_axes
        self.report['changes'] = {}

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix with empty slices purged.
        """
        slices = []
        for axis in range(matrix.ndim):
            if self.purge_axes is None or axis in self.purge_axes:
                sum_axes = list(range(matrix.ndim))
                sum_axes.remove(axis)
                axis_slice = np.where(matrix.sum(axis=tuple(sum_axes)) != 0)[0]

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report['changes'][str(axis)]['purged'] += len(
                    np.where(matrix.sum(axis=tuple(sum_axes)) == 0)[0]
                )
                self.log('Purged {} from axis {}.'.format(
                    self.report['changes'][str(axis)]['purged'], axis)
                )
            else:
                axis_slice = list(range(matrix.shape[axis]))
            slices.append(axis_slice)

        return matrix.slice(*slices)
