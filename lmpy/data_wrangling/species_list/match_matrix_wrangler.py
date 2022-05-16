"""Module containing data wranglers for subsetting a species list to match a matrix."""
from lmpy.matrix import Matrix

from lmpy.data_wrangling.species_list.base import _SpeciesListDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class MatchMatrixSpeciesListWrangler(_SpeciesListDataWrangler):
    """Subsets a species list to match the species in the matrix."""
    name = 'MatchMatrixSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        matrix,
        species_axis,
        **params
    ):
        """Constructor for MatchMatrixSpeciesListWrangler class.

        Args:
            matrix (Matrix): A matrix to get taxon names to match.
            species_axis (int): The matrix axis with taxon names.
            **params (dict): Keyword parameters to pass to _SpeciesListDataWrangler.
        """
        _SpeciesListDataWrangler.__init__(self, **params)
        if isinstance(matrix, str):
            matrix = Matrix.load(matrix)
        self.keep_names = matrix.get_headers(axis=str(species_axis))

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Returns:
            SpeciesList: A species list intersected with the provided matrix.
        """
        ret_sl = SpeciesList(species_list.intersection(self.keep_names))
        self.report['removed'] = len(species_list) - len(ret_sl)
        self.log(f'removed {self.report["removed"]} tips.')
        return ret_sl
