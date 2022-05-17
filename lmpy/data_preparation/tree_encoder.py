"""Module containing a class for encoding a Phylogenetic tree into a matrix.

See:
    Leibold, m.A., E.P. Economo and P.R. Peres-Neto. 2010. Metacommunity
        phylogenetics: separating the roles of environmental filters and
        historical biogeography. Ecology letters 13: 1290-1299.
"""
import numpy as np

from lmpy.matrix import Matrix
from lmpy.tree import TreeWrapper


# .............................................................................
class EncodingException(Exception):
    """Exception indicating there was a problem with encoding."""


# .............................................................................
class TreeEncoder:
    """A class representing encoding of tree to match PAM."""

    # ..............................
    def __init__(self, tree, pam):
        """Base constructor for tree encoder.

        Args:
            tree (TreeWrapper): A tree object to encode.
            pam (Matrix): A PAM matrix object.
        """
        self.tree = tree
        self.tree.add_node_labels()

        if isinstance(pam, Matrix):
            self.pam = pam
        else:
            self.pam = Matrix(pam)

        # Get labels from matrix or tree tips
        self.labels = self.pam.get_column_headers()
        if self.labels is None:
            self.labels = [tax.label for tax in tree.taxon_namespace]

    # ..............................
    @classmethod
    def from_file(cls, tree_file_name, pam_file_name):
        """Creates an instance of the PhyloEncoding class from tree and pam.

        Args:
            tree_file_name (str): The location of the tree.
            pam_file_name (str): The location of the PAM.

        Returns:
            TreeEncoder: A new tree encoder instance.
        """
        tree = TreeWrapper.from_filename(tree_file_name)
        pam = Matrix.load(pam_file_name)
        return cls(tree, pam)

    # ..............................
    def encode_phylogeny(self):
        """Encode the phylogenetic tree into a matrix.

        Note:
            P in the literature, a tip (row) by internal node (column) matrix
                that needs to match the provided PAM.

        Raises:
            EncodingException: Raised if the PAM and tree do not match.

        Returns:
            Matrix: An encoding of the phylogenetic tree.
        """
        if self.validate():  # Make sure that the PAM and tree match
            if self.tree.has_branch_lengths():
                p_mtx = self._build_p_matrix_with_branch_lengths()
            else:
                p_mtx = self._build_p_matrix_no_branch_lengths()
        else:
            raise EncodingException("PAM and Tree do not match, fix before encoding")

        return p_mtx

    # ..............................
    def validate(self):
        """Validates the tree / PAM combination.

        Returns:
            bool: Boolean indicating if the tree / pam is valid.
        """
        # check if tree is ultrametric
        if all(
            [
                (not self.tree.has_branch_lengths() or self.tree.is_ultrametric()),
                self.tree.is_binary(),
                len(self.tree.taxon_namespace) == self.pam.shape[1]
            ]
        ):
            # Check that the tips in the tree are the same as the column headers in the
            #     matrix
            # Check that matrix indices in tree match PAM
            tree_tips = [tax.label for tax in self.tree.taxon_namespace]

            # Find the intersection between the two lists
            intersection = set(self.labels) & set(tree_tips)

            # This checks that there are no duplicates in either of the indices
            #     lists and that they overlap completely
            if all([
                len(intersection) == len(self.labels),
                len(self.labels) == len(tree_tips)
            ]):
                # If everything checks out to here, return true for valid
                return True
        # If anything does not validate, return false
        return False

    # ..............................
    def _build_p_branch_length_values(self, node):
        """Recurse through the tree to get P matrix values for node / tips.

        Args:
            node (dendropy.Node): The current clade.

        Returns:
            tuple: A tuple of branch length dictionary, sum of branch lengths, and
                p-values dictionary.
        """
        # Dictionary of branch length lists, bottom-up from tip to current node
        bl_dict = {}

        clade_bl = node.edge_length  # To avoid lookups

        # This is the sum of all branch lengths in the clade and will be used
        #    as the denominator for the p value for each tip to this node.  See
        #    the literature for more information.  We will initialize with the
        #    branch length of this clade because it will always be added
        #    whether we are at a tip or an internal node.
        bl_sum = clade_bl

        # Dictionary of dictionaries of p values, first key is node path id,
        #    sub-keys are tip matrix indices for that node
        p_vals_dict = {}

        if node.num_child_nodes() > 0:  # Assume this is two since binary
            clade_p_vals = {}
            multipliers = [-1.0, 1.0]  # One positive, one negative
            np.random.shuffle(multipliers)

            for child in node.child_nodes():
                (
                    child_bl_dict,
                    child_bl_sum,
                    child_p_val_dict,
                ) = self._build_p_branch_length_values(child)
                multiplier = multipliers.pop(0)

                # Extend the p values dictionary
                p_vals_dict.update(child_p_val_dict)

                # Add this child's branch length sum to the clade's branch
                #    length sum
                bl_sum += child_bl_sum
                child_bl = child.edge_length

                # We will add this value to the branch length list for all of
                #    the tips in this clade.  It is the branch length of this
                #    clade divided by the number of tips in the clade.
                add_val = 1.0 * child_bl / len(child_bl_dict)

                # Process eac of the tips in the child_bl_dict
                for k, child_bl_k in child_bl_dict.items():
                    # The formula for calculating the p value is:
                    #    P(tip)(node) = (l1 + l2/2 + l3/3 + ... ln/n) / sum of
                    #        branch lengths to node
                    #    The value is arbitrarily set to be positive for one
                    #        child and negative for the other
                    #    The 'l' term is the length of a branch  and it is
                    #        divided by the number of tips that share that
                    #        branch.
                    tip_bls = child_bl_k + [add_val]

                    # Add the p value to p_vals_dict
                    clade_p_vals[k] = multiplier * sum(tip_bls) / child_bl_sum

                    # Add to bl_dict with this branch length
                    bl_dict[k] = tip_bls

            p_vals_dict[node.label] = clade_p_vals

        else:  # We are at a tip
            bl_dict = {self.labels.index(node.taxon.label): []}

        return bl_dict, bl_sum, p_vals_dict

    # ..............................
    def _build_p_matrix_no_branch_lengths(self):
        """Creates a P matrix when no branch lengths are present.

        Note:
            For this method, we assume that there is a total weight of -1 to
                the left and +1 to the right for each node.  As we go down
                (towards the tips) of the tree, we divide the proportion of
                each previously visited node by 2.  We then recurse with this
                new visited list down the tree.  Once we reach a tip, we can
                return that list of proportions because it will match for that
                tip for each of its ancestors.

        Example:
            3
            +-- 2
            |   +-- 1
            |   |   +-- 0
            |   |   |   +-- A
            |   |   |   +-- B
            |   |   |
            |   |   +-- C
            |   |
            |   +-- D
            |
            +--4
               +-- E
               +-- F

            Step 1: (Node 3) []
                - recurse left with [(3,-1)]
                - recurse right with [(3,1)]
            Step 2: (Node 2) [(3,-1)]
                - recurse left with [(3,-.5),(2,-1)]
                - recurse right with [(3,-.5),(2,1)]
            Step 3: (Node 1)[(3,-.5),(2,-1)]
                - recurse left with [(3,-.25),(2,-.5),(1,-1)]
                - recurse right with [3,-.25),(2,-.5),(1,1)]
            Step 4: (Node 0)[(3,-.25),(2,-.5),(1,-1)]
                - recurse left with [(3,-.125),(2,-.25),(1,-.5),(0,-1)]
                - recurse right with [(3,-.125),(2,-.25),(1,-.5),(0,1)]
            Step 5: (Tip A) - Return [(3,-.125),(2,-.25),(1,-.5),(0,-1)]
            Step 6: (Tip B) - Return [(3,-.125),(2,-.25),(1,-.5),(0,1)]
            Step 7: (Tip C) - Return [(3,-.25),(2,-.5),(1,1)]
            Step 8: (Tip D) - Return [(3,-.5),(2,1)]
            Step 9: (Node 4) [(3,1)]
                - recurse left with [(3,.5),(4,-1)]
                - recurse right with [(3,.5),(4,1)]
            Step 10: (Tip E) - Return [(3,.5),(4,-1)]
            Step 11: (Tip F) - Return [(3,.5),(4,1)]

            Creates matrix:
                     0     1     2      3       4
                A -1.0  -0.5  -0.25  -0.125   0.0
                B  1.0  -0.5  -0.25  -0.125   0.0
                C  0.0   1.0  -0.5   -0.25    0.0
                D  0.0   0.0   1.0   -0.5     0.0
                E  0.0   0.0   0.0    0.5    -1.0
                F  0.0   0.0   0.0    0.5     1.0

        See:
            Page 1293 of the literature.

        Returns:
            Matrix: An encoded phylogeny matrix.
        """
        # .......................
        # Initialize the matrix
        internal_node_labels = [n.label for n in self.tree.nodes() if not n.is_leaf()]

        # We need a mapping of node path id to matrix column.  I don't think
        #     order matters
        node_col_idx = dict(zip(internal_node_labels, range(len(internal_node_labels))))

        mtx = Matrix(
            np.zeros((len(self.labels), len(internal_node_labels)), dtype=float),
            headers={'0': self.labels, '1': internal_node_labels},
        )

        # Get the list of tip proportion lists
        # Note: Which tip each of the lists belongs to doesn't really matter
        #    but recursion will start at the top and go to the bottom of the
        #    tree tips.
        self.tree.seed_node._set_edge_length(0.0)
        tip_props = self._build_p_matrix_tip_proportion_list(
            self.tree.seed_node, visited=[]
        )

        # The matrix index of the tip in the PAM maps to the row index of P
        for row_idx, tip_prop in tip_props:
            for node_clade_id, val in tip_prop:
                mtx[row_idx][node_col_idx[node_clade_id]] = val

        return mtx

    # ..............................
    def _build_p_matrix_tip_proportion_list(self, node, visited=None):
        """Builds a list of tip proportions for the p matrix w/o branch lengths.

        Args:
            node (dendropy.Node): The current clade.
            visited (:obj:`None` or :obj:`list` of :obj:`tuple`): A list of
                (node path id, proportion) tuples.

        Note:
            Proportion for each visited node is divided by two as we go
                towards the tips at each hop.

        Returns:
            list: A list of tip proportions.
        """
        if visited is None:
            visited = []  # pragma: no cover

        tip_props = []
        if node.num_child_nodes() > 0:  # Assume this is two since binary
            # First divide all existing visited by two
            new_visited = [(idx, val / 2) for idx, val in visited]
            # Recurse.  Left is negative, right is positive
            left_child, right_child = node.child_nodes()
            tip_props.extend(
                self._build_p_matrix_tip_proportion_list(
                    left_child, visited=new_visited + [(node.label, -1.0)]
                )
            )
            tip_props.extend(
                self._build_p_matrix_tip_proportion_list(
                    right_child, visited=new_visited + [(node.label, 1.0)]
                )
            )
        else:
            tip_props.append((self.labels.index(node.taxon.label), visited))

        return tip_props

    # ..............................
    def _build_p_matrix_with_branch_lengths(self):
        """Creates a P matrix when branch lengths are present.

        Note:
            For this method, we assume that there is a total weight of -1 to
                the left and +1 to the right for each node.  As we go down
                (towards the tips) of the tree, we divide the proportion of
                each previously visited node by 2.  We then recurse with this
                new visited list down the tree.  Once we reach a tip, we can
                return that list of proportions because it will match for that
                tip for each of its ancestors.

        Example:
            3
            +-- 2 (0.4)
            |    +-- 1 (0.15)
            |    |    +-- 0 (0.65)
            |    |    |    +-- A (0.2)
            |    |    |    +-- B (0.2)
            |    |    |
            |    |    +-- C (0.85)
            |    |
            |    +-- D (1.0)
            |
            +-- 4 (0.9)
                 +-- E (0.5)
                 +-- F (0.5)

            Value for any cell (tip)(node) = (l1 + l2/2 + l3/3 + ... + ln/n) /
                                   (Sum of branch lengths in daughter clade)
            ln / n -> The length of branch n divided by the number of tips that
                descend from that clade

            P(A)(2) = (0.2 + 0.65/2 + 0.15/3) /
                        (0.2 + 0.2 + 0.65 + 0.85 + 0.15)
                    = (0.2 + 0.325 + 0.05) / (2.05)
                    = 0.575 / 2.05
                    = 0.280

            P(D)(3) = (1.0 + 0.4/4) / (.2 + .2 + .65 + .85 + .15 + 1.0 + .4)
                    = 1.1 / 3.45
                    = 0.319

            Creates matrix:
                    0         1       2       3       4
                A  -1.000  -0.500  -0.280  -0.196   0.000
                B   1.000  -0.500  -0.280  -0.196   0.000
                C   0.000   1.000  -0.439  -0.290   0.000
                D   0.000   0.000   1.000  -0.319   0.000
                E   0.000   0.000   0.000   0.500  -1.000
                F   0.000   0.000   0.000   0.500   1.000

        See:
            Literature supplemental material.

        Returns:
            Matrix: An encoded phylogeny matrix.
        """
        # We only need the P-values dictionary
        # TODO: Is there a better way to do this so the length of the r?
        self.tree.seed_node._set_edge_length(0.0)
        _, _, p_val_dict = self._build_p_branch_length_values(self.tree.seed_node)

        # Initialize the matrix
        mtx = Matrix(
            np.zeros((len(self.labels), len(p_val_dict)), dtype=float),
            headers={'0': self.labels, '1': list(p_val_dict.keys())},
        )

        # We need a mapping of node path id to matrix column.  I don't think
        #     order matters
        node_col_idx = dict(zip(p_val_dict.keys(), range(len(p_val_dict.keys()))))

        for node_clade_id, p_val_node_val in p_val_dict.items():
            for tip_mtx_idx, tip_p_vals in p_val_node_val.items():
                mtx[int(tip_mtx_idx)][node_col_idx[node_clade_id]] = tip_p_vals

        return mtx
