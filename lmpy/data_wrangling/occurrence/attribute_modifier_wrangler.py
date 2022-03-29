"""Module containing attribute modifier occurrence data wrangler."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class AttributeModifierWrangler(_OccurrenceDataWrangler):
    """Modifies a point attribute according to a function."""
    name = 'AttributeModifierWrangler'
    version = '1.0'

    # .......................
    def __init__(self, attribute_name, attribute_func, **params):
        """Constructor for AttributeModifierWrangler class.

        Args:
            attribute_name (str): The name of the attribute to modify.
            attribute_func (Method): A function to generate values for a point.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.attribute_name = attribute_name
        self.attribute_func = attribute_func
        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    def _modify_point(self, point):
        """Update point attributes.

        Args:
            point (Point): A point to modify.

        Returns:
            Point, bool: Modified point and boolean if point was modified.
        """
        point.set_attribute(self.attribute_name, self.attribute_func(point))

        return point, True
