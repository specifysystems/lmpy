"""Module containing Species List Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _SpeciesListDataWrangler(_DataWrangler):
    """Species List data wrangler base class."""
    name = '_SpeciesListDataWrangler'

    # .......................
    def __init__(self, **params):
        """Constructor for _SpeciesListDataWrangler base class.

        Args:
            **params (dict): Named parameters to pass to _DataWrangler base class.
        """
        _DataWrangler.__init__(self, **params)
        self.report['unresolved'] = 0
        self.report['duplicates'] = 0

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Raises:
            NotImplementedError: This method is not implemeneted for the base class.
        """
        raise NotImplementedError('wrangle_species_list not implemented on base class.')
