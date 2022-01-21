===========================================
Metacommunity Phylogenetics Analysis (MCPA)
===========================================

Introduction
============
We provide an implementation of the metacommunity phylogenetics analysis (MCPA)
from Liebold et al. 2010 that allows a researcher to study the effects of
environment and historical biogeography on the distributions of sister clades
in a phylogeny.  This analysis can be used to find significant correlations
between clade distributions and various environmental and biogeographic
predictors to determine if their distributions are limited by environmental
filtering, have vagility limited by historical biogeography, or a combination
of both.

The computation itself takes four matrix arguments, a site by species incidence
matrix (presence absence matrix), a tip by node encoded phylogenetic tree,
a site by environmental predictor matrix of environmental data, and a site by
biogeographic predictor matrix of Helmert contrasts for each biogeographic
hypothesis.

Leibold, M.A., E.P. Economo and P.R. Peres-Neto. 2010.
    Metacommunity phylogenetics: separating the roles of environmental filters and
    historical biogeography. Ecology Letters 13: 1290-1299.

----

Tutorial
========
For this simple tutorial, we will perform a single MCPA run using observed
data and will focus on the creation of the input matrices.  This example will
make use of the various encoding methods provided with lmpy but those steps
could be skipped if you already have a matrix representation of the needed
components.

.. code-block:: python

    from lmpy import Matrix
    from lmpy.data_preparation.layer_encoder import LayerEncoder
    from lmpy.data_preparation.tree_encoder import TreeEncoder
    from lmpy.statistics.mcpa import mcpa

    # Species distribution layers for PAM creation
    SDM_LAYER_FILENAMES = [
        'species_layer_1.tif',
        'species_layer_2.tif',
        'species_layer_3.tif',
        'species_layer_4.tif',
        'species_layer_5.tif',
        'species_layer_6.tif',
        'species_layer_7.tif',
        'species_layer_8.tif',
        'species_layer_9.tif'
    ]
    sdm_encoder = LayerEncoder()
    pam = sdm_encoder.encode_layers()

    # Encode a phylogenetic tree with species matching a PAM
    tree_filename = 'my_tree.nex'
    tree = TreeWrapper.get(path=tree_filename, schema='nexus')
    tree_encoder = TreeEncoder(pam, tree)
    phylo_matrix = tree_encoder.encode_phylogeny()

    # Encode environmental data
    ENVIRONMENT_LAYER_FILENAMES = [
        'env_layer_1.tif',
        'env_layer_2.tif',
        'env_layer_3.tif',
        'env_layer_4.tif',
        'env_layer_5.tif'
    ]
    env_encoder = LayerEncoder()
    env_mtx = env_encoder.encode_layers()

    # Encode biogeographic hypothesis data
    BIOGEO_LAYER_FILENAMES = [
        'bg_layer_1.shp',
        'bg_layer_2.shp',
        'bg_layer_3.shp',
        'bg_layer_4.shp'
    ]
    bg_encoder = LayerEncoder()
    bg_mtx = bg_encoder.encode_layers()

    mcpa(pam, phyl_mtx, env_mtx, bg_mtx)
