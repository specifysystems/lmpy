=====================
Matrix Data Wrangling
=====================

Introduction
============
There are several scenarios where you would want to wrangle a Matrix by subsetting or
reordering or changing columns, etc.  Here are some examples.
----

Subset a PAM for a Taxon or Group of Taxa and Export to GeoJSON
===============================================================
You can subset a PAM for one ore more taxa using a data wrangler and then create
GeoJSON for the subset Matrix.

.. code-block:: python

    >>> import json
    >>> from lmpy.matrix import Matrix
    >>> from lmpy.spatial.geojsonify import geojsonify_matrix
    >>> from lmpy.data_wrangling.matrix.subset_reorder_slices_wrangler import SubsetReorderSlicesWrangler
    >>> pam = Matrix.load('my_pam.lmm')
    >>> keep_taxa = ['Species A', 'Species B', 'Species R']
    >>> wrangler = SubsetReorderSlicesWrangler(axes={'1': keep_taxa})
    >>> subset_pam = wrangler.wrangle_matrix(pam)
    >>> # create GeoJSON for subset PAM
    >>> subset_geojson = geojsonify_matrix(subset_pam, resolution=0.5, omit_values=[0])
    >>> with open('subset_pam.geojson', mode='wt') as out_json:
    >>>     out_json.dump(subset_geojson, out_json)

----

Subset a Matrix by Taxa, Generate Stats, and Write GeoJSON
==========================================================
You can subset a PAM by taxa, generate stats, and then write the outputs to a GeoJSON
file for spatial inspection using data wranglers and PamStats.

.. code-block:: python

    >>> import json
    >>> from lmpy.matrix import Matrix
    >>> from lmpy.spatial.geojsonify import geojsonify_matrix
    >>> from lmpy.statistics.pam_stats import PamStats
    >>> from lmpy.data_wrangling.matrix.purge_empty_slices_wrangler import PurgeEmptySlicesWrangler
    >>> from lmpy.data_wrangling.matrix.subset_reorder_slices_wrangler import SubsetReorderSlicesWrangler
    >>> pam = Matrix.load('my_pam.lmm')
    >>> keep_taxa = ['Species A', 'Species B', 'Species R']
    >>> # Set up wranlgers, first subset by species, then purge empty rows
    >>> wranglers = [
    ...     SubsetReorderSlicesWrangler(axes={'1': keep_taxa}),
    ...     PurgeEmptySlicesWrangler(purge_axes=[0])
    ... ]
    >>> # Wrangle the matrix using each of the wranglers
    >>> wrangled_pam = pam
    >>> for wrangler in wranglers:
    ...     wrangled_pam = wrangler.wrangle_matrix(pam)
    >>> # Create PamStats for the subset matrix
    >>> site_stats = PamStats(wrangled_pam).calculate_site_statistics()
    >>> # create GeoJSON for the site statistics
    >>> stats_geojson = geojsonify_matrix(site_stats, resolution=0.5, omit_values=[0])
    >>> with open('site_stats.geojson', mode='wt') as out_json:
    >>>     out_json.dump(stats_geojson, out_json)
