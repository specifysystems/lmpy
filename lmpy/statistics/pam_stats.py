"""Module containing base PAM statistic functionality."""
import numpy as np
from lmpy import Matrix


# .............................................................................
# Matric Decorators
# .............................................................................
class PamStatsMetric:
    """Base class for PAM statistics metrics.

    This wrapper is used to classify each statistic so that the arguments it
    needs can be inferred.
    """
    # .........................
    def __init__(self, func):
        """Constructor.
        """
        self.func = func
        self.__doc__ = self.func.__doc__

    # .........................
    def __call__(self, *args, **kwargs):
        # Do anything needed before calling the function
        ret = self.func(*args, **kwargs)
        # Do anything needed after the function
        return ret


# .............................................................................
class CovarianceMatrixMetric(PamStatsMetric):
    """
    """


# .............................................................................
class DiversityMetric(PamStatsMetric):
    """A single-value diversity metric."""


# .............................................................................
class _SiteStatMetric(PamStatsMetric):
    """A site-base statistic (do not use directly)."""


# .............................................................................
class _SpeciesStatMetric(PamStatsMetric):
    """A species-based statistic (do not use directly)."""


# .............................................................................
class SpeciesMatrixMetric(_SpeciesStatMetric):
    """A species-based statistic that is generated from a PAM."""


# .............................................................................
class SiteMatrixMetric(_SiteStatMetric):
    """A site-based metric that takes the PAM as input."""


# .............................................................................
class PamDistMatrixMetric(_SiteStatMetric):
    """A site-based metric computed from a PAM and Tree"""


# .............................................................................
class TreeMetric(_SiteStatMetric):
    """A site-based metric that takes a Dendropy tree as an argument."""


# .............................................................................
class TreeDistanceMatrixMetric(_SiteStatMetric):
    """A site-based metric that takes a distance matrix as an argument."""


# .............................................................................
# Site-based statistics
# .............................................................................
@SiteMatrixMetric
def alpha(pam):
    return pam.sum(axis=1)


# .............................................................................
@SiteMatrixMetric
def alpha_proportional(pam):
    """Calculate proportional alpha diversity."""
    return pam.sum(axis=1).astype(np.float) / num_species(pam)


# .............................................................................
@SiteMatrixMetric
def phi(pam):
    """"""
    return pam.dot(pam.sum(axis=0))


# .............................................................................
@SiteMatrixMetric
def phi_average_proportional(pam):
    """"""
    return pam.dot(omega(pam)).astype(np.float) / (num_sites(pam) * alpha(pam))


# .............................................................................
# Species metrics
# .............................................................................
@SpeciesMatrixMetric
def omega(pam):
    return pam.sum(axis=0)


# .............................................................................
@SpeciesMatrixMetric
def omega_proportional(pam):
    return pam.sum(axis=0).astype(float) / num_sites(pam)


# .............................................................................
@SpeciesMatrixMetric
def psi(pam):
    return pam.sum(axis=1).dot(pam)


# .............................................................................
@SpeciesMatrixMetric
def psi_average_proportional(pam):
    return alpha(pam
                 ).dot(pam).astype(np.float) / (num_species(pam) * omega(pam))


# .............................................................................
# Diversity metrics
# .............................................................................
@DiversityMetric
def schluter_species_variance_ratio(pam):
    sigma_species_ = sigma_species(pam)
    return float(sigma_species_.sum() / sigma_species_.trace())


# .............................................................................
@DiversityMetric
def schluter_site_variance_ratio(pam):
    sigma_sites_ = sigma_sites(pam)
    return float(sigma_sites_.sum() / sigma_sites_.trace())


# .............................................................................
@DiversityMetric
def num_sites(pam):
    """Get the number of sites with presences."""
    return np.sum(np.any(pam, axis=1))


# .............................................................................
@DiversityMetric
def num_species(pam):
    """Get the number of species with presences."""
    return np.sum(np.any(pam, axis=0))


# .............................................................................
@DiversityMetric
def whittaker(pam):
    return num_species(pam) / (pam.sum(axis=0).astype(float) / num_sites(pam))


# .............................................................................
@DiversityMetric
def lande(pam):
    return num_species(pam) - (
        pam.sum(axis=0).astype(float) / num_sites(pam)).sum()


# .............................................................................
@DiversityMetric
def legendre(pam):
    return omega(pam).sum() - (float((omega(pam) ** 2).sum()) / num_sites(pam))


# .............................................................................
@DiversityMetric
def c_score(pam):
    temp = 0.0
    # Cache these so we don't recompute
    omega_ = omega(pam)  # Cache so we don't waste computations
    num_species_ = num_species(pam)

    for i in range(num_species_):
        for j in range(i, num_species_):
            num_shared = len(np.where(np.sum(pam[:, [i, j]], axis=1) == 2)[0])
            p_1 = omega_[i] - num_shared
            p_2 = omega_[j] - num_shared
            temp += p_1 * p_2
    return 2 * temp / (num_species_ * (num_species_ - 1))


