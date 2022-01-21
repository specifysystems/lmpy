==================
Occurrence Filters
==================

Introduction
============
Occurrence filters are methods that take an occurrence point as input and return a binary
value indicating if that point passes that particular filter.  These filter
functions are exposed via 'get' methods that allow you to configure a
particular filter to fit your needs and then provide a reusable function that
can be used to process entire sets of points.  Filters can be chained together
to "clean" occurrence data before processing.

Bounding Box Filter
===================
A bounding box filter simply checks to see if the X,Y coordinates of a point
fall within the specified bounding box.

See: `get_bounding_box_filter <../autoapi/lmpy/data_wrangling/occurrence/filters/index.html#lmpy.data_wrangling.occurrence.filters.get_bounding_box_filter>`_

    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> bbox_filter = get_bounding_box_filter(0, 0, 30, 30)
    >>> print(bbox_filter(point_1))
    []
    >>> print(bbox_filter(point_2))
    [Point('Test species', 20, 20)]

----

Disjoint Geometries Filter
==========================
A disjoint geometries filter will only pass points that fall outside of a set
of geometries.  This is useful if you want to do something like remove species occurrence points
that are from specimens from living research collections.  For example, you would create a set of bufferred point
geometries around each garden locations and use those to configure the filter.

See `get_disjoint_geometries_filter <../autoapi/lmpy/data_wrangling/occurrence/filters/index.html#lmpy.data_wrangling.occurrence.filters.get_disjoint_geometries_filter>`_

    >>> # Filter points not within bounding box (0, 0, 40, 40)
    >>> test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> disjoint_filter = get_disjoint_geometries_filter(test_geometries)
    >>> print(disjoint_filter(point_1))
    [Point('Test species', -10, 10)]
    >>> print(disjoint_filter(point_2))
    []

----

Intersect Geometries Filter
===========================
The intersect geometries filter is the inverse of the disjoint geometries
filter.  It only passes points found within the specified test geometries.

See `get_intersect_geometries_filter <../autoapi/lmpy/data_wrangling/occurrence/filters/index.html#lmpy.data_wrangling.occurrence.filters.get_intersect_geometries_filter>`_

    >>> # Filter points within bounding box (0, 0, 40, 40)
    >>> test_geometries = ['POLYGON ((0 0, 40 0, 40 40, 0 40, 0 0))']
    >>> point_1 = Point('Test species', -10, 10)
    >>> point_2 = Point('Test species', 20, 20)
    >>> intersect_filter = get_intersect_geometries_filter(test_geometries)
    >>> print(intersect_filter(point_1))
    []
    >>> print(intersect_filter(point_2))
    [Point('Test species', 20, 20)]

----

Unique Localities Filter
========================
The unique localities filter is used to filter out points with identical
localities.  This is used to ensure that models are only produced
for species with a minimum number of unique localites.

See `get_unique_localities_filter <../autoapi/lmpy/data_wrangling/occurrence/filters/index.html#lmpy.data_wrangling.occurrence.filters.get_unique_localities_filter>`_

    >>> point_1 = Point('Test species', -10, 10)
    >>> unique_loc_filter = get_unique_localities_filter()
    >>> # Should pass the first time
    >>> print(unique_loc_filter(point_1))
    [Point('Test species', -10, 10)]
    >>> # Try a second time, should fail
    >>> print(unique_loc_filter(point_1))
    []
