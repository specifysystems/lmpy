"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class MinimumPointsFilter(_OccurrenceDataWrangler):
    """Filter points if there are less than the specified number."""
    name = 'MinimumPointsWrangler'
    version = '1.0'

    # .......................
    def __init__(self, minimum_count, **params):
        """Get an occurrence data wrangler for minimum points.

        Args:
            minimum_count (int): The minimum number of points in order to keep all.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.minimum_count = minimum_count
        _OccurrenceDataWrangler.__init__(self, **params)

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
        """Wrangle points.  Return all or none based on how many are present.

        Args:
            points (list of Point): A list of points to assess.

        Returns:
            list of Point: Either an empty list or all of the points passed in.
        """
        if len(points) >= self.minimum_count:
            # Enough points, so all pass
            self._pass_condition = self._get_all_pass_condition()
        else:
            # Not enough points to all fail
            self._pass_condition = self._get_all_fail_condition()

        # Call parent class wrangle_points function
        return _OccurrenceDataWrangler.wrangle_points(self, points)
