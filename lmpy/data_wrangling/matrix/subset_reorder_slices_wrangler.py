"""Module containing data wranglers for subsetting and reordering matrix slices."""
from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class SubsetReorderSlicesWrangler(_MatrixDataWrangler):
    """Subsets and / or reorders matrix slices."""
    name = 'SubsetReorderSlicesWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        axes,
        **params
    ):
        """Constructor for PurgeEmptySlicesWrangler class.

        Args:
            axes (dict): A dictionary of axis keys (int or str of int) and list of
                values of those headers to keep.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)
        # Convert axis keys to integers
        self.slice_axes = {int(k): axes[k] for k in axes.keys()}
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
            if axis in self.slice_axes.keys():
                axis_slice = []
                axis_headers = matrix.get_headers(axis=str(axis))
                for idx in self.slice_axes[axis]:
                    # If the header is in the axis headers, append the index
                    if idx in axis_headers:
                        axis_slice.append(axis_headers.index(idx))

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report[
                    'changes'
                ][str(axis)]['purged'] += (len(axis_headers) - len(axis_slice))
                self.log('Purged {} from axis {}.'.format(
                    self.report['changes'][str(axis)]['purged'], axis)
                )
            else:
                axis_slice = list(range(matrix.shape[axis]))

            slices.append(axis_slice)

        return matrix.slice(*slices)
