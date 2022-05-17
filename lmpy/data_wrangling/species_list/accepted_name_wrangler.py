"""Module containing occurrence data wranglers for modifying a species list."""
from lmpy.data_wrangling.common.accepted_name_wrangler import (
    _AcceptedNameWrangler,
    resolve_names_gbif,
)
from lmpy.data_wrangling.species_list.base import _SpeciesListDataWrangler
from lmpy.species_list import SpeciesList


# .....................................................................................
class AcceptedNameSpeciesListWrangler(_SpeciesListDataWrangler, _AcceptedNameWrangler):
    """Modifies a species list to update taxon names to the "accepted" names."""
    name = 'AcceptedNameSpeciesListWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        name_map=None,
        name_resolver=None,
        purge_failures=True,
        out_map_filename=None,
        map_write_interval=100,
        out_map_format='json',
        **params
    ):
        """Constructor for AcceptedNameSpeciesListModifier class.

        Args:
            name_map (dict): A map of original name to accepted name.
            name_resolver (str or Method): If provided, use this method for getting new
                accepted names.  If set to 'gbif', use GBIF name resolution.
            purge_failures (bool): Should failures be purged from the tree.
            out_map_filename (str): A file location to write the updated name map.
            map_write_interval (int): Update the name map output file after each set of
                this many iterations.
            out_map_format (str): The format to write the names map (csv or json).
            **params (dict): Keyword parameters to pass to _TreeDataWrangler.
        """
        if isinstance(name_resolver, str) and name_resolver.lower() == 'gbif':
            name_resolver = resolve_names_gbif
        _AcceptedNameWrangler.__init__(
            self,
            name_map=name_map,
            name_resolver=name_resolver,
            out_map_filename=out_map_filename,
            map_write_interval=map_write_interval,
            out_map_format=out_map_format,
        )
        _SpeciesListDataWrangler.__init__(self, **params)

    # .......................
    def wrangle_species_list(self, species_list):
        """Wrangle a species list.

        Args:
            species_list (SpeciesList): A species list to wrangle.

        Returns:
            SpeciesList: A species list with accepted names.
        """
        accepted_species = set()
        acc_names = self.resolve_names(species_list)
        num_unresolved = 0
        num_duplicates = 0
        for name in species_list:
            if acc_names[name] is None:
                num_unresolved += 1
            elif acc_names[name] in accepted_species:
                num_duplicates += 1
            else:
                accepted_species.add(acc_names[name])
        self.report['unresolved'] = num_unresolved
        self.report['duplicates'] = num_duplicates
        return SpeciesList(accepted_species)
