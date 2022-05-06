# lmpy.data_wrangling

Submodules under this module define "Data Wranglers" that can be configured for
various operations. "Data Wranglers" are tools used to filter and / or modify data.  
Some examples are filtering
occurrence records that do not satisfy standards for modeling or modifying the tips of a
phylogenetic tree so that they match accepted taxonomy.

## Configuration

Data wrangling requires a JSON configuration, containing a list of one dictionary per 
desired wrangle. Each dictionary must contain "**wrangler_type**", with the name of the 
wrangler types. The dictionary will also contain any required parameters or optional 
parameters.

## Wrangler Factory

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
