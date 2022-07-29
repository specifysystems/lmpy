"""Module containing data wranglers for matching a matrix to a tree."""
from logging import DEBUG

from lmpy.tree import TreeWrapper

from lmpy.data_wrangling.matrix.base import _MatrixDataWrangler


# .....................................................................................
class MatchTreeMatrixWrangler(_MatrixDataWrangler):
    """Subset and reorder a matrix to match a tree."""
    name = 'MatchTreeMatrixWrangler'
    version = '1.0'

    # .......................
    def __init__(
        self,
        tree,
        species_axis,
        **params
    ):
        """Constructor for MatchTreeMatrixWrangler class.

        Args:
            tree (TreeWrapper or str): A tree object or file path to a tree.
            species_axis (int): The matrix axis with species names to match.
            **params (dict): Keyword parameters to pass to _MatrixDataWrangler.
        """
        _MatrixDataWrangler.__init__(self, **params)

        if isinstance(tree, str):
            tree = TreeWrapper.from_filename(tree)
        self.tree = tree
        self.species_axis = species_axis
        self.report['changes'] = {}

    # .......................
    def wrangle_matrix(self, matrix):
        """Wrangle a matrix.

        Args:
            matrix (Matrix): A matrix to wrangle.

        Returns:
            Matrix: The matrix subset to tree tip names.
        """
        slices = []
        for axis in range(matrix.ndim):
            if axis == self.species_axis:
                axis_slice = []
                axis_headers = matrix.get_headers(axis=str(axis))

                unmatched_tree_taxa = set()
                for taxon in self.tree.taxon_namespace:
                    if taxon.label in axis_headers:
                        axis_slice.append(axis_headers.index(taxon.label))
                    else:
                        unmatched_tree_taxa.add(taxon.label)
                        self.logger.log(
                            f"Tree taxon {taxon.label} not present in matrix",
                            refname=self.__class__.__name__)
                unmatched_matrix_taxa = set(axis_headers).difference(
                    set(self.tree.taxon_namespace))
                for mtaxa in unmatched_matrix_taxa:
                    self.logger.log(
                        f"Matrix taxon {mtaxa} not present in tree",
                        refname=self.__class__.__name__)

                if str(axis) not in self.report['changes'].keys():
                    self.report['changes'][str(axis)] = {
                        'purged': {'count': 0}}
                self.report['changes'][str(axis)]['purged'] = {
                    'count': (len(axis_headers) - len(axis_slice)),
                    'species': list(unmatched_tree_taxa)}

                # Logging
                self.logger.log(
                    f"{len(unmatched_tree_taxa)} tree tips not present in matrix",
                    refname=self.__class__.__name__, log_level=DEBUG)
                self.logger.log(
                    f"{len(unmatched_matrix_taxa)} matrix columns not present in tree",
                    refname=self.__class__.__name__, log_level=DEBUG)
                self.logger.log(
                    f"Purging {self.report['changes'][str(axis)]['purged']} species.",
                    refname=self.__class__.__name__, log_level=DEBUG)

            else:
                axis_slice = list(range(matrix.shape[axis]))

            slices.append(axis_slice)

        return matrix.slice(*slices)
