# lmpy.data_preparation
This module prepares data as input into lmpy biogeographical analyses.  

* **build_grid** prepares a geospatial vector file representing a regular grid of square cells covering a rectangular  
  geospatial region of the earth, and defined by minimum and maximum x and y coordinates.  The resulting output is 
  called a **shapegrid** and the cells in it are called **sites**.

* **layer_encoder** prepares a matrix from one or more geospatial layers, either raster or vector, and a shapegrid.  
  Parameters define the algorithm, layer attributes and values to use for encoding the region covered by a shapegrid 
  site.

* **occurrence_splitter** prepares a set of occurrence records, in either Darwin Core Archive (DwCA) or delimited text 
  (CSV) format by splitting the data into groups, for use as inputs to analyses, such as species distribution 
  modeling (SDM) or collection analyses. 

* **tree_encoder** enables a phylogenetic tree to be encoded into a new output matrix, given an input tree and input
  matrix where the tree tip labels match the matrix labels.