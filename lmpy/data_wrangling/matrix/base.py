"""Module containing Matrix Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _MatrixDataWrangler(_DataWrangler):
    """Matrix data wrangler base class."""
    name = '_MatrixDataWrangler'

    # .......................
    def __init__(self):
        """Constructor for _MatrixDataWrangler base class."""
        pass

    # .......................
    @classmethod
    def from_config_dict(cls, config_dict):
        """Build an instance from a configuration dictionary.

        Args:
            config_dict (dict): A dictionary of instance parameters.

        Returns:
            _MatrixDataWrangler: A configured occurrence data wrangler.
        """
        raise NotImplementedError('Not implemented for base class')
