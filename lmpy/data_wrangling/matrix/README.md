# Matrix Data Wranglers

Matrix data wranglers operate on `lmpy.matrix.Matrix` objects and modify / filter rows,
columns, and other axes to manipulate a Matrix so that it may be used for further
analyses.  Each Matrix Data Wrangler is a subclass of
`lmpy.data_wrangling.matrix.base._MatrixDataWrangler` and exposes functionality through
the `wrangle_matrix` method.  This method takes a `Matrix` object as input and returns
a wrangled version of that provided matrix.  Some common operations are to purge and
reorder columns and rows of a matrix so that it matches another data structure, such as
the order of the tips in a tree.

## Example Usage

The data wrangler factory can be used to instantiate matrix data wranglers from a JSON
configuration file.  The following example will perform taxonomic name resolution for
the columns of a matrix (where each column represents a species) and then purge and
reorder the columns of the matrix to match a provided tree.

Matrix data wranglers example:

```python
from lmpy.data_wrangling.factory import WranglerFactory

# my_tree is a TreeWrapper object previously loaded
wrangler_config = [
    {
        "wrangler_type": "AcceptedNameMatrixWrangler",
        "name_resolver": "gbif",
        "taxon_axis": 1
    },
    {
        "wrangler_type": "MatchTreeMatrixWrangler",
        "tree": my_tree,
        "species_axis": 1
    }
]

factory = WranglerFactory()
matrix_wranglers = factory.get_wranglers(wrangler_config)

# Assume that 'my_mtx' is a Matrix object of site rows and species columns
for wrangler in matrix_wranglers:
    my_mtx = wrangler.wrangle_matrix(my_mtx)
```

## Subclassing _MatrixDataWrangler

Creating a new matrix data wrangler requires overriding the `wrangle_matrix` method.
See examples [match_tree_wrangler.MatchTreeMatrixWrangler](./match_tree_wrangler.py)
and [accepted_name_wrangler.AcceptedNameMatrixWrangler](./accepted_name_wrangler.py).
