# lmpy

[![Latest release](https://img.shields.io/github/release/lifemapper/lmpy.svg)](
https://github.com/specifysystems/lmpy/releases/latest)
[![Build Status](https://travis-ci.com/lifemapper/lmpy.svg?branch=master)](
https://travis-ci.com/specifysystems/lmpy)
[![Coverage Status](https://coveralls.io/repos/github/lifemapper/lmpy/badge.svg)](
https://coveralls.io/github/lifemapper/lmpy)
[![License Badge](https://img.shields.io/github/license/lifemapper/lmpy.svg)](
https://github.com/specifysystems/lmpy/blob/master/LICENSE)

The Lifemapper lmpy repository houses objects and common tools used within the
Lifemapper installation that may also be useful for outside contributors and
the community as a whole.

Any community contributed tool through the
[BiotaPhy Python Repository](https://github.com/biotaphy/BiotaPhyPy/) should
use these objects to ensure that the new analysis is compatible with the
Lifemapper backend.

We have also made our PAM randomization code available so that those
researchers that don't need or want to use the entire Lifemapper system can
create their own null models for large matrices that are not currently possible
with other existing software pacakges.  This repository will serve as the
reference end-point for citations to our randomization method and the latest
version of this code will live in this repository.

Please use the following with citing our randomization algorithm:

    Grady, C. J., Beach, J. H., and Stewart, A. M. (in preparation). A parallel,
    heuristic-based fill method for creating presence-absence matrix randomizations.

Tutorials and additional documentation can be found on
[The lmpy GitHub pages](https://specifysystems.github.io/lmpy/).

This work has been supported by NSF  Awards NSF BIO-1458422, OCI-1234983. BIO/CIBR-1930005
