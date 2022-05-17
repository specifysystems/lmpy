# Occurrence Data Wranglers

Occurrence data wranglers operate on lists of `lmpy.point.Point` objects and modify
and / or filter those point records according to each of the occurrence data wranglers
configured.  Each occurrence data wrangler is a subclass of
`lmpy.data_wrangling.occurrence.base._OccurrenceDataWrangler` and exposes functionality
through the `wrangle_occurrences` method.  This method takes a list of `Point` objects
as input and returns a list of wrangled `Point` objects which may include filtering out
points that don't satisfy the specified criteria or they may be modified by a wrangler
to fit a specified need, such as modifying the set of fields for a point so that it
meets a common format for aggregation.

* A configuration file is in JSON format, a list of one dictionary per desired
  wrangler.
  * Each dictionary must contain "wrangler_type", with the name of the wrangler types
    (listed below).
  * The dictionary will also contain all required parameters and any optional
    parameters.

* Currently, wrangler names correspond to the wrangler class `name` attribute in this
  module's files.
* Each wrangler's parameters correspond to the constructor arguments for that wrangler.
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

## Example Usage

The data wrangler factory can be used to instantiate data wranglers from a JSON configuration
file.  To use the data wrangler factory, create a json file containing a list of dictionaries
with parameters for each particular data wrangler to use.

Example wrangler factory usage:

```python
from lmpy.data_wrangling.factory import WranglerFactory

wrangler_config = [
    {
        "wrangler_type": "AcceptedNameOccurrenceWrangler",
        "name_resolver": "gbif"
    },
    {
        "wrangler_type": "UniqueLocalitiesFilter",
    },
    {
        "wrangler_type": "BoundingBoxFilter",
        "min_x": -171.79,
        "min_y": 18.91,
        "max_x": -66.96,
        "max_y": 71.36
    }
]

factory = WranglerFactory()
occ_wranglers = factory.get_wranglers(wrangler_config)

# Assume that points have been established somewhere
for wrangler in occ_wranglers:
    if points:
        points = wrangler.wrangle_points(points)
```

## Subclassing _OccurrenceDataWrangler

Creating a new occurrence data wrangler class can be somewhat simple.  For a new
filter-type wrangler, you can just override the `_pass_condition` method
(See: [bounding_box_wrangler.BoundingBoxWrangler](./bounding_box_wrangler.py)).
For a simple modifier wrangler, you can override the `_modify_point` method
(See: [common_format_wrangler.CommonFormatWrangler](./common_format_wrangler.py)).
For more complex cases, you may need to override both methods and maybe the
`wrangle_points` method as well
(see: [minimum_points_wrangler.MinimumPointsFilter](./minimum_points_wrangler.py)).

## Wrangler types

### AcceptedNameOccurrenceWrangler

* optional

  * name_map (dict): A map of original name to accepted name.
  * name_resolver (str or Method): If provided, use this method for getting new
    accepted names. If set to 'gbif', use GBIF name resolution.
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

* required

  * decimal_places (int): Only keep points with at least this many decimal places of
    precision.

### DisjointGeometriesFilter

* required

  * geometry_wkts (list of str): A list of geometry WKTs to check against.

### IntersectGeometriesFilter

* required

  * geometry_wkts (list of str): A list of WKT strings.

### MinimumPointsWrangler

* required

  * minimum_count (int): The minimum number of points in order to keep all.

### SpatialIndexFilter

* required

  * spatial_index (SpatialIndex): A SpatialIndex object that can be searched.
  * intersections_map (dict): A dictionary of species name keys and corresponding valid
    intersection values.
  * check_hit_func (Method): A function that takes two arguments (search hit, valid
    intersections for a species) and returns a boolean indication if the hit should be
    counted.

### UniqueLocalitiesFilter

* optional

  * do_reset (bool): Reset the list of seen localities after each group.
