"""Module containing occurrence data wranglers for matching a species list."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class MatchSpeciesListWrangler(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by a species list."""
    name = 'OccurrenceSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(self, species_list, **params):
        """Get an occurrence data wrangler for filtering by bounding box.

        Args:
            species_list (SpeciesList): A species list to match against.
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        _OccurrenceDataWrangler.__init__(self, **params)
        if isinstance(species_list, str):
            species_list = SpeciesList.from_file(species_list)
        self.species_list = species_list

    # .......................
    def _pass_condition(self, point):
        """Pass condition for a point.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passed assessment.
        """
        return point.species_name in self.species_list
