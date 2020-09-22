"""Module containing a class for working with a spatial index.

Version 1: Store geometries in memory in table.  Save as wkt.
"""
import json
import os
from osgeo import ogr
import rtree


# .............................................................................
def create_geometry_from_bbox(min_x, min_y, max_x, max_y):
    """Create a geometry from a bounding box."""
    wkt = 'POLYGON (({0} {1}, {0} {3}, {2} {3}, {2} {1}, {0} {1}))'.format(
        min_x, min_y, max_x, max_y)
    return ogr.CreateGeometryFromWkt(wkt)


# .............................................................................
def quadtree_index(geom, bbox, min_size, depth_left):
    """Use a quadtree approach to gather spatial index data."""
    # min_x, min_y, max_x, max_y = bbox
    test_geom = create_geometry_from_bbox(*bbox)
    intersection = geom.Intersection(test_geom)
    min_x, max_x, min_y, max_y = intersection.GetEnvelope()
    if min_x == max_x or min_y == max_y:
        return []
    # if intersection.Equals(test_geom):
    if intersection.Area() < min_size:
        return [(bbox, intersection)]
    if intersection.Area() == test_geom.Area():
        return [(bbox, True)]
    ret = []
    if depth_left > 0:
        half_x = min_x + (max_x - min_x) / 2.0
        half_y = min_y + (max_y - min_y) / 2.0
        ret.extend(
            quadtree_index(
                intersection, (min_x, min_y, half_x, half_y), min_size,
                depth_left - 1))
        ret.extend(
            quadtree_index(
                intersection, (half_x, min_y, max_x, half_y), min_size,
                depth_left - 1))
        ret.extend(
            quadtree_index(
                intersection, (half_x, half_y, max_x, max_y), min_size,
                depth_left - 1))
        ret.extend(
            quadtree_index(
                intersection, (min_x, half_y, half_x, max_y), min_size,
                depth_left - 1))
    return ret


# .............................................................................
class SpatialIndex:
    """This class provides an index for quickly performing intersects."""
    # ..........................
    def __init__(self, index_name=None):
        self.index = rtree.index.Index(index_name)
        self._att_filename = '{}.json'.format(index_name)
        self._geom_filename = '{}.geom_json'.format(index_name)
        self.att_lookup = {}
        if os.path.exists(self._att_filename):
            with open(self._att_filename) as in_file:
                self.att_lookup = json.load(in_file)
        self.geom_lookup = {}
        if os.path.exists(self._geom_filename):
            with open(self._geom_filename) as in_file:
                tmp_geoms = json.load(in_file)
                for k, wkt in tmp_geoms.items():
                    self.geom_lookup[k] = ogr.CreateGeometryFromWkt(wkt)
                #self.geom_lookup = json.load(in_file)
        self.min_size = 0.01
        self.depth_left = 10
        self.next_geom = len(self.geom_lookup)

    # ..........................
    def add_feature(self, identifier, geom, att_dict):
        """Add a feature to the index.

        Args:
            identifier: An identifier for this feature in the lookup table
            geom: A geometry to spatially index
            att_dict: A dictionary of attributes to store in the lookup table
        """
        self.att_lookup[str(identifier)] = att_dict
        if isinstance(geom, str):
            geom = ogr.CreateGeometryFromWkt(geom)
        min_x, max_x, min_y, max_y = geom.GetEnvelope()
        idx_entries = quadtree_index(
            geom, (min_x, min_y, max_x, max_y), self.min_size, self.depth_left)
        for bbox, idx_geom in idx_entries:
            if isinstance(idx_geom, bool) and idx_geom:
                # Index as entire bbox
                self.index.insert(identifier, bbox, obj=True)
            else:
                # Add geometry to lookup, increment counter
                self.index.insert(identifier, bbox, obj=self.next_geom)
                self.geom_lookup[self.next_geom] = idx_geom
                self.next_geom += 1

    # ..........................
    def save(self):
        """Save the index attributes"""
        with open(self._att_filename, 'w') as out_file:
            json.dump(self.att_lookup, out_file)
        with open(self._geom_filename, 'w') as out_file:
            out_geoms = {k: val.ExportToWkt() for k, val in self.geom_lookup.items()}
            json.dump(out_geoms, out_file)
            # json.dump(self.geom_lookup, out_file)

    # ..........................
    def search(self, x, y):
        """Search for x, y and return attributes in lookup if found."""
        hits = {}
        for hit in self.index.intersection((x, y, x, y), objects=True):
            if hit.id not in hits.keys():
                if isinstance(hit.object, bool) or \
                        self._point_intersect(x, y, self.geom_lookup[str(hit.object)]):
                    hits[str(hit.id)] = self.att_lookup[str(hit.id)]
        return hits

    # ..........................
    @staticmethod
    def _point_intersect(pt_x, pt_y, geom):
        pt_geom = ogr.CreateGeometryFromWkt('POINT ({} {})'.format(pt_x, pt_y))
        return pt_geom.Within(geom)


# .............................................................................
__all__ = ['SpatialIndex']
