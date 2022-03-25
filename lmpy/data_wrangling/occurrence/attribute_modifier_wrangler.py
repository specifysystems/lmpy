"""Module containing attribute modifier occurrence data wrangler."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.point import Point


# .....................................................................................
class AttributeModifierWrangler(_OccurrenceDataWrangler):
    """Modifies a point attribute according to a function."""

    # .......................
    def __init__(self, attribute_name, attribute_func):
        """AttributeModifierWrangler constructor.

        Args:
            attribute_name (str): The name of the attribute to modify.
            attribute_func (Method): A function to generate values for a point.
        """
        self.attribute_name = attribute_name
        self.attribute_func = attribute_func
        _OccurrenceDataWrangler.__init__(self)

    # .......................
    def _modify_point(point):
        """Update point attributes.

        Args:
            point (Point): A point to modify.

        Returns:
            Point, bool: Modified point and boolean if point was modified.
        """
        point.set_attribute(self.attribute_name, self.attribute_func(point))

        return point, True
