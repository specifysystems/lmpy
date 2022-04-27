=============
Layer Encoder
=============

Introduction
============
The layer encoder provides functionality for converting spatial data into a
site by layer matrix.  This is useful for creating presence absence matrices,
PAMs, as well as other matrices that have the same spatial composition, so
that you may join species presence with environment or test biogeographic
hypotheses.

Creating a PAM
==============

Creating a PAM requires encoding each species layer (raster or vector) into a
matrix column of presence or absence values for each site.  This operation
requires that you create an encoder for a grid of cells and then encode each
species layer individually.  There are three configuration parameters for
encoding these layers to consider.  Minimum presence, this is the minimum value
of the species layer that should be considered present.  For example, if your
species layer is scaled 0-100, maybe you want to consider any value above 0 to
be present.  Maximum presence is the maximum value to be considered present.
This is possibly most useful when you have a postive NODATA value, such as 255
for unsigned single byte integer cell values.  Finally, minimum coverage, this
value indicates what portion of a grid cell must be covered by "present" values
to call that cell present.  For instance, you may want to call grid cells
present if any part of the cell is present, so you would set the value to
something small, like 1 percent, or you may want more substantial coverage, so
you would set the value to 10 or 25 percent.

See: `encode_presence_absence <../autoapi/lmpy/data_preparation/layer_encoder/index.html#lmpy.data_preparation.layer_encoder.LayerEncoder.encode_presence_absence>`_

    >>> grid_filename = 'my_grid.shp'
    >>> min_x, min_y, max_x, max_y = (0, 0, 90, 90)
    >>> cell_size = 1.0  # Decimal degrees
    >>> grid_epsg = 4326
    >>> cell_sides = 4  # Squares
    >>> build_shapegrid(
    ...     grid_filename,
    ...     min_x,
    ...     min_y,
    ...     max_x,
    ...     max_y,
    ...     cell_size,
    ...     grid_epsg,
    ...     cell_sides
    ... )
    >>> encoder = LayerEncoder(grid_filename)
    >>> min_presence = 1
    >>> max_presence = 254
    >>> min_coverage = 25  # Percent
    >>> encoder.encode_presence_absence(
    ...     species_raster_1,
    ...     'Species 1',
    ...     min_presence,
    ...     max_presence,
    ...     min_coverage
    ... )
    >>> encoder.encode_presence_absence(
    ...     species_raster_2,
    ...     'Species 2',
    ...     min_presence,
    ...     max_presence,
    ...     min_coverage
    ... )
    >>> encoder.encode_presence_absence(
    ...     species_raster_3,
    ...     'Species 3',
    ...     min_presence,
    ...     max_presence,
    ...     min_coverage
    ... )
    >>> pam = encoder.get_encoded_matrix()
    >>> pam_geojson = encoder.get_geojson()

----

Encoding Environmental Data
===========================
You may want to encode environmental data using the same grid used to create a
PAM.  To do so, you can use the encode_mean_value and encode_largest_class
methods to store either the average non-NODATA value for continuous values or
the most prevalent non-NODATA value for categorical data respectively.

See: `encode_mean_value <../autoapi/lmpy/data_preparation/layer_encoder/index.html#lmpy.data_preparation.layer_encoder.LayerEncoder.encode_mean_value>`_

See: `encode_largest_class <../autoapi/lmpy/data_preparation/layer_encoder/index.html#lmpy.data_preparation.layer_encoder.LayerEncoder.encode_largest_class>`_

From new grid:

.. code-block:: python

    >>> grid_filename = 'my_grid.shp'
    >>> min_x, min_y, max_x, max_y = (0, 0, 90, 90)
    >>> cell_size = 1.0  # Decimal degrees
    >>> grid_epsg = 4326
    >>> cell_sides = 4  # Squares
    >>> build_shapegrid(
    ...     grid_filename,
    ...     min_x,
    ...     min_y,
    ...     max_x,
    ...     max_y,
    ...     cell_size,
    ...     grid_epsg,
    ...     cell_sides
    ... )
    >>> encoder = LayerEncoder(grid_filename)
    >>> min_presence = 1
    >>> max_presence = 127
    >>> min_coverage = 25  # Percent
    >>> encoder.encode_mean_value(env_raster_1, 'ENV Raster 1', nodata=-999)
    >>> encoder.encode_mean_value(env_raster_2, 'ENV Raster 2')
    >>> encoder.encode_largest_class(
    ...     env_vector_3,
    ...     'ENV Vector 3',
    ...     min_coverage,
    ...     attribute_name='category'
    ... )
    >>> encoder.encode_largest_class(
    ...     env_vector_4,
    ...     'ENV Vector 4',
    ...     min_coverage,
    ...     attribute_name='ecozone'
    ... )
    >>> env_mtx = encoder.get_encoded_matrix()
    >>> env_geojson = encoder.get_geojson()

From existing grid:

.. code-block:: python

    >>> import json
    >>> from lmpy.data_preparation/layer_encoder import LayerEncoder
    >>> grid_filename = 'my_grid.shp'
    >>> env_layer_1 = 'precipitation.tif'
    >>> env_layer_2 = 'temperature.tif'
    >>> encoder = LayerEncoder(grid_filename)
    >>> min_coverage = 25  # Percent
    >>> encoder.encode_mean_value(env_layer_1, 'Precipitation')
    >>> encoder.encode_mean_value(env_layer_2, 'Temperature')
    >>> env_mtx = encoder.get_encoded_matrix()
    >>> # Write GeoJSON
    >>> with open('encoded_layers.geojson', mode='wt') as out_json:
    ...     json.dump(encoder.get_geojson(), out_json)
    >>> # Write CSV
    >>> with open('encoded_layers.csv', mode='wt') as out_csv:
    ...     env_mtx.write_csv(out_csv)

----

Encoding Biogeographic Hypotheses
=================================

You can encode biogeographic hypothesis layers as binary (0, 1) or tertiary
(-1, 0, 1) values in a matrix.  This is used by computations such as MCPA
(Metacommunity Phylogenetic Analysis) for determining if presences are found
inside or outside of single-sided hypotheses or inside one side, the other, or
neither for two-sided hypotheses.

See `encode_biogeographic_hypothesis <../autoapi/lmpy/data_preparation/layer_encoder/index.html#lmpy.data_preparation.layer_encoder.LayerEncoder.encode_biogeographic_hypothesis`>_

    >>> grid_filename = 'my_grid.shp'
    >>> min_x, min_y, max_x, max_y = (0, 0, 90, 90)
    >>> cell_size = 1.0  # Decimal degrees
    >>> grid_epsg = 4326
    >>> cell_sides = 4  # Squares
    >>> build_shapegrid(
    ...     grid_filename,
    ...     min_x,
    ...     min_y,
    ...     max_x,
    ...     max_y,
    ...     cell_size,
    ...     grid_epsg,
    ...     cell_sides
    ... )
    >>> encoder = LayerEncoder(grid_filename)
    >>> min_presence = 1
    >>> max_presence = 127
    >>> min_coverage = 25  # Percent
    >>> encoder.encode_biogeographic_hypothesis(
    ...     hypothesis_1,
    ...     'Hypothesis 1',
    ...     min_coverage
    ... )
    >>> # Encode a hypothesis shapefile with multiple features using the 'zone'
    >>> #  attribute of each feature.
    >>> encoder.encode_biogeographic_hypothesis(
    ...     hypothesis_2,
    ...     'Hypothesis 2',
    ...     min_coverage,
    ...     event_field='zone'
    ... )
    >>> bg_mtx = encoder.get_encoded_matrix()
    >>> bg_geojson = encoder.get_geojson()
