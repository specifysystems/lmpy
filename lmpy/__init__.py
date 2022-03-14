"""Base init module."""
# flake8: noqa
from . import matrix
from . import randomize
from . import tree
from .matrix import *
from .tree import *
from .point import Point
from . import data_preparation
from . import data_wrangling
from . import spatial
from . import statistics
from . import tools

__all__ = [
    'data_preparation',
    'data_wrangling',
    'randomize',
    'spatial',
    'statistics',
    'tools',
]
__all__.extend(matrix.__all__)
__all__.extend(tree.__all__)

from . import _version

__version__ = _version.get_versions()['version']
