"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class UniqueLocalitiesFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for unique localities per species."""
    name = 'UniqueLocalitiesFilter'

    # .......................
    def __init__(self, do_reset=True, store_attribute=None):
        """Get an occurrence data wrangler unique localities for a group of points.

        Args:
            do_reset (bool): Reset the list of seen localities after each group.
            store_attribute (str or None): An attribute name to store assessment.
        """
        self.seen_localities = []
        self.do_reset = do_reset
        _OccurrenceDataWrangler.__init__(self, store_attribute=store_attribute)

    # .......................
    def _pass_condition(self, point):
        """Assess a point to see if it is unique spatially.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: An indication if the point is spatially unique.
        """
        test_val = (point.x, point.y)
        if test_val in self.seen_localities:
            return False
        self.seen_localities.append(test_val)
        return True

    # .......................
    def wrangle_points(self, points):
        """Wrangle points.

        Adds an optional reset step so the same filter can be used for many species.

        Args:
            points (list of Point): A list of points to wrangle.

        Returns:
            list of Point: A list of points with unique localities.
        """
        if self.do_reset:
            self.seen_localities = []
        return _OccurrenceDataWrangler.wrangle_points(self, points)

