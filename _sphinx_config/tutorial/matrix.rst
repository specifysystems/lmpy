==============
Matrix Objects
==============

Introduction
============
We have found that, while easy to use and an efficient data structure, NumPy
arrays do not really support metadata.  We had dealt with this in the past by
passing a secondary data structure with metadata along with the array but we
found that it was too easy for that metadata to get lost, out of date, or just
ignored.  In response, we have sub-classed Numpy ndarray to create 'Matrix'
objects that extend the base functionality provided by ndarrays to include
metadata and headers for the arrays without the needing a secondary data
structure.  Additionally, we provide some convenience functions for
manipulating these arrays as well as their metadata and headers so that they
are more useful for our needs.  This additional functionality may be useful for
you as well, so we have included it in the lmpy repository.  Note that if you
are developing an extension for the
`BiotaPhy Python Repository <https://github.com/biotaphy/BiotaPhyPy>`_, you
should utilize this class as arrays within a Lifemapper cluster use these
Matrix objects.


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
