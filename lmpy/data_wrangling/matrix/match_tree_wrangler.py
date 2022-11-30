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
                self.report["changes"][str(axis)] = {}
                axis_slice = []
                axis_headers = matrix.get_headers(axis=str(axis))

                unmatched_tree_taxa = set()
                all_tree_taxa = []
                for taxon in self.tree.taxon_namespace:
                    all_tree_taxa.append(taxon.label)
                    if taxon.label in axis_headers:
                        # Subset matrix to include only taxa in tree
                        axis_slice.append(axis_headers.index(taxon.label))
                        self.logger.log(
                            f"Tree taxon {taxon.label} added to wrangled matrix",
                            refname=self.__class__.__name__)
                    else:
                        # Report tree taxa not in matrix
                        unmatched_tree_taxa.add(taxon.label)
                self.logger.log(
                    f"{len(unmatched_tree_taxa)} Tree taxa not found in matrix: " +
                    "{unmatched_tree_taxa}",
                    refname=self.__class__.__name__)

                # Report matrix taxa not present in tree
                unmatched_matrix_taxa = []
                for name in axis_headers:
                    if name not in all_tree_taxa:
                        unmatched_matrix_taxa.append(name)
                self.logger.log(
                    f"{len(unmatched_matrix_taxa)} Matrix taxon NOT present in tree" +
                    f" (and purged from matrix): {unmatched_matrix_taxa}",
                    refname=self.__class__.__name__)
                # unmatched_matrix_taxa = set(axis_headers).difference(
                #     set(self.tree.taxon_namespace))
                # for mtaxa in unmatched_matrix_taxa:
                #     self.logger.log(
                #         f"Matrix taxon {mtaxa} not present in tree (but not purged)",
                #         refname=self.__class__.__name__)
                self.report["changes"][str(axis)]["purged"] = {
                    'count': (len(unmatched_matrix_taxa)),
                    'species': list(unmatched_matrix_taxa)
                }

                # Logging
                self.logger.log(
                    f"From matrix with {len(axis_headers)} species, purged " +
                    f"{len(unmatched_matrix_taxa)} species: {unmatched_matrix_taxa}.",
                    refname=self.__class__.__name__, log_level=DEBUG)
                self.logger.log(
                    f"Tree contains {len(self.tree.taxon_namespace)} tips, " +
                    f"{len(unmatched_tree_taxa)} are not in matrix: " +
                    f"{unmatched_tree_taxa}",
                    refname=self.__class__.__name__,
                    log_level=DEBUG)

            else:
                axis_slice = list(range(matrix.shape[axis]))

            slices.append(axis_slice)

        return matrix.slice(*slices)
