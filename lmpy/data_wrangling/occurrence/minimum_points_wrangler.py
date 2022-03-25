"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class MinimumPointsFilter(_OccurrenceDataWrangler):
    """Filter points if there are less than the specified number."""
    name = 'MinimumPointsFilter'

    # .......................
    def __init__(self, minimum_count, store_attribute=None):
        """Get an occurrence data wrangler for minimum points.

        Args:
            store_attribute (str or None): An attribute name to store assessment.
        """
        self.minimum_count = minimum_count
        _OccurrenceDataWrangler.__init__(self, store_attribute=store_attribute)

    # .......................
    def _get_all_pass_condition(self):
        def all_pass_condition(point):
            return True
        return all_pass_condition

    # .......................
    def _get_all_fail_condition(self):
        def all_fail_condition(point):
            return False
        return all_fail_condition

    # .......................
    def wrangle_points(self, points):
        if len(points) >= self.minimum_count:
            # Enough points, so all pass
            self.pass_condition = self._get_all_pass_condition()
        else:
            # Not enough points to all fail
            self.pass_condition = self._get_all_fail_condition()

        # Call parent class wrangle_points function
        return _OccurrenceDataWrangler.wrangle_points(self, points)
