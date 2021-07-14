==============
PAM Statistics
==============

Introduction
============
The PAM data structure can be used to generate many diversity statistics.  By
default, many of the statistics presented in Soberon and Cavner, 2015 are
generated as well as some phylogenetic diversity metrics if a tree is provided.
Additionally, new statistics can be created by decorating functions with the
appropriate statistic type and adding them to the stats instance.

----

Generating Default Statistics
=============================
You can generate the base statistics without any special configuration of a
PamStats instance.  Simply supply the PAM and optionally a tree then request
the category of statistics you would like to be returned.

.. code-block:: python

    >>> stats = PamStats(pam, tree=my_tree)
    >>> site_stats = stats.calculate_site_statistics()
    >>> species_stats = stats.calculate_species_statistics()
    >>> diversity_stats = stats.calculate_diversity_statistics()

----

Adding New Statistics
=====================
It is fairly simple at add new metrics to the computations.  The first step is
to identify which class of metrics the new metric belongs to, this will
determine how the metric is called within the statistics package and what the
expected output is.

For example, if we wanted to add a metric that computed the sum of tip lengths
for the species present at a site, we would need the tree of those species as
input and we would produce a single value for each site.  This maps to
`TreeMetric` and so we can define our function with a tree as input and add the
`TreeMetric` decorator.

See: `register_metric <../autoapi/lmpy/statistics/pam_stats/index.html#lmpy.statistics.pam_stats.PamStats.register_metric>`_

.. code-block:: python

    @TreeMetric
    def sum_tip_lengths(tree):
        tip_length_sum = 0
        for node in tree.nodes():
            if node.is_leaf():
                tip_length_sum += node.edge_length
         return tip_length_sum

Then we can register this new metric with the statistics package and it will
automatically be calculated at the appropriate time with the appropriate
inputs.

.. code-block:: python

    >>> stats = PamStats(pam, tree=tree)
    >>> stats.register_metric('Sum tip lengths', sum_tip_lengths)
    >>> site_stats = stats.calculate_site_statistics()

----

Covariance Matrix Metrics
=========================
Covariance matrix metrics take a PAM as input and produce a site by site or
species by species matrix of metric values.

sigma_sites
-----------
Matrix of covariance of composition of sites.
:math:`\mathbf{\Sigma}_{sites}(j,k) = \frac{1}{S}\sum_{i=1}^{S}\delta_{j,l}\delta_{k,l} - \frac{\alpha_j\alpha_k}{S^2}`

sigma_species
-------------
Matrix of covariance of ranges of species.
:math:`\mathbf{\Sigma}_{species}(h,i) = \frac{1}{N}\sum_{j=i}^{N}\delta_{i,j}\delta_{h,j} - \frac{\omega_i\omega_h}{N^2}`

----

Diversity Metrics
=================
Diversity metrics take a PAM as input and produce a single metric value for the
entire study.

schluter_species_variance_ratio
-------------------------------
Schluter species-ranges covariance.
:math:`V_{species} = \frac{\bar{\psi}^* - N /\beta_W^2}{1/\beta_W - \bar{\varphi}^* / S}`

schluter_site_variance_ratio
----------------------------
Schluter sites-composition covariance.
:math:`V_{sites} = \frac{\bar{\varphi}^* - S /\beta_W^2}{1/\beta_W - \bar{\psi}^* / N}`

num_sites
---------
Num sites is the total number of sites in the study area that have any species
present.

num_species
-----------
Num species is the total number of species in the study that are present at any
site.

whittaker
---------
Whittaker's multaplicative beta diversity metric for a PAM.
:math:`\beta_W = \frac{1}{\bar{\omega}^{*}}`

lande
-----
Lande is Lande's addative beta diversity metric for a PAM.
:math:`\beta_A = S(1 - 1/\beta_W)`

legendre
--------
Legendre is Legendre's beta diversity metric for a PAM.
:math:`\beta_L = SS(\mathbf{X}) = SN / \beta_W - \left (\sum_{j=1}^{S}\omega_j^2 \right ) / N`

c_score
-------
C-score is the Stone & Robers checkerboard score for the PAM.
:math:`C = \frac{2}{S(S-1)}\left [ \sum_{i=1}^{N} \sum_{h<i}(\omega_i - \omega_{i,h})(\omega_h - \omega_{i,h}) \right ]`

----

Species Matrix Metrics
======================
Species matrix metrics take a PAM as input and return a column of metric values
for each species in the study.

omega
-----
Omega is the range size for each species.

omega_proportional
------------------
Omega proportional is the range size of each species as a proportion of the
total number of sites.
:math:`\omega_i^* = \frac{\bar{\rho}_i}{\bar{\psi}_i^* - \beta_W^{-1}}`

psi
---
Psi is the range richness of each species.
:math:`\psi_j = \sum_{i=1}^{N}\delta_{i,j} \alpha_i`

psi_average_proportional
------------------------
Psi average proportional is the mean proportional species diversity.

----

Site Matrix Metrics
===================
Site matrix metrics take a PAM as input and return a column of values for each
site in the study area.

alpha
-----
Alpha diversity is the number of species present at each site.

alpha_proportional
------------------
Alpha proportional diversity is the ratio of the number of species present at
each site to the total number of species in the entire study area.
:math:`\alpha_j^* = \frac{\tau_j}{\bar{\varphi}_j^*-\beta_W^{-1}}`

phi
---
Phi is the sum of the range size of the species present at each site.
:math:`\varphi_i = \sum_{j=1}^{S}\delta_{i,j} \omega_j`

phi_average_proportional
------------------------
Phy average proportional is the mean proportional range size of the species
present at each site.

----

PAM Distance Matrix Metrics
===========================
PAM distance matrix metrics are site-based metrics generated using a PAM and a
distance matrix for the tree over the entire study area.  These statistics
return a single column of values for each site.

pearson_correlation
-------------------
Pearson correlation is the pearson correlation coefficient for each site.

----

Tree Metrics
============
Tree metrics are site-based metrics generated from a phylogenetic tree that
only contains tips for species present at a site.  These metrics return a
single value for the current site.

phylogenetic_diversity
----------------------
Phylogenetic diversity is the sum of all of the branch lengths in the tree that
only contains species present at a site.

----

Tree Distance Matrix Metrics
============================
Tree distance matrix metrics are site-based statistics generated from a species
by species distance matrix for the species present at a particular site.  A
single value is returned for these metrics for the current site.

mean_nearest_taxon_distance
---------------------------
Mean nearest taxon distance, or MNTD, is the mean of the distance from each tip
to the closest tip to it for a tree of all species present at a site.

mean_pairwise_distance
----------------------
Mean pairwise distance, or MPD, is the mean of the distances of each tip to all
other tips in the tree of species present at a site.

sum_pairwise_distance
---------------------
Sum pairwise distance is the sum of the distances from each tip to all other
tips in a tree of the species present at a site.
