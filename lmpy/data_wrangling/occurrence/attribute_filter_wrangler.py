"""Module containing attribute filter occurrence data wrangler."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class AttributeFilterWrangler(_OccurrenceDataWrangler):
    """Filters points according to a function."""
    name = 'AttributeFilterWrangler'
    version = '1.0'

    # .......................
    def __init__(self, attribute_name, filter_func, **params):
        """Constructor for AttributeModifierWrangler class.

        Args:
            attribute_name (str): The name of the attribute to modify.
            filter_func (Method): A function to be used for the pass condition.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.attribute_name = attribute_name
        _OccurrenceDataWrangler.__init__(self, **params)
        self._get_pass_condition_func(filter_func)

    # .......................
    def _get_pass_condition_func(self, filter_func):
        """Get the pass condition function.

        Args:
            filter_func (Method or dict): A method to use for pass condition.
        """
        if isinstance(filter_func, dict):
            if 'for-each' in filter_func.keys():
                condition = filter_func['for-each']['condition']
                if condition.lower() == 'not-in':
                    bad_values = filter_func['for-each']['values']

                    def _each_value_not_in(point):
                        return all(
                            [
                                val not in bad_values
                                for val in point.get_attribute(self.attribute_name)
                            ]
                        )

                    self._pass_condition = _each_value_not_in
        else:
            self._pass_condition = filter_func
