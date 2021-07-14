=============
Data Cleaning
=============

Introduction
============
One of the first steps in creating species distribution models, let alone multi-species
analyses, is acquiring and preparing specimen occurrence records.  There are multiple
method for acquiring these raw specimen records such as aggregator downloads or API
calls but once you have the raw data, you need to assemble your entire dataset, which
involves converting records to a common format, grouping, and cleaning.  The lmpy
library provides tools for performing these aggregation and cleaning steps to greatly
simplify the process for the user.


Reading a CSV File
==================
Read a CSV file that has fields "decimalLongitude" and "decimalLatitude" for x and y
and "speciesName" for the species binomial.

    >>> reader = PointCsvReader(csv_filename, 'speciesName', 'decimalLongitude', 'decimalLatitude')


Reading a Darwin Core Archive File
==================================
Read a Darwin Core Archive file.  The file is assumed to be valid and metadata will
be pulled from the 'meta.xml' file contained within the zip file.

    >>> reader = PointDwcaReader(dwca_filename)


Filtering Records
=================

Built-in Filters
----------------
Filter a list of Point objects so that those with less than four (4) decimal places
of precision are removed.

    >>> points = [Point('Species A', 10.3, 23.1),
    ...    Point('Species B', 11.34123, 12.2314),
    ...    Point('Species C', 13.23131, 18.3123)]
    >>> precision_filter = get_decimal_precision_filter(4)
    >>> flt_points = precision_filter(points)
    >>> print(flt_points)
    [Point('Species B', 11.34123, 12.2314), Point('Species C', 13.23131, 18.3123)]


Custom Filters
--------------
Filter a list of points so that those without a species epithet are removed.

    >>> def genus_filter_func(point):
    ...     return len(point.split(' ')) > 1
    >>> genus_filter = get_occurrence_filter(genus_filter_func)
    >>> points = [Point('Species A', 1, 2),
    ...     Point('Genus', 3, 4), Point('Genus', 9, 3), Point('Species B', 2, 1)]
    >>> flt_points = genus_filter(points)
    >>> print(flt_points)
    [Point('Species A', 1, 2), Point('Species B', 2, 1)]


Modifying Records
=================

Built-in Modifiers
------------------

Custom Modifiers
----------------

Putting It All Together
=======================

Aggregate and Clean Multiple Data Files
---------------------------------------

    >>> get_data_from_aggregator
