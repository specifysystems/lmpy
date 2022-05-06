# Tree Data Wranglers

Tree data wranglers operate on `lmpy.tree.TreeWrapper` objects and modify / filter tips
of the tree so that the tree can be used in additional analyses.  Each tree wrangler is
a subclass of `lmpy.data_wrangling.tree.base._TreeDataWrangler` and exposes
functionality through the `wrangle_tree` method.  This method takes a `TreeWrapper`
object as input and returns a wrangled version of that provided tree.  Some common
options are to purge some tips from the tree and updating the taxon name for each tip
using a taxonomic name resolution service.

## Example Usage

The data wrangler factory can be used to instantiate tree data wranglers from a JSON
configuration file.  The following example will perform taxonomic name resolution for
the tips in a tree and then purge tips that are not present in a provided matrix.

Tree data wranglers example:

```python
from lmpy.data_wrangling.factory import WranglerFactory

# my_tree is a TreeWrapper object previously loaded
# my_mtx is a Matrix object that has been previously loaded
wrangler_config = [
    {
        "wrangler_type": "AcceptedNameTreeWrangler",
        "name_resolver": "gbif",
    },
    {
        "wrangler_type": "MatchMatrixTreeWrangler",
        "matrix": my_mtx,
        "species_axis": 1
    }
]

factory = WranglerFactory()
tree_wranglers = factory.get_wranglers(wrangler_config)

for wrangler in tree_wranglers:
    my_tree = wrangler.wrangle_tree(my_tree)
```

## Subclassing _TreeDataWrangler

Creating a new tree data wrangler requires overriding the `wrangle_tree` method.  See
examples [accepted_name_wrangler.AcceptedNameTreeWrangler](./accepted_name_wrangler.py)
and [subset_tree_wrangler.SubsetTreeWrangler](./subset_tree_wrangler.py).
