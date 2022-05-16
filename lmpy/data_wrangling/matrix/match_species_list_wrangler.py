"""Module containing data wranglers for matching a matrix to a species list."""
from lmpy.species_list import SpeciesList

from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class MatchSpeciesListMatrixWrangler(_MatrixDataWrangler):
    """Subset and reorder a matrix to match a species list."""
    name = 'MatchSpeciesListMatrixWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        species_list,
        species_axis,
        **params
    ):
        """Constructor for MatchSpeciesListMatrixWrangler class.

        Args:
            species_list (SpeciesList or str): A species list object or file path.
            species_axis (int): The matrix axis with species names to match.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)

        if isinstance(species_list, str):
            species_list = SpeciesList.from_file(species_list)
        self.species_list = species_list
        self.species_axis = species_axis
        self.report['changes'] = {}

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix subset to species list entries.
        """
        slices = []
        for axis in range(matrix.ndim):
            if axis == self.species_axis:
                axis_slice = []
                axis_headers = matrix.get_headers(axis=str(axis))

                for name in self.species_list:
                    if name in axis_headers:
                        axis_slice.append(axis_headers.index(name))

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {'purged': 0}
                self.report[
                    'changes'
                ][str(axis)]['purged'] += (len(axis_headers) - len(axis_slice))
                self.log('Purged {} species.'.format(
                    self.report['changes'][str(axis)]['purged'])
                )
            else:
                axis_slice = list(range(matrix.shape[axis]))

            slices.append(axis_slice)

        return matrix.slice(*slices)
