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
        self.attribute_func = self._get_attribute_func(attribute_func)
        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    @staticmethod
    def _get_constant_func(val):
        """Get a function that returns a constant.

        Args:
            val (object): A constant value to return.

        Returns:
            Method: A method that returns a constant.
        """
        # .......................
        def const_func(_):
            """Return a constant.

            Returns:
                object: A constant value.
            """
            return val

        return const_func

    # .......................
    def _get_attribute_func(self, attribute_func):
        """Get the attribute function for generating values for a point.

        Args:
            attribute_func (Method or dict): A function or dictionary of parameters.

        Returns:
            Method: A method for getting attribute value.
        """
        if isinstance(attribute_func, dict) and 'constant' in attribute_func.keys():
            return self._get_constant_func(attribute_func['constant'])
        return attribute_func

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
