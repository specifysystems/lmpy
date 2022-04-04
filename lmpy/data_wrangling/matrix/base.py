"""Module containing Matrix Data Wrangler base class."""
import numpy as np

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
        _DataWrangler(self, **params)

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
    def wrangle_axis(self, matrix, axis, wrangle_func, purge_failures=True):
        """Wrangle a matrix axis.

        Args:
            matrix (Matrix): The matrix to wrangle.
            axis (int): The axis to wrangle.
            wrangle_func (Method): A function that takes a header and a matrix slice
                and returns a boolean.
            purge_failures (bool): Should failures be purged from the matrix.

        Returns:
            Matrix: A wrangled matrix.
        """
        headers = matrix.get_headers(axis=axis)
        failures = []

        for i, vals in enumerate(np.rollaxis(axis)):
            if not wrangle_func(headers[i], vals):
                failures.append(i)

        # Handle failures
        if purge_failures:
            # Purge failures
            matrix = np.delete(matrix, failures, axis=axis)
        return matrix

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
