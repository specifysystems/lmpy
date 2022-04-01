"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class UniqueLocalitiesFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for unique localities per species."""
    name = 'UniqueLocalitiesFilter'
    version = '1.0'

    # .......................
    def __init__(self, do_reset=True, **params):
        """Get an occurrence data wrangler unique localities for a group of points.

        Args:
            do_reset (bool): Reset the list of seen localities after each group.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.seen_localities = []
        # JSON may make boolean into a string so handle that
        if isinstance(do_reset, str):
            do_reset = do_reset.lower() != 'false'
        self.do_reset = bool(do_reset)
        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    def _pass_condition(self, point):
        """Assess a point to see if it is unique spatially.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: An indication if the point is spatially unique.
        """
        test_val = (point.species_name, point.x, point.y)
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
