"""This module tests the lmpy.statistics.mcpa.py module."""
import numpy as np

from lmpy import Matrix, TreeWrapper
from lmpy.data_preparation.tree_encoder import TreeEncoder
from lmpy.statistics.mcpa import get_p_values, mcpa


ROUND_POSITION = 7


# .............................................................................
def _make_ultrametric_helper(species, max_branch_length):
    """Helper function for creating an ultrametric tree.

    Args:
        species (list): List of species to include in the tree.
        max_branch_length (numeric): Maximum branch length.

    Returns:
        tuple: Tuple of tree root node and height of the node.
    """
    # If length of list == 1, bounce
    if species and len(species) == 1:
        node = species[0].replace(' ', '_')
        node_height = 0.0
    else:
        # Split and recurse
        if len(species) > 2:
            split_pos = np.random.randint(1, len(species) - 1)
        else:
            split_pos = 1
        node_a, node_height_a = _make_ultrametric_helper(
            species[:split_pos], max_branch_length
        )
        node_b, node_height_b = _make_ultrametric_helper(
            species[split_pos:], max_branch_length
        )
        # Get the maximum node height and add this branch length
        node_height = round(
            max(node_height_a, node_height_b)
            + (max_branch_length * np.random.random()),
            ROUND_POSITION,
        )
        # Make sure node heights are equal for each branch by subtracting
        #    from node height
        node = '({}:{},{}:{})'.format(
            node_a, node_height - node_height_a, node_b, node_height - node_height_b
        )
    # Return branch and height
    return (node, node_height)


# .............................................................................
def _get_random_pam_and_tree(
    num_species, num_sites, fill_percentage, max_branch_length, num_mismatches=0
):
    """Get a random PAM and matching tree.

    Args:
        num_species (int): The number of species in the PAM / Tree.
        num_sites (int): The number of sites in the PAM.
        fill_percentage (float): The percentage of cells that are present in the PAM.
        max_branch_length (float): The maximum branch length for each branch in the
            tree.
        num_mismatches (int): A number of mismatches to include between PAM and tree.

    Returns:
        tuple: A tuple of the presence-absence Matrix and the associated TreeWrapper.
    """
    site_headers = ['Site {}'.format(site_idx) for site_idx in range(num_sites)]
    pam_species = []
    tree_species = []
    for sp_idx in range(num_species):
        sp = 'Species{}'.format(sp_idx)
        pam_species.append(sp)
        tree_species.append(sp)

    # Add a few species to PAM species and tree species
    for sp_idx in range(num_mismatches):
        pam_species.append('PamSpecies {}'.format(sp_idx))
        tree_species.append('TreeSpecies {}'.format(sp_idx))

    np.random.shuffle(pam_species)
    np.random.shuffle(tree_species)

    pam = Matrix(
        (np.random.random((num_sites, num_species)) < fill_percentage).astype(int),
        headers={'0': site_headers, '1': pam_species},
    )

    if max_branch_length:
        tree_data = '{};'.format(
            _make_ultrametric_helper(tree_species, max_branch_length)[0]
        )
    else:
        tmp = []
        tmp.extend(tree_species)
        while len(tmp) > 1:
            sp_1 = tmp.pop()
            sp_2 = tmp.pop()
            tmp.append('({},{})'.format(sp_1, sp_2))
        tree_data = '{};'.format(tmp[0])
    tree = TreeWrapper.get(data=tree_data, schema='newick')
    tree.annotate_tree_tips('squid', {sp: sp for sp in tree_species})
    tree.annotate_tree_tips('mx', {sp: idx for idx, sp in enumerate(pam_species)})
    return (pam, tree)


# .............................................................................
def _create_env_and_biogeo_matrices(pam, num_env_cols, num_bg_cols):
    """Create environment and bio geo matrices matching pam sites.

    Args:
        pam (Matrix): A presence-absence Matrix.
        num_env_cols (int): The number of environment layers to generate.
        num_bg_cols (int): The number of biogeographic hypotheses to generate.

    Returns:
        tuple: A tuple of enviroment Matrix and biogeo hypotheses Matrix.
    """
    bg_mtx = Matrix(
        np.random.randint(-1, 2, (pam.shape[0], num_bg_cols)),
        headers={
            '0': pam.get_row_headers(),
            '1': ['BG - {}'.format(i) for i in range(num_bg_cols)],
        },
    )
    env_mtx = Matrix(
        np.random.uniform(0.0, 100.0, (pam.shape[0], num_env_cols)),
        headers={
            '0': pam.get_row_headers(),
            '1': ['Env - {}'.format(i) for i in range(num_env_cols)],
        },
    )
    return (env_mtx, bg_mtx)


# .............................................................................
class Test_mcpa:
    """Test various individual metrics."""

    # ............................
    def test_mcpa_with_branch_lengths(self):
        """Test MCPA with branch lengths."""
        # Need PAM, Encoded tree, Env matrix, BG matrix
        pam, tree = _get_random_pam_and_tree(10, 20, 0.3, 1.0)
        phylo_mtx = TreeEncoder(tree, pam).encode_phylogeny()
        env_mtx, bg_mtx = _create_env_and_biogeo_matrices(pam, 10, 3)
        mcpa(pam, phylo_mtx, env_mtx, bg_mtx)

    # ............................
    def test_mcpa_no_branch_lengths(self):
        """Test MCPA no branch lengths."""
        # Need PAM, Encoded tree, Env matrix, BG matrix
        pam, tree = _get_random_pam_and_tree(10, 20, 0.3, None)
        phylo_mtx = TreeEncoder(tree, pam).encode_phylogeny()
        env_mtx, bg_mtx = _create_env_and_biogeo_matrices(pam, 10, 3)
        mcpa(pam, phylo_mtx, env_mtx, bg_mtx)


# .............................................................................
class Test_get_p_values:
    """Test the get_p_values method.

    Note:
        Deprecate this in favor of using running stats version.
    """

    # ............................
    def test_single_permutation(self):
        """Test with a single test permutation."""
        obs_mtx = Matrix(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
        test_mtx = Matrix(
            np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]]).reshape((3, 3, 1))
        )
        p_vals = get_p_values(obs_mtx, [test_mtx])[:, :, 0]
        p_test_mtx = Matrix(np.array([[1, 1, 1], [1, 1, 0], [0, 0, 0]]))
        assert np.all(p_vals == p_test_mtx)

    # ............................
    def test_single_permutation_3dim(self):
        """Test with a single test permutation."""
        obs_mtx = Matrix(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
        test_mtx = Matrix(np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]]))
        p_vals = get_p_values(obs_mtx, [test_mtx])[:, :, 0]
        p_test_mtx = Matrix(np.array([[1, 1, 1], [1, 1, 0], [0, 0, 0]]))
        assert np.all(p_vals == p_test_mtx)

    # ............................
    def test_multiple_permutations(self):
        """Test with multiple test permutations."""
        obs_mtx = Matrix(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
        test_mtxs = [
            Matrix(np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]])),
            Matrix(np.array([[5, 5, 5], [5, 5, 5], [5, 5, 5]])),
            Matrix(np.array([[3, 3, 3], [6, 6, 6], [8, 8, 8]])),
            Matrix(np.array([[3, 2, 1], [6, 5, 4], [9, 8, 7]])),
        ]
        p_vals = get_p_values(obs_mtx, test_mtxs, num_permutations=len(test_mtxs))[
            :, :, 0
        ]
        p_test_mtx = Matrix(np.array([[1, 1, 0.75], [1, 1, 0.25], [0.5, 0.5, 0]]))
        assert np.all(p_vals == p_test_mtx)
