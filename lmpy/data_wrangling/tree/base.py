"""Module containing Tree Data Wrangler base class."""
from lmpy.data_wrangling.base import _DataWrangler


# .....................................................................................
class _TreeDataWrangler(_DataWrangler):
    """Tree data wrangler base class."""
    name = '_TreeDataWrangler'

    # .......................
    def __init__(self):
        """Constructor for _OcccurrenceDataWrangler base class."""
        pass

    # .......................
    @classmethod
    def from_config_dict(cls, config_dict):
        """Build an instance from a configuration dictionary.

        Args:
            config_dict (dict): A dictionary of instance parameters.

        Returns:
            _TreeDataWrangler: A configured Tree data wrangler.
        """
        raise NotImplementedError('Not implemented for base class')
