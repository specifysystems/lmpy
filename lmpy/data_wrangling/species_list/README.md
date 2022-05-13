# Species List Data Wranglers

Species list data wranglers operate on `lmpy.species_list.SpeciesList` objects and
modify / filter the species within so that it may be used for further analyses. Each
Species List Data Wrangler is a subclass of
`lmpy.data_wrangling.species_list.base._SpeciesListDataWrangler` and exposes
functionality through the `wrangle_species_list` method.  This method takes a
`SpeciesList` object as input and returns a wrangled version of that provided species
list.  Some common operations are to resolve taxonomy using a taxonomic name resolution
service and subset a list to match the tips in a tree or columns in a matrix.

## Example Usage

The data wrangler factory can be used to instantiate species list data wranglers from a
JSON configuration file.  The following example will perform taxonomic name resolution
for the names in a species list and then subset to those that are present in a tree.

Species list data wranglers example:

```python
from lmpy.data_wrangling.factory import WranglerFactory
from lmpy.species_list import SpeciesList
from lmpy.tree import TreeWrapper

tree_fn = 'some tree filename'
tree_schema = 'newick'
species_list_filename = 'location of species list'

my_tree = TreeWrapper.get(path=tree_fn, schema=tree_schema)
wrangler_config = [
    {
        "wrangler_type": "AcceptedNameSpeciesListWrangler",
        "name_resolver": "gbif",
    },
    {
        "wrangler_type": "MatchMatrixSpeciesListWrangler",
        "tree": my_tree,
        "species_axis": 1
    }
]

factory = WranglerFactory()
species_list_wranglers = factory.get_wranglers(wrangler_config)

species_list = SpeciesList.from_file(species_list_filename)
for wrangler in species_list_wranglers:
    species_list = wrangler.wrangle_matrix_species_list(species_list)
```

## Subclassing _SpeciesListDataWrangler

Creating a new species list data wrangler requires overriding the
`wrangle_species_list` method.
See examples [match_matrix_wrangler.MatchMatrixSpeciesListWrangler](./match_matrix_wrangler.py)
and [accepted_name_wrangler.AcceptedNameSpeciesListWrangler](./accepted_name_wrangler.py).
