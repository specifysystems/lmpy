"""Module containing common format occurrence data wrangler."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.point import Point


# .....................................................................................
class CommonFormatWrangler(_OccurrenceDataWrangler):
    """Modifies a point record using an attribute map."""
    # .......................
    def __init__(self, attribute_map):
        """CommonFormatWrangler constructor.

        Args:
            attribute_map (dict): A mapping of source key, target values.
        """
        self.attribute_map = attribute_map
        _OccurrenceDataWrangler.__init__(self)

    # .......................
    def _modify_point(point):
        """Update point attributes.

        Args:
            point (Point): A point to modify.

        Returns:
            Point, bool: Modified (if needed) point and boolean if point was modified.
        """
        new_pt = Point(
            point.species_name,
            point.x,
            point.y,
            attributes={
                new_name: point.get_attribute(old_name)
                for old_name, new_name in self.attribute_map.items()
            },
        )

        return new_pt, True
