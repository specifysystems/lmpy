# lmpy Spatial Submodule

The lmpy spatial submodule contains modules and tools for spatial operations.  These
include tools for creating GeoJSON for a matrix in [geojsonify](./geojsonify.py) and
tools for creating a spatial index for data wrangling in
[spatial_index](./spatial_index.py) which define spatial indexes for faster operations 
to identify the geospatial relationships between geospatial features, such as nearest,
intersection, and more.  An index is built on either a single geospatial vector file,
in JSON or geo-JSON format, or a set of geospatial features in WKT format.
