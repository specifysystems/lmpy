"""Tests for the spatial_index module."""
import os
import tempfile

from lmpy.spatial.spatial_index import (
    create_geometry_from_bbox, quadtree_index, SpatialIndex)


# .............................................................................
class Test_create_geometry_from_bbox:
    """Test the create_geometry_from_bbox function."""
    # ..........................
    def test_valid(self):
        """Test with valid inputs."""
        _ = create_geometry_from_bbox(-10, -20, 30, 40)

    # ..........................
    def test_invalid_min_greater_than_max(self):
        """Test with invalid inputs."""
        _ = create_geometry_from_bbox(100, -20, 30, 40)


# .............................................................................
class Test_quadtree_index:
    """Test the quadtree_index function directly."""
    # ..........................
    def test_complete_overlap(self):
        """Simple test of two identical bounding boxes."""
        bbox = (-10, -10, 10, 10)
        test_geom = create_geometry_from_bbox(*bbox)
        test_vals = quadtree_index(test_geom, bbox, 0.1, 20)
        assert len(test_vals) == 1
        assert test_vals[0][0] == bbox
        assert test_vals[0][1]

    # ..........................
    def test_edge_overlap(self):
        """Test for bounding boxes that share an edge."""
        bbox_1 = (-10, -10, 10, 10)
        bbox_2 = (10, -10, 20, 20)
        test_geom = create_geometry_from_bbox(*bbox_1)
        test_vals = quadtree_index(test_geom, bbox_2, 0.1, 20)
        assert len(test_vals) == 0

    # ..........................
    def test_min_size(self):
        """Test intersect that is less than minimum size."""
        bbox_1 = (-10, -10, 10, 10)
        bbox_2 = (9, -10, 20, 20)
        test_geom = create_geometry_from_bbox(*bbox_1)
        test_vals = quadtree_index(test_geom, bbox_2, 1000, 20)
        assert len(test_vals) == 1
        assert test_vals[0][0] == bbox_2
        assert test_vals[0][1].GetEnvelope() == (9, 10, -10, 10)

    # ..........................
    def test_partial_overlap(self):
        """Test partially overlapping geometries."""
        bbox_1 = (-30, -30, 30, 30)
        bbox_2 = (-60, -40, 75, 0)
        test_geom = create_geometry_from_bbox(*bbox_1)
        test_vals = quadtree_index(test_geom, bbox_2, 0.001, 5)
        assert len(test_vals) >= 4


# .............................................................................
class Test_SpatialIndex:
    """Tests for the SpatialIndex class."""
    # ..........................
    def _clean_up(self, sp_index):
        """Remove files created when saving an index."""
        index_name = sp_index.index.properties.filename
        sp_index.close()
        for ext in ['.json', '.geom_json', '.dat', '.idx']:
            fn = '{}{}'.format(index_name, ext)
            if os.path.exists(fn):
                os.remove(fn)

    # ..........................
    def test_constructor(self):
        """Test constructor."""
        sp_index_1 = SpatialIndex()
        self._clean_up(sp_index_1)
        tmp_file = tempfile.NamedTemporaryFile()
        temp_name = tmp_file.name
        tmp_file.close()
        sp_index_2 = SpatialIndex(temp_name)
        sp_index_2.save()
        sp_index_2 = None
        # Check that it can be reloaded
        sp_index_3 = SpatialIndex(temp_name)
        self._clean_up(sp_index_3)

    # ..........................
    def test_build_index(self):
        """Test building and reloading an index."""
        tmp_file = tempfile.NamedTemporaryFile()
        temp_name = tmp_file.name
        tmp_file.close()
        sp_index = SpatialIndex(temp_name)
        # Build index
        sp_index.add_feature(
            1, create_geometry_from_bbox(-10, -10, 10, 10), {'att_1': 'val_1'})
        sp_index.add_feature(
            2, create_geometry_from_bbox(-20, -20, 20, 20), {'att_1': 'val_2'})
        sp_index.add_feature(
            3, create_geometry_from_bbox(-30, -30, 30, 30), {'att_1': 'val_3'})
        # Save index
        sp_index.save()
        sp_index = None
        # Reload index
        sp_index = SpatialIndex(temp_name)
        self._clean_up(sp_index)

    # ..........................
    def test_search_index(self):
        """Test searching an index."""
        tmp_file = tempfile.NamedTemporaryFile()
        temp_name = tmp_file.name
        tmp_file.close()
        sp_index = SpatialIndex(temp_name)
        # Build index
        sp_index.add_feature(
            1, create_geometry_from_bbox(-10, -10, 10, 10), {'att_1': 'val_1'})
        sp_index.add_feature(
            2, create_geometry_from_bbox(-20, -20, 20, 20), {'att_1': 'val_2'})
        sp_index.add_feature(
            3, create_geometry_from_bbox(-30, -30, 30, 30), {'att_1': 'val_3'})
        # Search
        hits_1 = sp_index.search(0, 0)
        assert len(hits_1) == 3
        assert hits_1['1']['att_1'] == 'val_1'
        assert hits_1['2']['att_1'] == 'val_2'
        assert hits_1['3']['att_1'] == 'val_3'
        hits_2 = sp_index.search(15, 15)
        assert len(hits_2) == 2
        assert hits_2['2']['att_1'] == 'val_2'
        assert hits_2['3']['att_1'] == 'val_3'
        hits_3 = sp_index.search(-25, -25)
        assert len(hits_3) == 1
        assert hits_3['3']['att_1'] == 'val_3'
        # Save index
        sp_index.save()
        sp_index = None
        # Reload index
        sp_index = SpatialIndex(temp_name)
        hits_1 = sp_index.search(0, 0)
        assert len(hits_1) == 3
        assert hits_1['1']['att_1'] == 'val_1'
        assert hits_1['2']['att_1'] == 'val_2'
        assert hits_1['3']['att_1'] == 'val_3'
        hits_2 = sp_index.search(15, 15)
        assert len(hits_2) == 2
        assert hits_2['2']['att_1'] == 'val_2'
        assert hits_2['3']['att_1'] == 'val_3'
        hits_3 = sp_index.search(-25, -25)
        assert len(hits_3) == 1
        assert hits_3['3']['att_1'] == 'val_3'
        self._clean_up(sp_index)

    # ..........................
    def test_edges(self):
        """Test edge cases."""
        tmp_file = tempfile.NamedTemporaryFile()
        temp_name = tmp_file.name
        tmp_file.close()
        sp_index = SpatialIndex(temp_name)
        # Add feature from WKT
        wkt_1 = 'POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))'
        sp_index.add_feature(1, wkt_1, {'att_1': 'val_1'})
        # Add feature that does not break down to rectangles
        wkt_2 = 'POLYGON ((0 -30, 30 0, 0 30, -30 0, 0 -30))'
        sp_index.add_feature(2, wkt_2, {'att_1': 'val_2'})
        _ = sp_index.search(-30, 0)
        sp_index.save()
        sp_index = None
        sp_index = SpatialIndex(temp_name)
        _ = sp_index.search(-30, 0)
        self._clean_up(sp_index)
