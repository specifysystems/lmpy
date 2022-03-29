"""Module containing occurrence data wranglers for modifying point data."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
def get_accepted_name_map(name_map):
    """Get the accepted name map from a dictionary or a filename.

    Args:
        name_map (str or dict): A filename or mapping dictionary.

    Returns:
        dict: A mapping dictionary
    """
    if isinstance(name_map, dict):
        return name_map
    accepted_name_map = {}
    with open(name_map, mode='rt') as in_file:
        _ = next(in_file)
        for line in in_file:
            parts = line.split(',')
            accepted_name_map[parts[0].strip()] = parts[1].strip()
    return accepted_name_map


# .....................................................................................
class AcceptedNameWrangler(_OccurrenceDataWrangler):
    """Modifies the species_name to the "accepted" taxon name for the species."""
    name = 'AcceptedNameOccurrenceWrangler'
    version = '1.0'

    # .......................
    def __init__(self, accepted_name_map, store_original_attribute=None, **params):
        """Constructor for AcceptedNameModifier class.

        Args:
            accepted_name_map (dict): A map of original name to accepted name.
            store_original_attribute (str or None): A new attribute to store the
                original taxon name.
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        if isinstance(accepted_name_map, dict):
            self.accepted_name_map = accepted_name_map
        else:
            self.accepted_name_map = get_accepted_name_map(accepted_name_map)
        self.store_original_attribute = store_original_attribute
        _OccurrenceDataWrangler.__init__(self, **params)

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
        acc_name = ''
        is_modified = False
        if point.species_name in self.accepted_name_map.keys():
            acc_name = self.accepted_name_map[point.species_name]

        # If we should keep original, add a new attribute
        if self.store_original_attribute is not None:
            point.set_attribute(self.store_original_attribute, point.species_name)
            is_modified = True

        if point.species_name != acc_name:
            point.species_name = acc_name
            is_modified = True

        return point, is_modified
