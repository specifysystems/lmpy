# lmpy.statistics

The statistics module contains submodules and tools for performing statistical
analyses.  There are some specialty analyses in [mcpa](mcpa.py) and
[pam stats](./pam_stats.py) and some general tools for statistical analysis in
[running_stats](./running_stats.py).

* **mcpa** MetaCommunity Phylogenetics Analysis (MCPA) brings together species
  distributions, with a phylogenetic tree of those species, and geospatial
  environmental values for the region of interest.  MCPA analyses reveal the
  relationships between the evolutionary paths of species, their distribution, and
  geospatial (i.e. geological, geographical) elements of the landscape.
* **pam_stats**: define different accepted measures and comparisons for a PAM matrix.
* **running_stats**: compute common values and objects used for computing a variety of
  matrix statistics, to avoid repeating common computations and reduce memory usage.

