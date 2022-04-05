"""Module containing Tree Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _TreeDataWrangler(_DataWrangler):
    """Tree data wrangler base class."""
    name = '_TreeDataWrangler'

    # .......................
    def __init__(self, **params):
        """Constructor for _TreeDataWrangler base class.

        Args:
            **params (dict): Named parameters to pass to _DataWrangler base class.
        """
        _DataWrangler(self, **params)
        self.report['modified'] = 0
        self.report['purged'] = 0

    # .......................
    def _report_tip(self, modified=False, purged=False):
        """Report what is done on a tree tip.

        Args:
            modified (bool): Was the tip modified.
            purged (bool): Was the tip purged.
        """
        if modified:
            self.report['modified'] += 1

        if purged:
            self.report['purged'] += 1

    # .......................
    def wrangle_tree(self, tree):
        """Wrangle a tree.

        Args:
            tree (TreeWrapper): A phylogenetic tree to wrangle.

        Raises:
            NotImplementedError: This method is not implemeneted for the base class.
        """
        raise NotImplementedError('wrangle_matrix not implemented on base class.')
