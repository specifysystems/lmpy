"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.spatial import SpatialIndex


# .....................................................................................
class SpatialIndexFilter(_OccurrenceDataWrangler):
    """Spatial Index Filter Occurrence Data Wrangler."""
    name = 'SpatialIndexFilter'

    # .......................
    def __init__(
        self,
        spatial_index,
        intersections_map,
        check_hit_func,
        store_attribute=None
    ):
        self.spatial_index = spatial_index
        if not isinstance(self.spatial_index, SpatialIndex):
            self.spatial_index = SpatialIndex(spatial_index)
        self.intersections_map = intersections_map
        self.check_hit_func = check_hit_func

        _OccurrenceDataWrangler.__init__(self, store_attribute=store_attribute)

    # .......................
    def _pass_condiation(self, point):
        """Assess a point to see if it passes the spatial index filter.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passess the assessment.
        """
        if point.species_name not in self.intersections_map.keys() \
            or len(self.intersections_map[point.species_name]) == 0
        :
            return True
        for hit in self.spatial_index.search(point.x, point.y).values():
            if self.check_hit_func(hit, self.intersections_map[point.species_name]):
                return True
        return False
