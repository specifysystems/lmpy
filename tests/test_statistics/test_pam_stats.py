"""This module tests the lmpy.statistics.pam_stats.py module."""
import numpy as np
import pytest

from lmpy import Matrix, TreeWrapper
import lmpy.statistics.pam_stats as stats


ROUND_POSITION = 7


# .............................................................................
def _make_ultrametric_helper(species, max_branch_length):
    """Helper function for generating an ultrametric tree.

    Args:
        species (list): List of species to include.
        max_branch_length (numeric): The maximum branch length for this branch.

    Returns:
        tuple: A tuple of a tree root node and the height.
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
def get_random_pam_and_tree(
    num_species, num_sites, fill_percentage, max_branch_length, num_mismatches=0
):
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

    Returns:
        tuple: Return a tuple of the PAM matrix and the tree generated.
    """
    site_headers = ['Site {}'.format(site_idx) for site_idx in range(num_sites)]
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

    np.random.shuffle(pam_species)
    np.random.shuffle(tree_species)

    pam = Matrix(
        (np.random.random((num_sites, num_species)) < fill_percentage).astype(int),
        headers={'0': site_headers, '1': pam_species},
    )

    tree_data = '({});'.format(
        _make_ultrametric_helper(tree_species, max_branch_length)[0]
    )
    tree = TreeWrapper.get(data=tree_data, schema='newick')
    tree.annotate_tree_tips('squid', {sp: sp for sp in tree_species})
    return (pam, tree)


# .............................................................................
class Test_Metrics:
    """Test various individual metrics."""

    # ............................
    def test_covariance_metrics(self):
        """Test the covariance metrics."""
        pam, _ = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        sigma_sites = stats.sigma_sites(pam)
        assert sigma_sites.shape == (20, 20)

        sigma_species = stats.sigma_species(pam)
        assert sigma_species.shape == (10, 10)

    # ............................
    def test_diversity_metrics(self):
        """Test the diversity metrics."""
        pam, _ = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        metrics = [
            ('c-score', stats.c_score),
            ('lande', stats.lande),
            ('legendre', stats.legendre),
            ('num sites', stats.num_sites),
            ('num species', stats.num_species),
            ('whittaker', stats.whittaker),
        ]
        for name, func in metrics:
            print(name)
            metric = func(pam)
            assert isinstance(metric, (int, float))

    # ............................
    def test_site_matrix_metrics(self):
        """Test site metrics that take a matrix as input."""
        pam, _ = get_random_pam_and_tree(10, 20, 0.3, 1.0)
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
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        metrics = [('Phylogenetic Diversity', stats.phylogenetic_diversity)]
        labels = pam.get_column_headers()
        for name, func in metrics:
            print(name)
            for row in pam:
                present_labels = [labels[i] for i in np.where(row == 1)[0]]
                if present_labels:
                    slice_tree = tree.extract_tree_with_taxa_labels(present_labels)
                    metric = func(slice_tree)
                    assert isinstance(metric, (int, float))

    # ............................
    def test_site_tree_distance_matrix_stats(self):
        """Test site metrics that take a distance matrix as input."""
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        metrics = [
            ('MNTD', stats.mean_nearest_taxon_distance),
            ('Mean Pairwise Distance', stats.mean_pairwise_distance),
            ('Sum Pairwise Distance', stats.sum_pairwise_distance),
        ]
        labels = pam.get_column_headers()
        for name, func in metrics:
            print(name)
            for row in pam:
                present_labels = [labels[i] for i in np.where(row == 1)[0]]
                if present_labels:
                    slice_tree = tree.extract_tree_with_taxa_labels(present_labels)
                    slice_dist_mtx = slice_tree.get_distance_matrix()
                    metric = func(slice_dist_mtx)
                    assert isinstance(metric, (int, float))

    # ............................
    def test_site_pam_dist_matrix_stats(self):
        """Test site metrics that take a PAM and distance matrix as input."""
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        dist_mtx = tree.get_distance_matrix()
        metrics = [('pearson_correlation', stats.pearson_correlation)]
        for name, func in metrics:
            print(name)
            metric = func(pam, dist_mtx)
            assert metric.shape == (20, 1)

    # ............................
    def test_species_matrix_metrics(self):
        """Test species metrics."""
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        metrics = [
            ('omega', stats.omega),
            ('omega_proportional', stats.omega_proportional),
            ('psi', stats.psi),
            ('psi_average_proportional', stats.psi_average_proportional),
        ]
        for name, func in metrics:
            print(name)
            metric = func(pam)
            assert metric.shape == (10,)


# .............................................................................
class Test_PamStats:
    """Test the PamStats class."""

    # ............................
    def test_simple(self):
        """Perform simple PAM stats computations."""
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

    # ............................
    def test_add_metric(self):
        """Test adding metrics to the statistics computations."""
        pam, tree = get_random_pam_and_tree(10, 20, 0.3, 1.0)
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
            ('psi_average_proportional', stats.psi_average_proportional),
        ]
        ps.register_metric('schluter_site_variance', stats.schluter_site_variance_ratio)
        ps.register_metric(
            'schluter_species_variance', stats.schluter_species_variance_ratio
        )
        for name, func in reg_metrics:
            ps.register_metric(name, func)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

        with pytest.raises(TypeError):
            ps.register_metric('bad_metric', int)

    # ............................
    def test_medium_matrix(self):
        """Test species metrics."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

    # ............................
    def test_medium_matrix_with_mismatches(self):
        """Test species metrics."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0, num_mismatches=10)
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

    # ............................
    def test_medium_matrix_with_mismatches_and_empty_row_cols(self):
        """Test species metrics."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0, num_mismatches=10)
        for i in np.random.randint(0, 100, (10,)):
            pam[:, i] = np.zeros((200,))
        for i in np.random.randint(0, 200, (10,)):
            pam[i, :] = np.zeros((100,))
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_covariance_statistics()
        ps.calculate_diversity_statistics()
        ps.calculate_site_statistics()
        ps.calculate_species_statistics()

    # ............................
    def test_empty_stat_types_site_matrix_stats(self):
        """Test removing all stats for type."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.site_matrix_stats = []
        ps.calculate_site_statistics()

    # ............................
    def test_empty_stat_types_site_tree_stats(self):
        """Test removing all stats for type."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.site_tree_stats = []
        ps.calculate_site_statistics()

    # ............................
    def test_empty_stat_types_site_tree_matrix_stats(self):
        """Test removing all stats for type."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.site_tree_distance_matrix_stats = []
        ps.calculate_site_statistics()

    # ............................
    def test_empty_stat_types_site_pam_dist_matrix_stats(self):
        """Test removing all stats for type."""
        pam, tree = get_random_pam_and_tree(100, 200, 0.3, 1.0)
        ps = stats.PamStats(pam, tree=tree)
        ps.site_pam_dist_mtx_stats = []
        ps.calculate_site_statistics()

    # ............................
    def test_single_double_tree_subsetting(self):
        """Tests for sites with one or two sites present."""
        pam, tree = get_random_pam_and_tree(5, 5, 0.2, 2.0)
        pam[0] = [1, 1, 0, 0, 0]
        pam[1] = [0, 0, 1, 0, 0]
        ps = stats.PamStats(pam, tree=tree)
        ps.calculate_site_statistics()
