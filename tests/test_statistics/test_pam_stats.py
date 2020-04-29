"""This module tests the lmpy.statistics.pam_stats.py module.

Note:
    * These test functions are pytest style tests for the pam_stats.py module.
"""
import numpy as np
import pytest

from lmpy import Matrix, TreeWrapper
import lmpy.statistics.pam_stats as stats


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
    tree.annotate_tree_tips('squid', {sp: sp for sp in species_names})
    return (pam, tree)


# .............................................................................
class Test_Metrics:
    """Test various individual metrics."""
    # ............................
    def test_covariance_metrics(self):
        """Test the covariance metrics."""
        pam, _ = get_random_pam_and_tree(10, 20, .3, 1.0)
        sigma_sites = stats.sigma_sites(pam)
        assert sigma_sites.shape == (20, 20)

        sigma_species = stats.sigma_species(pam)
        assert sigma_species.shape == (10, 10)

    # ............................
    def test_diversity_metrics(self):
        """Test the diversity metrics."""
        pam, _ = get_random_pam_and_tree(10, 20, .3, 1.0)
        metrics = [
            ('c-score', stats.c_score),
            ('lande', stats.lande),
            ('legendre', stats.legendre),
            ('num sites', stats.num_sites),
            ('num species', stats.num_species),
            ('whittaker', stats.whittaker)
            ]
        for name, func in metrics:
            print(name)
            metric = func(pam)
            assert isinstance(metric, (int, float))

    # ............................
    def test_site_matrix_metrics(self):
        """Test site metrics that take a matrix as input."""
        pam, _ = get_random_pam_and_tree(10, 20, .3, 1.0)
        metrics = [
            ('alpha', stats.alpha),
            ('alpha proportional', stats.alpha_proportional),
            ('phi', stats.phi),
            ('phi average proportional', stats.phi_average_proportional),
            ]
        for name, func in metrics:
            print(name)
            metric = func(pam)
            assert metric.shape == (20,)

    # ............................
    def test_site_tree_stats(self):
        """Test site metrics that take a tree as input."""
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        metrics = [('Phylogenetic Diversity', stats.phylogenetic_diversity)]
        labels = pam.get_column_headers()
        for name, func in metrics:
            print(name)
            for row in pam:
                present_labels = [labels[i] for i in np.where(row == 1)[0]]
                if present_labels:
                    slice_tree = tree.extract_tree_with_taxa_labels(
                        present_labels)
                    metric = func(slice_tree)
                    assert isinstance(metric, (int, float))

    # ............................
    def test_site_tree_distance_matrix_stats(self):
        """Test site metrics that take a distance matrix as input."""
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        metrics = [
            ('MNTD', stats.mean_nearest_taxon_distance),
            ('Mean Pairwise Distance', stats.mean_pairwise_distance),
            ('Sum Pairwise Distance', stats.sum_pairwise_distance)]
        labels = pam.get_column_headers()
        for name, func in metrics:
            print(name)
            for row in pam:
                present_labels = [labels[i] for i in np.where(row == 1)[0]]
                if present_labels:
                    slice_tree = tree.extract_tree_with_taxa_labels(
                        present_labels)
                    slice_dist_mtx = slice_tree.get_distance_matrix()
                    metric = func(slice_dist_mtx)
                    assert isinstance(metric, (int, float))

    # ............................
    def test_site_pam_dist_matrix_stats(self):
        """Test site metrics that take a PAM and distance matrix as input."""
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        dist_mtx = tree.get_distance_matrix()
        metrics = [('pearson_correlation', stats.pearson_correlation)]
        for name, func in metrics:
            print(name)
            metric = func(pam, dist_mtx)
            assert metric.shape == (20, 1)

    # ............................
    def test_species_matrix_metrics(self):
        """Test species metrics"""
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        metrics = [
            ('omega', stats.omega),
            ('omega_proportional', stats.omega_proportional),
            ('psi', stats.psi),
            ('psi_average_proportional', stats.psi_average_proportional)]
        for name, func in metrics:
            print(name)
            metric = func(pam)
            assert metric.shape == (10,)


# .............................................................................
class Test_PamStats:
    """Test the PamStats class."""
    # ............................
    def test_simple(self):
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

    # ............................
    def test_add_metric(self):
        pam, tree = get_random_pam_and_tree(10, 20, .3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        # Remove all metrics
        ps.covariance_stats = []
        ps.diversity_stats = []
        ps.site_matrix_stats = []
        ps.site_tree_stats = []
        ps.site_tree_distance_matrix_stats = []
        ps.site_pam_dist_mtx_stats = []
        ps.species_matrix_stats = []

        # Register all of the metrics
        reg_metrics = [
            ('sigma sites', stats.sigma_sites),
            ('sigma species', stats.sigma_species),
            ('c-score', stats.c_score),
            ('lande', stats.lande),
            ('legendre', stats.legendre),
            ('num sites', stats.num_sites),
            ('num species', stats.num_species),
            ('whittaker', stats.whittaker),
            ('alpha', stats.alpha),
            ('alpha proportional', stats.alpha_proportional),
            ('phi', stats.phi),
            ('phi average proportional', stats.phi_average_proportional),
            ('Phylogenetic Diversity', stats.phylogenetic_diversity),
            ('MNTD', stats.mean_nearest_taxon_distance),
            ('Mean Pairwise Distance', stats.mean_pairwise_distance),
            ('Sum Pairwise Distance', stats.sum_pairwise_distance),
            ('pearson_correlation', stats.pearson_correlation),
            ('omega', stats.omega),
            ('omega_proportional', stats.omega_proportional),
            ('psi', stats.psi),
            ('psi_average_proportional', stats.psi_average_proportional)
            ]
        ps.register_metric(
            'schluter_site_variance', stats.schluter_site_variance_ratio)
        ps.register_metric(
            'schluter_species_variance', stats.schluter_species_variance_ratio)
        for name, func in reg_metrics:
            ps.register_metric(name, func)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

        with pytest.raises(TypeError):
            ps.register_metric('bad_metric', int)
