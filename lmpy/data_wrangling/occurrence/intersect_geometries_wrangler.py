"""Module containing occurrence data wranglers for filtering points."""
from osgeo import ogr
from lmpy.data_wrangling.occurrence.base import _OccurrenceDataWrangler


# .....................................................................................
class IntersectGeometriesFilter(_OccurrenceDataWrangler):
    """Get an occurrence data wrangler for filtering by intersect geometries."""
    name = 'IntersectGeometriesFilter'
    version = '1.0'

    # .......................
    def __init__(self, geometry_wkts, **params):
        """Get an occurrence data wrangler for filtering by intersecting geometries.

        Args:
            geometry_wkts (list of str): A list of WKT strings.
            **params (dict): Keyword parameters to pass to _OccurrenceDataWrangler.
        """
        _OccurrenceDataWrangler.__init__(self, **params)
        self.geometries = []
        for wkt in geometry_wkts:
            self.geometries.append(ogr.CreateGeometryFromWkt(wkt))

    # .......................
    def _pass_condition(self, point):
        """Assessment function for a point.

        Args:
            point (Point): A point object to assess.

        Returns:
            bool: An indication if a point passed assessment.
        """
        point_geometry = ogr.Geometry(ogr.wkbPoint)
        point_geometry.AddPoint(point.x, point.y)
        return any(
            [
                not geom.Intersection(point_geometry).IsEmpty()
                for geom in self.geometries
            ]
        )
