"""Module containing occurrence data wranglers for filtering points."""
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler
from lmpy.spatial import SpatialIndex


# .....................................................................................
class SpatialIndexFilter(_OccurrenceDataWrangler):
    """Spatial Index Filter Occurrence Data Wrangler."""
    name = 'SpatialIndexFilter'
    version = '1.0'

    # .......................
    def __init__(
        self,
        spatial_index,
        intersections_map,
        check_hit_func,
        **params,
    ):
        """A data wrangler to filter points using a spatial index.

        Args:
            spatial_index (SpatialIndex): A SpatialIndex object that can be searched.
            intersections_map (dict): A dictionary of species name keys and
                corresponding valid intersection values.
            check_hit_func (Method): A function that takes two arguments
                (search hit, valid intersections for a species) and returns a boolean
                indication if the hit should be counted.
            **params (dict): Extra parameters to be sent to the base class.
        """
        self.spatial_index = spatial_index
        if not isinstance(self.spatial_index, SpatialIndex):
            self.spatial_index = SpatialIndex(spatial_index)
        self.intersections_map = intersections_map
        self.check_hit_func = check_hit_func

        _OccurrenceDataWrangler.__init__(self, **params)

    # .......................
    def _pass_condition(self, point):
        """Assess a point to see if it passes the spatial index filter.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: Indication if the point passess the assessment.
        """
        if any(
            [
                point.species_name not in self.intersections_map.keys(),
                len(self.intersections_map[point.species_name]) == 0
            ]
        ):
            return True
        for hit in self.spatial_index.search(point.x, point.y).values():
            if self.check_hit_func(hit, self.intersections_map[point.species_name]):
                return True
        return False