# .............................................................................
# Covariance metrics
# .............................................................................
@CovarianceMatrixMetric
def sigma_sites(pam):
    """
    """
    site_by_site = pam.dot(pam.T).astype(np.float)
    alpha_prop = alpha_proportional(pam)
    return (site_by_site / num_species(pam)) - np.outer(alpha_prop, alpha_prop)


# .............................................................................
@CovarianceMatrixMetric
def sigma_species(pam):
    """
    """
    species_by_site = pam.T.dot(pam).astype(np.float)
    omega_prop = omega_proportional(pam)
    return (species_by_site / num_sites(pam)
            ) - np.outer(omega_prop, omega_prop)


# .............................................................................
# Tree distance matrix metrics
# .............................................................................
@TreeDistanceMatrixMetric
def mean_nearest_taxon_distance(phylo_dist_mtx):
    """Calculates the nearest neighbor distance.
    """
    nearest_total = np.sum([np.min(row[row > 0.0]) for row in phylo_dist_mtx])
    return nearest_total / phylo_dist_mtx.shape[0]


# .............................................................................
@TreeDistanceMatrixMetric
def mean_pairwise_distance(phylo_dist_mtx):
    """Calculates mean pairwise distance

    Calculates mean pairwise distance between the species present at each site
    """
    num_sp = phylo_dist_mtx.shape[0]
    return (phylo_dist_mtx.sum() - phylo_dist_mtx.trace()
            ) / (num_sp * (num_sp - 1))


# .............................................................................
@TreeDistanceMatrixMetric
def sum_pairwise_distance(phylo_dist_mtx):
    """Calculates the sum pairwise distance for all species present at a site
    """
    return (phylo_dist_mtx.sum() - phylo_dist_mtx.trace()) / 2.0


# .............................................................................
@PamDistMatrixMetric
def pearson_correlation(pam, phylo_dist_mtx):
    """Calculates the Pearson correlation coef. for each site."""
    num_sites_ = pam.shape[0]
    pearson = np.zeros((num_sites_, 1), dtype=float)

    for site_idx in range(num_sites_):
        sp_idxs = np.where(pam[site_idx] == 1)[0]
        num_sp = len(sp_idxs)
        num_pairs = num_sp * (num_sp - 1) / 2
        if num_pairs >= 2:
            # Need at least 2 pairs
            pair_dist = []
            pair_sites_shared = []
            for i in range(num_sp - 1):
                for j in range(i + 1, num_sp):
                    pair_dist.append(phylo_dist_mtx[i, j])
                    pair_sites_shared.append(
                        pam[:, i].dot(pam[:, j]))
            # X : Pair distance
            # Y : Pair sites shared
            x_val = np.array(pair_dist)
            y_val = np.array(pair_sites_shared)
            sum_xy = np.sum(x_val * y_val)
            sum_x = np.sum(x_val)
            sum_y = np.sum(y_val)
            sum_x_sq = np.sum(x_val ** 2)
            sum_y_sq = np.sum(y_val ** 2)

            # Pearson
            p_num = sum_xy - sum_x * sum_y / num_pairs
            p_denom = np.sqrt(
                (sum_x_sq - (sum_x ** 2 / num_pairs)
                 ) * (sum_y_sq - (sum_y ** 2 / num_pairs)))
            pearson[site_idx, 0] = p_num / p_denom
    return pearson


# .............................................................................
@TreeMetric
def phylogenetic_diversity(tree):
    """Calculate phylogenetic diversity
    """
    return np.sum([node.edge_length for node in tree.nodes])


