===================
TreeWrapper Objects
===================

Introduction
============
We have created a subclass of the `Dendropy <https://dendropy.org>`_ base Tree
class that adds a few convenience functions that are useful to several
Lifemapper analyses.  We found that the existing method for generating a
distance matrix consumed far too much memory for very large trees that we often
work with, therefore, we have provided an alternative method for generating
those distance matrices that runs in slightly more time, but requires
significantly less memory.  You can use all of the same functions available to
the base Tree class as well as those described.


Creating TreeWrapper Instances
==============================
From an existing Dendropy Tree
------------------------------
See: `TreeWrapper.from_base_tree <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.from_base_tree>`_

    >>> tree = TreeWrapper.from_base_tree(dendropy_tree)

Reading a file
--------------
See: `TreeWrapper.from_filename <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.from_filename>`_

    >>> tree = TreeWrapper.from_filename('my_tree_file.tre')

----

Annotations
===========
Adding node labels
------------------
Adds labels to tree nodes the same way that R does

See: `TreeWrapper.add_node_labels <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.add_node_labels>`_

    >>> tree.add_node_labels()

Annotating tips and nodes
-------------------------
See: `TreeWrapper.annotate_tree <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.annotate_tree>`_

    >>> ann_dict = {'A' : 1, 'B' : 2, 'C' : 3}
    >>> tree.annotate_tree(ann_dict)

Annotating tree tips
--------------------
See: `TreeWrapper.annotate_tree_tips <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.annotate_tree_tips>`_

    >>> ann_pairs = {'Sp_1': 1999, 'Sp_2': 1973, 'Sp_3' : 1934}
    >>> tree.annotate_tree_tips('year', ann_pairs)

Retrieving annotations
----------------------
See: `TreeWrapper.get_annotations <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.get_annotations>`_

    >>> annotations = tree.get_annotations('my_attribute')

Retrieving tip labels
---------------------
See: `TreeWrapper.get_labels <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.get_labels>`_

    >>> labels = tree.get_labels()

----

Getting matrices
================
Get distance matrix
-------------------
Get a matrix of phylogenetic distances from each tip to all other tips.  This
version has a smaller memory footprint than the original Dendropy method at the
trade-off of a slightly longer running time for large matrices.

See: `TreeWrapper.get_distance_matrix <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.get_distance_matrix>`_

    >>> d_mtx = tree.get_distance_matrix()

Get distance matrix using Dendropy method
-----------------------------------------
Get a matrix of phylogenetic distances from each tip to all other tips.  This
version uses the built-in function from Dendropy to generate the matrix and has
a much larger memory footprint but runs slightly faster at large scales.

See: `TreeWrapper.get_distance_matrix_dendropy <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.get_distance_matrix_dendropy>`_

    >>> d_mtx = tree.get_distance_matrix_dendropy()

Get variance covariance matrix
------------------------------
See: `TreeWrapper.get_variance_covariance_matrix <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.get_variance_covariance_matrix>`_

    >>> var_cov_mtx = tree.get_variance_covariance_matrix()

----

Inspecting the tree
===================
Checking for branch lengths
---------------------------
See: `TreeWrapper.has_branch_lengths <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.has_branch_lengths>`_

    >>> bool(tree.has_branch_lengths())
    True

Checking for polytomies
-----------------------
See: `TreeWrapper.has_polytomies <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.has_polytomies>`_

    >>> bool(tree.has_polytomies())
    False

Checking if a tree is binary
----------------------------
See: `TreeWrapper.is_binary <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.is_binary>`_

    >>> bool(tree.is_binary())
    True

Checking if a tree is ultrametric
---------------------------------
See: `TreeWrapper.is_ultrametric <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.is_ultrametric>`_

    >>> bool(tree.is_ultrametric())
    True

----

Pruning tree tips without an attribute
======================================
See: `TreeWrapper.prune_tips_without_attribute <../autoapi/lmpy/tree/index.html#lmpy.tree.TreeWrapper.prune_tips_without_attribute>`_

    >>> tree.prune_tips_without_attribute(search_attribute='my_att')
