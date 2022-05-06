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