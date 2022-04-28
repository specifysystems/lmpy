"""Module containing base PAM statistic functionality."""
import numpy as np
from lmpy import Matrix


# .............................................................................
# Metric Decorators
# .............................................................................
class PamStatsMetric:
    """Base class for PAM statistics metrics.

    This wrapper is used to classify each statistic so that the arguments it
    needs can be inferred.
    """

    # .........................
    def __init__(self, func):
        """Constructor.

        Args:
            func: The function to call.
        """
        self.func = func
        self.__doc__ = self.func.__doc__

    # .........................
    def __call__(self, *args, **kwargs):
        """Call the wrapped function.

        Args:
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.

        Returns:
            object: The output of the wrapped function.
        """
        # Do anything needed before calling the function
        ret = self.func(*args, **kwargs)
        # Do anything needed after the function
        return ret


# .............................................................................
class CovarianceMatrixMetric(PamStatsMetric):
    """A metric that produces a covariance matrix."""


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
    """A site-based metric computed from a PAM and Tree."""


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
    """Calculate alpha diversity, the number of species in each site.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A column of alpha diversity values for each site in the PAM.
    """
    return pam.sum(axis=1)


# .............................................................................
@SiteMatrixMetric
def alpha_proportional(pam):
    """Calculate proportional alpha diversity.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A column of proportional alpha diversity values for each site in the
            PAM.
    """
    return pam.sum(axis=1).astype(float) / num_species(pam)


# .............................................................................
@SiteMatrixMetric
def phi(pam):
    """Calculate phi, the range size per site.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A column of the sum of the range sizes for the species present at each
            site in the PAM.
    """
    return pam.dot(pam.sum(axis=0))


# .............................................................................
@SiteMatrixMetric
def phi_average_proportional(pam):
    """Calculate proportional range size per site.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A column of the proportional value of the sum of the range sizes for
            the species present at each site in the PAM.
    """
    return pam.dot(omega(pam)).astype(float) / (num_sites(pam) * alpha(pam))


# .............................................................................
# Species metrics
# .............................................................................
@SpeciesMatrixMetric
def omega(pam):
    """Calculate the range size per species.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A row of range sizes for each species in the PAM.
    """
    return pam.sum(axis=0)


# .............................................................................
@SpeciesMatrixMetric
def omega_proportional(pam):
    """Calculate the mean proportional range size of each species.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A row of the proportional range sizes for each species in the PAM.
    """
    return pam.sum(axis=0).astype(float) / num_sites(pam)


# .............................................................................
@SpeciesMatrixMetric
def psi(pam):
    """Calculate the range richness of each species.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A row of range richness for the sites that each species is present in.
    """
    return pam.sum(axis=1).dot(pam)


# .............................................................................
@SpeciesMatrixMetric
def psi_average_proportional(pam):
    """Calculate the mean proportional species diversity.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: A row of proportional range richness for the sites that each species in
            the PAM is present.
    """
    return alpha(pam).dot(pam).astype(float) / (num_species(pam) * omega(pam))


# .............................................................................
# Diversity metrics
# .............................................................................
@DiversityMetric
def schluter_species_variance_ratio(pam):
    """Calculate Schluter's species variance ratio.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: The Schluter species variance ratio for the PAM.
    """
    sigma_species_ = sigma_species(pam)
    return float(sigma_species_.sum() / sigma_species_.trace())


# .............................................................................
@DiversityMetric
def schluter_site_variance_ratio(pam):
    """Calculate Schluter's site variance ratio.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: The Schluter site variance ratio for the PAM.
    """
    sigma_sites_ = sigma_sites(pam)
    return float(sigma_sites_.sum() / sigma_sites_.trace())


# .............................................................................
@DiversityMetric
def num_sites(pam):
    """Get the number of sites with presences.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        int: The number of sites that have present species.
    """
    return int(np.sum(np.any(pam, axis=1)))


# .............................................................................
@DiversityMetric
def num_species(pam):
    """Get the number of species with presences.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        int: The number of species that are present in at least one site.
    """
    return int(np.sum(np.any(pam, axis=0)))


# .............................................................................
@DiversityMetric
def whittaker(pam):
    """Calculate Whittaker's beta diversity metric for a PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: Whittaker's beta diversity for the PAM.
    """
    return float(num_species(pam) / omega_proportional(pam).sum())


# .............................................................................
@DiversityMetric
def lande(pam):
    """Calculate Lande's beta diversity metric for a PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: Lande's beta diversity for the PAM.
    """
    return float(
        num_species(pam) - (pam.sum(axis=0).astype(float) / num_sites(pam)).sum()
    )


