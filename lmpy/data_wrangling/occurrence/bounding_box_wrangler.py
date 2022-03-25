"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler

# .....................................................................................
class BoundingBoxFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by bounding box."""
    name = 'BoundingBoxFilter'

    # .......................
    def __init__(self, min_x, min_y, max_x, max_y, store_attribute=None):
        """Get an occurrence data wrangler for filtering by bounding box.

        Args:
            min_x (numeric): The minimum 'x' value for the bounding box.
            min_y (numeric): The minimum 'y' value for the bounding box.
            max_x (numeric): The maximum 'x' value for the bounding box.
            max_y (numeric): The maximum 'y' value for the bounding box.
            store_attribute (str or None): An attribute name to store assessment.
        """
        _OccurrenceDataWrangler.__init__(self, store_attribute=store_attribute)

    # .......................
    def _pass_condition(point):
        """Pass condition for a point.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passed assessment.
        """
        return min_x <= point.x <= max_x and min_y <= point.y <= max_y
