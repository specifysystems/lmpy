"""Module containing occurrence data wranglers for modifying point data."""
from lmpy.data_wrangling.base import DataWranglerInput
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
def get_accepted_name_map(accepted_name_map_or_filename):
    """Get the accepted name map from a dictionary or a filename."""
    accepted_name_map = {}
    with open(accepted_name_map_or_filename, mode='rt') as in_file:
        _ = next(in_file)
        for line in in_file:
            parts = line.split(',')
            accepted_name_map[parts[0].strip()] = parts[1].strip()
    return accepted_name_map


# .....................................................................................
class AcceptedNameModifier(_OccurrenceDataWrangler):
    """Modifies the species_name to the "accepted" taxon name for the species."""
    name = 'AcceptedNameOccurrenceWrangler'
    inputs.extend(
        [
            DataWranglerInput(
                'accepted_name_map',
                get_accepted_name_map,
                True,
                'Parameters for getting taxon name map.',
            ),
            DataWranglerInput(
                'store_original_attribute',
                str,
                False,
                'Attribute to store original value.',
            ),
       ]
    )

    # .......................
    def __init__(
        self,
        accepted_name_map,
        store_original_attribute=None,
        store_attribute=None,
        pass_value=0,
        fail_value=1
    ):
        """AcceptedNameModifier constructor.

        Args:
            accepted_name_map (dict): A map of original name to accepted name.
            store_original_attribute (str or None): A new attribute to store the
                original taxon name.
            store_attribute (str or None): A new attribute to store the assessed value.
            pass_value (Object): A value to store when the point passes assessment.
            fail_value (Object): A value to store when the point fails assessment.
        """
        if isinstance(accepted_name_map, dict):
            self.accepted_name_map = accepted_name_map
        else:
            self.accepted_name_map = get_accepted_name_map(accepted_name_map)
        self.store_original_attribute = store_original_attribute
        _OccurrenceDataWrangler.__init__(
            self,
            store_attribute=store_attribute,
            pass_value=pass_value,
            fail_value=fail_value
        )

    # .......................
    def _pass_condition(point):
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
    def _modify_point(point):
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
