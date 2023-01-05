"""Module containing occurrence data wranglers for purging empty matrix slices."""
from logging import DEBUG

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
        # species_axis=None,
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
        # # Used only for reporting purposes when wrangling a PAM
        # self.species_axis = species_axis
        self.report['changes'] = {}

    # .......................
    def wrangle_matrix_bad(self, matrix):
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
                # TODO: Report which columns in a species axis were removed

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report['changes'][str(axis)]['purged'] += len(
                    np.where(matrix.sum(axis=tuple(sum_axes)) == 0)[0]
                )
                self.logger.log(
                    f"Purged {self.report['changes'][str(axis)]['purged']} " +
                    f"from axis {axis}.", refname=self.__class__.__name__,
                    log_level=DEBUG)
            else:
                axis_slice = list(range(matrix.shape[axis]))
            slices.append(axis_slice)

        return matrix.slice(*slices)


    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix with empty slices purged.

        Raises:
            Exception: on a matrix that is not 2-dimensions

        Notes:
            This works only on a 2d matrix, with axis 0 as sites, and axis 1 as species
        """
        slices = []
        if matrix.ndim != 2:
            msg = f"Cannot purge empty slices from a {matrix.ndim} dimensional matrix"
            self.report["errors"] = [msg]
            raise Exception(msg)

        if self.purge_axes is None:
            self.purge_axes = list(range(matrix.ndim))

        for axis in range(matrix.ndim):
            if axis in self.purge_axes:
                # Get axes and remove one we are working on
                sum_axes = list(range(matrix.ndim))
                sum_axes.remove(axis)
                # Sum of row or column <> 0
                condition = (matrix.sum(axis=tuple(sum_axes)) != 0)
                # Get the indices of the dimension where the condition is met
                # axis_slice = np.where(condition)[0]
                axis_slice = np.asarray(condition).nonzero()[0]
                # TODO: Report which columns in a species axis were removed
                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report['changes'][str(axis)]['purged'] += len(
                    np.where(matrix.sum(axis=tuple(sum_axes)) == 0)[0]
                )
                self.logger.log(
                    f"Purged {self.report['changes'][str(axis)]['purged']} " +
                    f"from axis {axis}.", refname=self.__class__.__name__,
                    log_level=DEBUG)
            else:
                axis_slice = list(range(matrix.shape[axis]))
            slices.append(axis_slice)

        return matrix.slice(*slices)