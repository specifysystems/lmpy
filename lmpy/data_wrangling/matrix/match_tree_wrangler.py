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
        # Axis 0 (y) should always be sites, Axis 1 should always be species
        for axis in range(matrix.ndim):
            if axis == self.species_axis:
                self.report["changes"][str(axis)] = {}
                # Include only columns with matching taxa
                column_indices = []
                axis_headers = matrix.get_headers(axis=str(axis))

                unmatched_tree_taxa = set()
                all_tree_taxa = []
                for taxon in self.tree.taxon_namespace:
                    all_tree_taxa.append(taxon.label)
                    if taxon.label in axis_headers:
                        # Save index of column from matrix for this taxon
                        taxa_col_idx = axis_headers.index(taxon.label)
                        column_indices.append(taxa_col_idx)
                        # axis_slice.append(axis_headers.index(taxon.label))
                        self.logger.log(
                            f"Tree taxon {taxon.label} from column {taxa_col_idx} " +
                            "added to slices for wrangled matrix",
                            refname=self.__class__.__name__)
                    else:
                        # Report tree taxa not in matrix
                        unmatched_tree_taxa.add(taxon.label)
                        self.logger.log(
                            f"Tree taxon {taxon.label} NOT present in matrix",
                            refname=self.__class__.__name__)

                # Report matrix taxa not present in tree
                unmatched_matrix_taxa = []
                for name in axis_headers:
                    if name not in all_tree_taxa:
                        unmatched_matrix_taxa.append(name)
                self.report["changes"][str(axis)]["purged"] = {
                    'count': (len(unmatched_matrix_taxa)),
                    'species': list(unmatched_matrix_taxa)
                }

                # Logging
                self.logger.log(
                    f"{len(unmatched_matrix_taxa)} species purged from matrix with " +
                    f"{len(axis_headers)} original species, {unmatched_matrix_taxa}.",
                    refname=self.__class__.__name__, log_level=DEBUG)
                self.logger.log(
                    f"{len(unmatched_tree_taxa)} Tree taxa of " +
                    f"{len(self.tree.taxon_namespace)} not found in matrix: " +
                    f"{unmatched_tree_taxa}",
                    refname=self.__class__.__name__, log_level=DEBUG)

            else:
                # Include all rows
                column_indices = list(range(matrix.shape[axis]))

            slices.append(column_indices)

        wrangled_matrix = matrix.slice(*slices)

        return wrangled_matrix
