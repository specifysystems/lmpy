"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class BoundingBoxFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by bounding box."""
    name = 'BoundingBoxFilter'
    version = '1.0'

    # .......................
    def __init__(self, min_x, min_y, max_x, max_y, **params):
        """Get an occurrence data wrangler for filtering by bounding box.

        Args:
            min_x (numeric): The minimum 'x' value for the bounding box.
            min_y (numeric): The minimum 'y' value for the bounding box.
            max_x (numeric): The maximum 'x' value for the bounding box.
            max_y (numeric): The maximum 'y' value for the bounding box.
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    def _pass_condition(self, point):
        """Pass condition for a point.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passed assessment.
        """
        return all(
            [self.min_x <= point.x <= self.max_x, self.min_y <= point.y <= self.max_y]
        )
