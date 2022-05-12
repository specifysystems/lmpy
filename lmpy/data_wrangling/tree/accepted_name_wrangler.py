"""Module containing occurrence data wranglers for modifying tree tips."""
from lmpy.data_wrangling.common.accepted_name_wrangler import (
    _AcceptedNameWrangler,
    resolve_names_gbif,
)
from lmpy.data_wrangling.tree.base import _TreeDataWrangler


# .....................................................................................
class AcceptedNameTreeWrangler(_TreeDataWrangler, _AcceptedNameWrangler):
    """Modifies tree columns to update taxon names to the "accepted" names."""
    name = 'AcceptedNameTreeWrangler'
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
        """Constructor for AcceptedNameTreeModifier class.

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
        _TreeDataWrangler.__init__(self, **params)

        self.purge_failures = purge_failures

    # .......................
    def wrangle_tree(self, tree):
        """Wrangle a tree.

        Args:
            tree (TreeWrapper): A tree to wrangle.

        Returns:
            TreeWrapper: The tree with accepted taxon names.
        """
        failures = []
        for taxon in tree.taxon_namespace:
            acc_name = self.resolve_names([taxon.label])[taxon.label]
            if acc_name is None:
                failures.append(taxon)
                taxon.label = ''
            elif taxon.label != acc_name:
                taxon.label = acc_name
                # report
                self._report_tip(modified=True)

        # Should we purge?
        if self.purge_failures and len(failures) > 0:
            for _ in failures:
                self._report_tip(purged=True)

            tree.prune_taxa(failures)
            tree.purge_taxon_namespace()

        return tree
