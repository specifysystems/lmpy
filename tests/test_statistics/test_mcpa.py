"""This module tests the lmpy.statistics.mcpa.py module.

Note:
    * These test functions are pytest style tests
"""
from random import randint, random, shuffle
import time

import numpy as np
import pytest

from lmpy import Matrix, TreeWrapper
from lmpy.data_preparation.tree_encoder import TreeEncoder
from lmpy.statistics.mcpa import mcpa


ROUND_POSITION = 7


# .............................................................................
def _make_ultrametric_helper(species, max_branch_length):
    # If length of list == 1, bounce
    if species and len(species) == 1:
        node = species[0].replace(' ', '_')
        node_height = 0.0
    else:
        # Split and recurse
        split_pos = randint(1, len(species) - 1)
        node_a, node_height_a = _make_ultrametric_helper(
            species[:split_pos], max_branch_length)
        node_b, node_height_b = _make_ultrametric_helper(
            species[split_pos:], max_branch_length)
        # Get the maximum node height and add this branch length
        node_height = round(
            max(node_height_a, node_height_b) + (
                max_branch_length * random()), ROUND_POSITION)
        # Make sure node heights are equal for each branch by subtracting
        #    from node height
        node = '({}:{},{}:{})'.format(
            node_a, node_height - node_height_a, node_b,
            node_height - node_height_b)
    # Return branch and height
    return (node, node_height)


# .............................................................................
def _get_random_pam_and_tree(num_species, num_sites, fill_percentage,
                             max_branch_length, num_mismatches=0):
    """Get a random PAM and matching tree.

    Args:
        num_species (int): The number of species in the PAM / Tree.
        num_sites (int): The number of sites in the PAM.
        fill_percentage (float): The percentage of cells that are present in
            the PAM.
        max_branch_length (float): The maximum branch length for each branch in
            the tree.
        num_mismatches (int): A number of mismatches to include between PAM and
            tree.
    """
    site_headers = [
        'Site {}'.format(site_idx) for site_idx in range(num_sites)]
    pam_species = []
    tree_species = []
    for sp_idx in range(num_species):
        sp = 'Species {}'.format(sp_idx)
        pam_species.append(sp)
        tree_species.append(sp)

    # Add a few species to PAM species and tree species
    for sp_idx in range(num_mismatches):
        pam_species.append('PamSpecies {}'.format(sp_idx))
        tree_species.append('TreeSpecies {}'.format(sp_idx))

    shuffle(pam_species)
    shuffle(tree_species)

    pam = Matrix(
        (np.random.random((num_sites, num_species)) < fill_percentage
         ).astype(np.int),
        headers={'0': site_headers, '1': pam_species})

    tree_data = '({});'.format(
        _make_ultrametric_helper(tree_species, max_branch_length)[0])
    tree = TreeWrapper.get(data=tree_data, schema='newick')
    tree.annotate_tree_tips('squid', {sp: sp for sp in tree_species})
    return (pam, tree)


# .............................................................................
def _create_env_and_biogeo_matrices(pam, num_env_cols, num_bg_cols):
    """Create environment and bio geo matrices matching pam sites."""
    bg_mtx = Matrix(
        np.random.randint(-1, 2, (pam.shape[0], num_bg_cols)),
        headers={
            '0': pam.get_row_headers(),
            '1': ['BG - {}'.format(i) for i in range(num_bg_cols)]})
    env_mtx = Matrix(
        np.random.uniform(0.0, 100.0, (pam.shape[0], num_env_cols)),
        headers={
            '0': pam.get_row_headers(),
            '1': ['Env - {}'.format(i) for i in range(num_env_cols)]})
    return (env_mtx, bg_mtx)


# .............................................................................
class Test_MCPA:
    """Test various individual metrics."""
    # ............................
    def test_mcpa(self):
        """Test MCPA"""
        # Need PAM, Encoded tree, Env matrix, BG matrix
        pam, tree = _get_random_pam_and_tree(10, 20, .3, 1.0)
        phylo_mtx = TreeEncoder(tree, pam).encode_phylogeny()
        env_mtx, bg_mtx = _create_env_and_biogeo_matrices(pam, 10, 3)
        mcpa(pam, phylo_mtx, env_mtx, bg_mtx)
