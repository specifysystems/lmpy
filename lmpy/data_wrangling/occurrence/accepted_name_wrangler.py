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
        out_map_filename=None,
        map_write_interval=100,
        out_map_format='json',
        **params
    ):
        """Constructor for AcceptedNameModifier class.

        Args:
            name_map (dict or str): A map of original name to accepted name.
            name_resolver (str or Method): If provided, use this method for getting new
                accepted names.  If set to 'gbif', use GBIF name resolution.
            store_original_attribute (str or None): A new attribute to store the
                original taxon name.
            out_map_filename (str): A file location to write the updated name map.
            map_write_interval (int): Update the name map output file after each set of
                this many iterations.
            out_map_format (str): The format to write the names map (csv or json).
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        _OccurrenceDataWrangler.__init__(self, **params)

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
