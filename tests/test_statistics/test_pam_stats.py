"""This module tests the lmpy.statistics.pam_stats.py module.

Note:
    * These test functions are pytest style tests for the pam_stats.py module.
"""
import numpy as np
import pytest

from lmpy import Matrix, TreeWrapper
from lmpy.statistics.pam_stats import PamStats


# .............................................................................
def get_random_pam_and_tree(num_species, num_sites, fill_percentage,
                            max_branch_length):
    """Get a random PAM and matching tree.

    Args:
        num_species (int): The number of species in the PAM / Tree.
        num_sites (int): The number of sites in the PAM.
        fill_percentage (float): The percentage of cells that are present in
            the PAM.
        max_branch_length (float): The maximum branch length for each branch in
            the tree.
    """
    site_headers = [
        'Site {}'.format(site_idx) for site_idx in range(num_sites)]
    species_names = [
        'Species {}'.format(sp_idx) for sp_idx in range(num_species)]
    pam = Matrix(
        (np.random.random((num_sites, num_species)) < fill_percentage
         ).astype(np.int),
        headers={'0': site_headers, '1': species_names})
    tree = TreeWrapper.get(
        data='({});'.format(
            ','.join([sp.replace(' ', '_') for sp in species_names])),
        schema='newick')
    tree.resolve_polytomies()
    for node in tree.nodes():
        node.edge_length = np.random.random() * max_branch_length
    return (pam, tree)


# .............................................................................
class Test_PamStats:
    """Test the PamStats class."""
    # ............................
    def test_simple(self):
        pam, tree = get_random_pam_and_tree(10, 10, .3, 1.0)
        ps = PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()
