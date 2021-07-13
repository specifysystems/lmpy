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


Reading Data Files
==================

Read a CSV File
---------------
Read a CSV file that has fields "decimalLongitude" and "decimalLatitude" for x and y
and "speciesName" for the species binomial.

    >>> reader = PointCsvReader(csv_filename, 'speciesName', 'decimalLongitude', 'decimalLatitude')


Read a Darwin Core Archive File
-------------------------------
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




Creating Matrix Instances
=========================

From an existing NumPy ndarray
------------------------------
See: `Matrix <../source/lmpy.html#lmpy.matrix.Matrix>`_

    >>> np_arr = numpy.ones((5, 5))
    >>> new_mtx = Matrix(np_arr)

Reading a CSV file
------------------
See: `Matrix.load_csv <../source/lmpy.html#lmpy.matrix.Matrix.load_csv>`_

    >>> csv_fn = 'my_csv_file.csv'
    >>> new_mtx = Matrix.load(csv_fn, num_header_rows=1)

Reading a saved Matrix
----------------------
See: `Matrix.load <../source/lmpy.html#lmpy.matrix.Matrix.load>`_

    >>> mtx_fn = 'my_mtx_file.lmm'
    >>> new_mtx = Matrix.load(mtx_fn)

Concatenating existing Matrix objects
-------------------------------------
See: `Matrix.concatenate <../source/lmpy.html#lmpy.matrix.Matrix.concatenate>`_

    >>> mtx_a = Matrix(np.ones((3, 3)))
    >>> mtx_b = Matrix(np.zeros((3, 10)))
    >>> concat_mtx = Matrix.concatenate([mtx_a, mtx_b], axis=1)

Slicing by array indices
------------------------
See: `Matrix.slice <../source/lmpy.html#lmpy.matrix.Matrix.slice>`_

    >>> np_mtx = numpy.arange(15).reshape((3, 5))
    >>> mtx = Matrix(np_mtx)
    >>> new_mtx = mtx.slice([0, 1], [0, 3, 4])

Slicing by headers
------------------
See: `Matrix.slice_by_header <../source/lmpy.html#lmpy.matrix.Matrix.slice_by_header>`_

    >>> np_mtx = numpy.arange(15).reshape((3, 5))
    >>> mtx = Matrix(np_mtx, headers={'0': ['A', 'B', 'C'], '1': [0, 1, 2, 3, 4]})
    >>> mtx.slice_by_header('B', 0)
    Matrix([[5, 6, 7, 8, 9]])

----

Writing Matrix objects
======================

Saving to the file system
-------------------------
See: `Matrix.save <../source/lmpy.html#lmpy.matrix.Matrix.write>`_

    >>> mtx.write('path_to_new_file.lmm')

Writing to a CSV file
---------------------
See: `Matrix.write_csv <../source/lmpy.html#lmpy.matrix.Matrix.write_csv>`_

    >>> mtx.write_csv('path_to_new_csv_file.csv')

----

Header management
=================

On instantiation
----------------
See: `Matrix <../source/lmpy.html#lmpy.matrix.Matrix>`_

    >>> mtx = Matrix(np.ones((3, 3)), headers={'0': [1, 2, 3], '1': ['A', 'B', 'C']})

Setting headers
---------------
See: `Matrix.set_headers <../source/lmpy.html#lmpy.matrix.Matrix.set_headers>`_,
`Matrix.set_column_headers <../source/lmpy.html#lmpy.matrix.Matrix.set_column_headers>`_,
`Matrix.set_row_headers <../source/lmpy.html#lmpy.matrix.Matrix.set_row_headers>`_

    >>> # Each method sets row headers to 0, 1, 2
    >>> mtx.set_headers([0, 1, 2], axis=0)
    >>> mtx.set_headers({'0': [0, 1, 2]})
    >>> mtx.set_row_headers([0, 1, 2])
    >>>
    >>> # Each method sets column headers to 'A', 'B', 'C'
    >>> mtx.set_headers(['A', 'B', 'C'], axis=1)
    >>> mtx.set_headers({'1': ['A', 'B', 'C']})
    >>> mtx.set_column_headers(['A', 'B', 'C'])

Getting headers
---------------
See: `Matrix.get_headers <../source/lmpy.html#lmpy.matrix.Matrix.get_headers>`_,
`Matrix.get_column_headers <../source/lmpy.html#lmpy.matrix.Matrix.get_column_headers>`_,
`Matrix.get_row_headers <../source/lmpy.html#lmpy.matrix.Matrix.get_row_headers>`_

    >>> mtx.get_headers()
    >>> mtx.get_column_headers()
    >>> mtx.get_headers(axis=1)
    >>> mtx.get_row_headers()
    >>> mtx.get_headers(axis=0)

----

Metadata management
===================

On instantiation
----------------
See: `Matrix <../source/lmpy.html#lmpy.matrix.Matrix>`_

    >>> mtx = Matrix(np.ones((3, 3)), metadata={'description': 'A 3x3 matrix of ones'})

Setting metadata
----------------

    >>> mtx.metadata['author'] = 'My name'

Getting metadata
----------------
See: `Matrix.get_metadata <../source/lmpy.html#lmpy.matrix.Matrix.get_metadata>`_

    >>> mtx.metadata
    >>> mtx.get_metadata()

----