# .............................................................................
@DiversityMetric
def legendre(pam):
    """Calculate Legendre's beta diversity metric for a PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: Legendre's beta diversity for the PAM.
    """
    return float(omega(pam).sum() - (float((omega(pam) ** 2).sum()) / num_sites(pam)))


# .............................................................................
@DiversityMetric
def c_score(pam):
    """Calculate the checker board score for the PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        float: The checkerboard score for the PAM.
    """
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
    """Compute the site sigma metric for a PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: Matrix of covariance of composition of sites.
    """
    site_by_site = pam.dot(pam.T).astype(float)
    alpha_prop = alpha_proportional(pam)
    return (site_by_site / num_species(pam)) - np.outer(alpha_prop, alpha_prop)


# .............................................................................
@CovarianceMatrixMetric
def sigma_species(pam):
    """Compute the species sigma metric for a PAM.

    Args:
        pam (Matrix): The presence-absence matrix to use for the computation.

    Returns:
        Matrix: Matrix of covariance of composition of species.
    """
    species_by_site = pam.T.dot(pam).astype(float)
    omega_prop = omega_proportional(pam)
    return (species_by_site / num_sites(pam)) - np.outer(omega_prop, omega_prop)


# .............................................................................
# Tree distance matrix metrics
# .............................................................................
@TreeDistanceMatrixMetric
def mean_nearest_taxon_distance(phylo_dist_mtx):
    """Calculates the nearest neighbor distance.

    Args:
        phylo_dist_mtx (Matrix): A matrix of distances between the species present at a
            site.

    Returns:
        float: The average distance from each taxa to taxa nearest to it.
    """
    try:
        nearest_total = np.sum([np.min(row[row > 0.0]) for row in phylo_dist_mtx])
        return float(nearest_total / phylo_dist_mtx.shape[0])
    except Exception:  # pragma: no cover
        return 0.0


# .............................................................................
@TreeDistanceMatrixMetric
def mean_pairwise_distance(phylo_dist_mtx):
    """Calculates mean pairwise distance between species present at a site.

    Args:
        phylo_dist_mtx (Matrix): A matrix of distances between the species present at a
            site.

    Returns:
        float: The average distance from each taxa all of the other co-located taxa.
    """
    num_sp = phylo_dist_mtx.shape[0]
    return float(
        (phylo_dist_mtx.sum() - phylo_dist_mtx.trace()) / (num_sp * (num_sp - 1))
    )


# .............................................................................
@TreeDistanceMatrixMetric
def sum_pairwise_distance(phylo_dist_mtx):
    """Calculates the sum pairwise distance for all species present at a site.

    Args:
        phylo_dist_mtx (Matrix): A matrix of distances between the species present at a
            site.

    Returns:
        float: The total distance from each taxa all of the other co-located taxa.
    """
    return float((phylo_dist_mtx.sum() - phylo_dist_mtx.trace()) / 2.0)


# .............................................................................
@PamDistMatrixMetric
def pearson_correlation(pam, phylo_dist_mtx):
    """Calculates the Pearson correlation coefficient for each site.

    Args:
        pam (Matrix): A presence-absence matrix to use for the computation.
        phylo_dist_mtx (Matrix): A matrix of distance between species.

    Returns:
        Matrix: A column of Pearson correlation values for each site in a PAM.
    """
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
                    pair_sites_shared.append(pam[:, i].dot(pam[:, j]))
            # X : Pair distance
            # Y : Pair sites shared
            x_val = np.array(pair_dist)
            y_val = np.array(pair_sites_shared)
            sum_xy = np.sum(x_val * y_val)
            sum_x = np.sum(x_val)
            sum_y = np.sum(y_val)
            sum_x_sq = np.sum(x_val**2)
            sum_y_sq = np.sum(y_val**2)

            # Pearson
            p_num = sum_xy - sum_x * sum_y / num_pairs
            p_denom = np.sqrt(
                (sum_x_sq - (sum_x**2 / num_pairs))
                * (sum_y_sq - (sum_y**2 / num_pairs))
            )
            pearson[site_idx, 0] = p_num / p_denom
    return pearson


# .............................................................................
@TreeMetric
def phylogenetic_diversity(tree):
    """Calculate phylogenetic diversity of a tree.

    Args:
        tree (TreeWrapper): A phylogenetic tree to compute phylogenetic diversity for.

    Returns:
        float: The sum of the edge lengths of the nodes of the provided tree.
    """
    try:
        return np.sum([node.edge_length for node in tree.nodes()])
    except Exception:  # pragma: no cover
        return 0.0


