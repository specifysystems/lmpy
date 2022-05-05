# Occurrence Data Wranglers

These files define occurrence data manipulation parameters that can be configured for various tools

* A configuration file is in JSON format, a list of one dictionary per desired wrangler.  
  * Each dictionary must contain "wrangler_type", with the name of the wrangler types (listed below).  
  * The dictionary will also contain all required parameters and any optional parameters.  

* Currently, wrangler names correspond to the wrangler class `name` attribute in this module's files.
* The factory module instantiates wranglers and checks validity of parameters and values.
* Each wrangler's parameters correspond to the constructor arguments for that wrangler. 
* Valid wrangler types are enumerated in lmpy.data_wrangling.occurrence.factory.WRANGLER_TYPES
* Example clean_occurrences wrangler configuration:

```json
[
    {
        "wrangler_type" : "DecimalPrecisionFilter",
        "decimal_places" : 4
    },
    {
        "wrangler_type" : "UniqueLocalitiesFilter"
    },
    {
        "wrangler_type" : "MinimumPointsWrangler",
        "minimum_count" : 12
    }
]

```

## Wrangler types 

### AcceptedNameOccurrenceWrangler
* optional
  * name_map (dict): A map of original name to accepted name.
  * name_resolver (str or Method): If provided, use this method for getting new accepted names. 
    If set to 'gbif', use GBIF name resolution. 
  * store_original_attribute (str): A new attribute to store the
    original taxon name.

### AttributeFilterWrangler
* required
  * attribute_name (str): The name of the attribute to modify.
  * filter_func (Method): A function to be used for the pass condition.

### AttributeModifierWrangler
* required
  * attribute_name (str): The name of the attribute to modify. 
  * attribute_func (Method): A function to generate values for a point.

### BoundingBoxFilter
* required
  * min_x (numeric): The minimum 'x' value for the bounding box.
  * min_y (numeric): The minimum 'y' value for the bounding box.
  * max_x (numeric): The maximum 'x' value for the bounding box.
  * max_y (numeric): The maximum 'y' value for the bounding box.

### CommonFormatWrangler
* required
  * attribute_map (dict): A mapping of source key, target values.

### CoordinateConverterWrangler
* required
  * target_epsg (int): Target map projection specified by EPSG code.
* optional
  * source_epsg (int): Source map projection specified by EPSG code.
  * epsg_attribute (str or None): A point attribute containing EPSG code.
  * original_x_attribute (str): An attribute to store the original x value.
  * original_y_attribute (str): An attribute to store the original y value.

### DecimalPrecisionFilter
* required:
  * decimal_places (int): Only keep points with at least this many decimal places of precision.

### DisjointGeometriesFilter
* required:
  * geometry_wkts (list of str): A list of geometry WKTs to check against.

### IntersectGeometriesFilter
* required:
  * geometry_wkts (list of str): A list of WKT strings.

### MinimumPointsWrangler
* required:
  * minimum_count (int): The minimum number of points in order to keep all.

### SpatialIndexFilter
* required:
  * spatial_index (SpatialIndex): A SpatialIndex object that can be searched.
  * intersections_map (dict): A dictionary of species name keys and corresponding valid intersection values.
  * check_hit_func (Method): A function that takes two arguments (search hit, valid intersections for a species) 
    and returns a boolean indication if the hit should be counted.

### UniqueLocalitiesFilter
* optional parameters:
  * do_reset (bool): Reset the list of seen localities after each group.