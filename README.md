# lmpy

[![Latest release](https://img.shields.io/github/release/lifemapper/lmpy.svg)](
https://github.com/specifysystems/lmpy/releases/latest)
[![PyPI version](https://badge.fury.io/py/specify-lmpy.svg)](
https://badge.fury.io/py/specify-lmpy)
[![Python Versions](https://img.shields.io/pypi/pyversions/specify-lmpy)](
https://img.shields.io/pypi/pyversions/specify-lmpy)
[![License Badge](https://img.shields.io/github/license/lifemapper/lmpy.svg)](
https://github.com/specifysystems/lmpy/blob/main/LICENSE)

[![PyPI download month](https://img.shields.io/pypi/dm/specify-lmpy.svg)](
https://pypi.python.org/pypi/specify-lmpy/)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/specifysystems/lmpy.svg?logo=lgtm&logoWidth=18
)](https://lgtm.com/projects/g/specifysystems/lmpy/alerts/)
[![Language grade: Python](
https://img.shields.io/lgtm/grade/python/g/specifysystems/lmpy.svg?logo=lgtm&logoWidth=18
)](https://lgtm.com/projects/g/specifysystems/lmpy/context:python)

[![Build Status](https://github.com/specifysystems/lmpy/workflows/PyTest%20with%20Conda/badge.svg)](
https://github.com/specifysystems/lmpy/actions)
[![GitHub issues](https://img.shields.io/github/issues/specifysystems/lmpy.svg)](
https://GitHub.com/specifysystems/lmpy/issues/)
[![Average time to resolve an issue](
http://isitmaintained.com/badge/resolution/specifysystems/lmpy.svg)](
http://isitmaintained.com/project/specifysystems/lmpy "Average time to resolve an issue")
[![Coverage Status](
https://coveralls.io/repos/github/specifysystems/lmpy/badge.svg?branch=main)](
https://coveralls.io/github/specifysystems/lmpy?branch=main)

[![Documentation Status](https://readthedocs.org/projects/specify-lmpy/badge/?version=latest)](http://specify-lmpy.readthedocs.io/?badge=latest)

[![Open Source Love svg3](https://badges.frapsoft.com/os/v3/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

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

Please see [CITATION.cff](./CITATION.cff) for citing the repository or the
specify-lmpy tool itself.

Tutorials and additional documentation can be found on
[The lmpy GitHub pages](https://specifysystems.github.io/lmpy/).

This work has been supported by NSF  Awards NSF BIO-1458422, OCI-1234983. BIO/CIBR-1930005
