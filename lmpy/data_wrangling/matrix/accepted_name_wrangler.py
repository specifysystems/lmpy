"""Module containing occurrence data wranglers for modifying matrices."""
import numpy as np

from lmpy.data_wrangling.common.accepted_name_wrangler import (
    _AcceptedNameWrangler,
    resolve_names_gbif,
)
from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class AcceptedNameMatrixWrangler(_MatrixDataWrangler, _AcceptedNameWrangler):
    """Modifies matrix columns to update taxon names to the "accepted" names."""
    name = 'AcceptedNameMatrixWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        name_map=None,
        name_resolver=None,
        taxon_axis=1,
        purge_failures=True,
        out_map_filename=None,
        map_write_interval=100,
        out_map_format='json',
        **params
    ):
        """Constructor for AcceptedNameMatrixModifier class.

        Args:
            name_map (dict): A map of original name to accepted name.
            name_resolver (str or Method): If provided, use this method for getting new
                accepted names.  If set to 'gbif', use GBIF name resolution.
            taxon_axis (int): The axis with taxon headers.
            purge_failures (bool): Should failures be purged from the matrix.
            out_map_filename (str): A file location to write the updated name map.
            map_write_interval (int): Update the name map output file after each set of
                this many iterations.
            out_map_format (str): The format to write the names map (csv or json).
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)
        if isinstance(name_resolver, str) and name_resolver.lower() == 'gbif':
            name_resolver = resolve_names_gbif
        _AcceptedNameWrangler.__init__(
            self,
            name_map=name_map,
            name_resolver=name_resolver,
            out_map_filename=out_map_filename,
            map_write_interval=map_write_interval,
            out_map_format=out_map_format,
        )

        self.taxon_axis = taxon_axis
        self.purge_failures = purge_failures

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix with accepted taxon names.
        """
        failures = []
        headers = matrix.get_headers(axis=self.taxon_axis)
        for i, hdr in enumerate(headers):
            acc_name = self.resolve_names([hdr])[hdr]
            if acc_name is None:
                failures.append(i)
            elif hdr != acc_name:
                matrix.headers[str(self.taxon_axis)][i] = acc_name
                # report
                self._report_slice(self.taxon_axis, i, modified=True)

        # Set defaults for purged and modified
        purged = False
        modified = True

        # Should we purge?
        if self.purge_failures:
            new_headers = matrix.get_headers(str(self.taxon_axis))
            matrix = np.delete(matrix, failures, axis=self.taxon_axis)
            # Go through failures and pop each, reverse list to start at biggest to
            #     maintain indices
            for i in sorted(failures, reverse=True):
                new_headers.pop(i)
            matrix.set_headers(str(self.taxon_axis), new_headers)
            # Change purged and modified since we are removing items
            purged = True
            modified = False

        for i in failures:
            self._report_slice(self.taxon_axis, i, modified=modified, purged=purged)

        return matrix
