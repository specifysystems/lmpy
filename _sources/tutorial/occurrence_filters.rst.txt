==================
Occurrence Filters
==================

Introduction
============
Occurrence filters are methods that take a Point as input and return a binary
value indicating if that point passes that particular filter.  These filter
functions are exposed via 'get' methods that allow you to configure a
particular filter to fit your needs and then provide a reusable function that
can be used to process entire sets of points.  Filters can be chained together
to "clean" occurrence data before processing.

Bounding Box Filter
===================
A bounding box filter simply checks to see if the X,Y coordinates of a point
fall within the specified bounding box.

See: `get_bounding_box_filter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_filters.get_bounding_box_filter>`_

    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> bbox_filter = get_bounding_box_filter(0, 0, 30, 30)
    >>> print(bbox_filter(point_1))
    False
    >>> print(bbox_filter(point_2))
    True

----

Data Flag Filter
================
Data flag filters can be used to determine if a point should be kept based on
any flags attached to it.  For example, you may want to remove any points that
have the flag 'invalid' but otherwise you would keep them, retaining points
with acceptable flags.

See: `get_data_flag_filter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_filters.get_data_flag_filter>`_

    >>> point_1 = Point('Test species', -10, 10, flags=['invalid'])
    >>> point_2 = Point('Test species', 20, 20, flags=['added species'])
    >>> flag_filter = get_data_flag_filter(['invalid'])
    >>> print(flag_filter(point_1))
    False
    >>> print(flag_filter(point_2))
    True

----

Disjoint Geometries Filter
==========================
A disjoint geometries filter will only pass points that fall outside of a set
of geometries.  This is useful if you want to do something like remove points
that are found in herbaria.  You would create a set of bufferred point
geometries around herbarium locations and use those to configure the filter.

See `get_disjoint_geometries_filter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_filters.get_disjoint_geometries_filter>`_

    >>> # Filter points not within bounding box (0, 0, 40, 40)
    >>> test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> disjoint_filter = get_disjoint_geometries_filter(test_geometries)
    >>> print(disjoint_filter(point_1))
    True
    >>> print(disjoint_filter(point_2))
    False

----

Intersect Geometries Filter
===========================
The intersect geometries filter is the inverse of the disjoint geometries
filter.  It only passes points found within the specified test geometries.

See `get_intersect_geometries_filter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_filters.get_intersect_geometries_filter>`_

    >>> # Filter points within bounding box (0, 0, 40, 40)
    >>> test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> intersect_filter = get_intersect_geometries_filter(test_geometries)
    >>> print(intersect_filter(point_1))
    False
    >>> print(intersect_filter(point_2))
    True

----

Unique Localities Filter
========================
The unique localities filter is used to filter out points with identical
localities.  This is used by Lifemapper to ensure that models are only produced
for species with a minimum number of unique localites.

See `get_unique_localities_filter <../source/lmpy.data_preparation.html#lmpy.data_preparation.occurrence_filters.get_unique_localities_filter>`_

    >>> point_1 = Point('Test species', -10, 10)
    >>> unique_loc_filter = get_unique_localities_filter()
    >>> # Should pass the first time
    >>> print(unique_loc_filter(point_1))
    True
    >>> # Try a second time, should fail
    >>> print(unique_loc_filter(point_1))
    False
