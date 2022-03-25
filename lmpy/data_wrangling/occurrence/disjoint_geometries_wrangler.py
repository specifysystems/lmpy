"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.spatial import SpatialIndex


# .....................................................................................
class DisjointGeometriesFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by disjoint geometries."""
    name = 'DisjointGeometriesFilter'

    # .......................
    def __init__(self, geometry_wkts, store_attribute=None):
        """Get an occurrence data wrangler for filtering by disjoint geometries.

        Args:
            geometry_wkts (list of str): A list of geometry WKTs to check against.
            store_attribute (str or None): An attribute name to store assessment.
        """
        _OccurrenceDataWrangler.__init__(self, store_attribute=store_attribute)
        self.geom_index = SpatialIndex()
        i = 0
        for wkt in geometry_wkts:
            self.geom_index.add_feature(i, wkt, {"feature_id": i})
            i += 1

    # .......................
    def _pass_condition(self, point):
        """Assesment of a point to see if it passes the condition.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passes assessment.
        """
        hits = self.geom_index.search(point.x, point.y)
        return not bool(hits)