# .............................................................................
class PamStats:
    """Class for managing metric computation for PAM statistics."""
    covariance_stats = [
        ('sigma sites', sigma_sites),
        ('sigma species', sigma_species)
        ]
    diversity_stats = [
        ('c-score', c_score),
        ('lande', lande),
        ('legendre', legendre),
        ('num sites', num_sites),
        ('num species', num_species),
        ('whittaker', whittaker)
        ]
    site_matrix_stats = [
        ('alpha', alpha),
        ('alpha proportional', alpha_proportional),
        ('phi', phi),
        ('phi average proportional', phi_average_proportional),
        ]
    site_tree_stats = [('Phylogenetic Diversity', phylogenetic_diversity)]
    site_tree_distance_matrix_stats = [
        ('MNTD', mean_nearest_taxon_distance),
        ('Mean Pairwise Distance', mean_pairwise_distance),
        ('Sum Pairwise Distance', sum_pairwise_distance)]
    site_pam_dist_mtx_stats = [('pearson_correlation', pearson_correlation)]
    species_matrix_stats = [
        ('omega', omega),
        ('omega_proportional', omega_proportional),
        ('psi', psi),
        ('psi_average_proportional', psi_average_proportional)
        ]

    # ...........................
    def __init__(self, pam, tree=None):
        self.pam = pam
        self.tree = tree

    # ...........................
    def calculate_covariance_statistics(self):
        """Calculate covariance statistics matrices."""
        return [(name, func(self.pam)) for name, func in self.covariance_stats]

    # ...........................
    def calculate_diversity_statistics(self):
        """Calculate diversity statistics."""
        diversity_matrix = Matrix(
            np.array([stat[1](self.pam) for stat in self.diversity_stats]),
            headers={
                '0': ['value'],
                '1': [name for name, _ in self.diversity_stats]})
        return diversity_matrix

    # ...........................
    def calculate_site_statistics(self):
        """Calculate site-based statistics."""
        # Matrix based
        site_stats_matrix = Matrix(
            np.zeros((self.pam.shape[0], len(self.site_matrix_stats))),
            headers={
                '0': self.pam.get_row_headers(),
                '1': [name for name, _ in self.site_matrix_stats]})
        for i in range(len(self.site_matrix_stats)):
            site_stats_matrix[:, i] = self.site_matrix_stats[i][1](self.pam)

        if self.tree is not None:
            squid_annotations = self.tree.get_annotations('squid')
            squid_dict = {squid: label for label, squid in squid_annotations}
            ordered_labels = [
                squid_dict[squid] for squid in self.pam.get_column_headers()]

            site_tree_stats_matrix = Matrix(
                np.zeros((self.pam.shape[0], len(self.site_tree_stats))),
                headers={
                    '0': self.pam.get_row_headers(),
                    '1': [name for name, _ in self.site_tree_stats]})

            site_tree_dist_mtx_matrix = Matrix(
                np.zeros((self.pam.shape[0],
                          len(self.site_tree_distance_matrix_stats))),
                headers={
                    '0': self.pam.get_row_headers(),
                    '1': [name for name, _ in
                          self.site_tree_distance_matrix_stats]})

            # PAM / Tree stats
            phylo_dist_mtx = self.tree.get_distance_matrix()
            site_pam_tree_matrix = Matrix(
                Matrix.concatenate(
                    [func(self.pam, phylo_dist_mtx
                          ) for _, func in self.site_pam_dist_mtx_stats]),
                headers={
                    '0': self.pam.get_row_headers(),
                    '1': [name for name, _ in self.site_pam_dist_mtx_stats]})

            # Loop through PAM
            for site_idx, site_row in enumerate(self.pam):
                # Get present species
                present_species = np.where(site_row == 1)[0]

                # Get sub tree
                present_labels = [ordered_labels[i] for i in present_species]
                site_tree = self.tree.extract_tree_with_taxa_labels(
                    present_labels)
                # Get distance matrix
                site_dist_mtx = site_tree.get_distance_matrix()
                site_tree_dist_mtx_matrix[site_idx] = [
                    func(site_dist_mtx
                         ) for _, func in self.site_tree_distance_matrix_stats]
                site_tree_stats_matrix[site_idx] = [
                    func(site_tree) for _, func in self.site_tree_stats]

            site_stats_matrix = Matrix.concatenate(
                [site_stats_matrix, site_tree_stats_matrix,
                 site_tree_dist_mtx_matrix, site_pam_tree_matrix], axis=1)
        return site_stats_matrix

    # ...........................
    def calculate_species_statistics(self):
        """Calculate species-based statistics."""
        # Matrix based
        species_stats_matrix = Matrix(
            np.zeros((self.pam.shape[1], len(self.species_matrix_stats))),
            headers={
                '0': self.pam.get_column_headers(),
                '1': [name for name, _ in self.species_matrix_stats]})
        for i in range(len(self.species_matrix_stats)):
            species_stats_matrix[:, i] = \
                self.species_matrix_stats[i][1](self.pam)

        return species_stats_matrix

    # ...........................
    def register_metric(self, name, metric_function):
        """Register a new metric.

        Args:
            name (str): A name for this metric that will be used for a header.
            metric_function (function): A decorated metric generating function.
        """
        if isinstance(metric_function, CovarianceMatrixMetric):
            self.covariance_stats.append((name, metric_function))
        elif isinstance(metric_function, DiversityMetric):
            self.diversity_stats.append((name, metric_function))
        elif isinstance(metric_function, SiteMatrixMetric):
            self.site_matrix_stats.append((name, metric_function))
        elif isinstance(metric_function, TreeMetric):
            self.site_tree_stats.append((name, metric_function))
        elif isinstance(metric_function, TreeDistanceMatrixMetric):
            self.site_tree_distance_matrix_stats.append(
                (name, metric_function))
        elif isinstance(metric_function, PamDistMatrixMetric):
            self.site_pam_dist_mtx_stats.append((name, metric_function))
        elif isinstance(metric_function, SpeciesMatrixMetric):
            self.species_matrix_stats.append((name, metric_function))
        else:
            raise TypeError(
                'Unknown metric type: {}, {}'.format(name, metric_function))
