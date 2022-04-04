"""Module containing occurrence data wranglers for modifying point data."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.data_wrangling.common.accepted_name_wrangler import (
    _AcceptedNameWrangler,
    resolve_names_gbif,
)


# .....................................................................................
class AcceptedNameOccurrenceWrangler(_OccurrenceDataWrangler, _AcceptedNameWrangler):
    """Modifies the species_name to the "accepted" taxon name for the species."""
    name = 'AcceptedNameOccurrenceWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        name_map=None,
        name_resolver=None,
        store_original_attribute=None,
        **params
    ):
        """Constructor for AcceptedNameModifier class.

        Args:
            name_map (dict): A map of original name to accepted name.
            name_resolver (str or Method): If provided, use this method for getting new
                accepted names.  If set to 'gbif', use GBIF name resolution.
            store_original_attribute (str or None): A new attribute to store the
                original taxon name.
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        _OccurrenceDataWrangler.__init__(self, **params)

        if isinstance(name_resolver, str) and name_resolver.lower() == 'gbif':
            name_resolver = resolve_names_gbif
        _AcceptedNameWrangler.__init__(
            self,
            name_map=name_map,
            name_resolver=name_resolver
        )

        self.store_original_attribute = store_original_attribute

    # .......................
    def _pass_condition(self, point):
        """Determine if a point has an accepted name.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: An indication if the point passed the test.
        """
        if point.species_name is None or len(point.species_name) == 0:
            return False
        return True

    # .......................
    def _modify_point(self, point):
        """Update taxon name if necessary.

        Args:
            point (Point): A point to modify.

        Returns:
            Point, bool: Modified (if needed) point and boolean if point was modified.
        """
        is_modified = False
        acc_name = self.resolve_names([point.species_name])[point.species_name]

        # If we should keep original, add a new attribute
        if self.store_original_attribute is not None:
            point.set_attribute(self.store_original_attribute, point.species_name)
            is_modified = True

        if point.species_name != acc_name:
            point.species_name = acc_name
            is_modified = True

        return point, is_modified