# .............................................................................
class PamStats:
    """Class for managing metric computation for PAM statistics."""

    covariance_stats = [('sigma sites', sigma_sites), ('sigma species', sigma_species)]
    diversity_stats = [
        ('c-score', c_score),
        ('lande', lande),
        ('legendre', legendre),
        ('num sites', num_sites),
        ('num species', num_species),
        ('whittaker', whittaker),
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
        ('Sum Pairwise Distance', sum_pairwise_distance),
    ]
    site_pam_dist_mtx_stats = [('pearson_correlation', pearson_correlation)]
    species_matrix_stats = [
        ('omega', omega),
        ('omega_proportional', omega_proportional),
        ('psi', psi),
        ('psi_average_proportional', psi_average_proportional),
    ]

    # ...........................
    def __init__(
            self,
            pam,
            tree=None,
            tree_matrix=None,
            node_heights_matrix=None,
            tip_lengths_matrix=None,
    ):
        """Constructor for PAM stats computations.

        Args:
            pam (Matrix): A presence-absence matrix to use for computations.
            tree (TreeWrapper): A tree to use for phylogenetic distance computations.
            tree_matrix (Matrix): A matrix of tip / node presence absence values.
            node_heights_matrix (Matrix): A matrix of node height values.
            tip_lengths_matrix (Matrix): A matrix of tip length values.
        """
        self.pam = pam
        self.tree = tree
        self.tree_matrix = tree_matrix
        self.node_heights_matrix = node_heights_matrix
        self.tip_lengths_matrix = tip_lengths_matrix

    # ...........................
    def calculate_covariance_statistics(self):
        """Calculate covariance statistics matrices.

        Returns:
            list of tuple: A list of metric name, value tuples for covariance stats.
        """
        return [(name, func(self.pam)) for name, func in self.covariance_stats]

    # ...........................
    def calculate_diversity_statistics(self):
        """Calculate diversity statistics.

        Returns:
            list of tuple: A list of metric name, value tuples for diversity metrics.
        """
        print([func(self.pam) for _, func in self.diversity_stats])
        diversity_matrix = Matrix(
            np.array([func(self.pam) for _, func in self.diversity_stats]),
            headers={'0': ['value'], '1': [name for name, _ in self.diversity_stats]},
        )
        return diversity_matrix

    # ...........................
    def calculate_site_statistics(self):
        """Calculate site-based statistics.

        Returns:
            Matrix: A matrix of site-based statistics for the selected metrics.
        """
        # Matrix based
        print('Start')
        site_stats_matrix = Matrix(
            np.zeros((self.pam.shape[0], len(self.site_matrix_stats))),
            headers={
                '0': self.pam.get_row_headers(),
                '1': [name for name, _ in self.site_matrix_stats],
            },
        )
        print('Site matrix stats')
        for i in range(len(self.site_matrix_stats)):
            site_stats_matrix[:, i] = self.site_matrix_stats[i][1](self.pam)

        if self.tree is not None:
            print('Tree stuff')
            squid_annotations = self.tree.get_annotations('squid')
            squid_dict = {squid: label for label, squid in squid_annotations}
            ordered_labels = []
            for squid in self.pam.get_column_headers():
                if squid in squid_dict.keys():
                    v = squid_dict[squid]
                else:  # pragma: no cover
                    v = ''
                ordered_labels.append(v)

            site_tree_stats_matrix = Matrix(
                np.zeros((self.pam.shape[0], len(self.site_tree_stats))),
                headers={
                    '0': self.pam.get_row_headers(),
                    '1': [name for name, _ in self.site_tree_stats],
                },
            )

            site_tree_dist_mtx_matrix = Matrix(
                np.zeros(
                    (self.pam.shape[0], len(self.site_tree_distance_matrix_stats))
                ),
                headers={
                    '0': self.pam.get_row_headers(),
                    '1': [name for name, _ in self.site_tree_distance_matrix_stats],
                },
            )

            # PAM / Tree stats
            print('Get distance matrix')
            phylo_dist_mtx = self.tree.get_distance_matrix()
            print('PAM dist mtx stats')
            site_pam_tree_matrix = None
            if self.site_pam_dist_mtx_stats:
                site_pam_tree_matrix = Matrix(
                    Matrix.concatenate(
                        [
                            func(self.pam, phylo_dist_mtx)
                            for _, func in self.site_pam_dist_mtx_stats
                        ]
                    ),
                    headers={
                        '0': self.pam.get_row_headers(),
                        '1': [name for name, _ in self.site_pam_dist_mtx_stats],
                    },
                )

            print('Site by site')
            # Loop through PAM
            for site_idx, site_row in enumerate(self.pam):
                # Get present species
                present_species = np.where(site_row == 1)[0]

                # Get sub tree
                present_labels = list(
                    filter(
                        lambda x: bool(x), [ordered_labels[i] for i in present_species]
                    )
                )
                present_dist_mtx_idxs = []
                for idx, label in enumerate(phylo_dist_mtx.get_column_headers()):
                    if label in present_labels:
                        present_dist_mtx_idxs.append(idx)
                try:
                    if present_labels:
                        site_tree = self.tree.extract_tree_with_taxa_labels(
                            present_labels
                        )
                        # Get distance matrix
                        site_dist_mtx = phylo_dist_mtx.slice(
                            present_dist_mtx_idxs, present_dist_mtx_idxs
                        )
                        # site_dist_mtx = site_tree.get_distance_matrix()
                        site_tree_dist_mtx_matrix[site_idx] = [
                            func(site_dist_mtx)
                            for (_, func) in self.site_tree_distance_matrix_stats
                        ]
                        site_tree_stats_matrix[site_idx] = [
                            func(site_tree) for _, func in self.site_tree_stats
                        ]
                except Exception as err:  # pragma: no cover
                    print(err)
                    print(present_labels)
                    print('Site index: {}'.format(site_idx))

            all_stat_matrices = []
            if site_stats_matrix is not None:
                all_stat_matrices.append(site_stats_matrix)
            if site_tree_stats_matrix is not None:
                all_stat_matrices.append(site_tree_stats_matrix)
            if site_tree_dist_mtx_matrix is not None:
                all_stat_matrices.append(site_tree_dist_mtx_matrix)
            if site_pam_tree_matrix is not None:
                all_stat_matrices.append(site_pam_tree_matrix)

            site_stats_matrix = Matrix.concatenate(all_stat_matrices, axis=1)
        return site_stats_matrix

    # ...........................
    def calculate_species_statistics(self):
        """Calculate species-based statistics.

        Returns:
            Matrix: A matrix of species-based statistics for the selected metrics.
        """
        # Matrix based
        species_stats_matrix = Matrix(
            np.zeros((self.pam.shape[1], len(self.species_matrix_stats))),
            headers={
                '0': self.pam.get_column_headers(),
                '1': [name for name, _ in self.species_matrix_stats],
            },
        )
        for i in range(len(self.species_matrix_stats)):
            species_stats_matrix[:, i] = self.species_matrix_stats[i][1](self.pam)

        return species_stats_matrix

    # ...........................
    def register_metric(self, name, metric_function):
        """Register a new metric.

        Args:
            name (str): A name for this metric that will be used for a header.
            metric_function (function): A decorated metric generating function.

        Raises:
            TypeError: Raised if the metric function type cannot be processed.
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
            self.site_tree_distance_matrix_stats.append((name, metric_function))
        elif isinstance(metric_function, PamDistMatrixMetric):
            self.site_pam_dist_mtx_stats.append((name, metric_function))
        elif isinstance(metric_function, SpeciesMatrixMetric):
            self.species_matrix_stats.append((name, metric_function))
        else:
            raise TypeError('Unknown metric type: {}, {}'.format(name, metric_function))


# .............................................................................
__all__ = [
    'CovarianceMatrixMetric',
    'DiversityMetric',
    'PamDistMatrixMetric',
    'PamStats',
    'PamStatsMetric',
    'SiteMatrixMetric',
    'SpeciesMatrixMetric',
    'TreeDistanceMatrixMetric',
    'TreeMetric',
    'alpha',
    'alpha_proportional',
    'c_score',
    'lande',
    'legendre',
    'mean_nearest_taxon_distance',
    'mean_pairwise_distance',
    'num_sites',
    'num_species',
    'omega',
    'omega_proportional',
    'pearson_correlation',
    'phi',
    'phi_average_proportional',
    'phylogenetic_diversity',
    'psi',
    'psi_average_proportional',
    'schluter_site_variance_ratio',
    'schluter_species_variance_ratio',
    'sigma_sites',
    'sigma_species',
    'sum_pairwise_distance',
    'whittaker',
]
