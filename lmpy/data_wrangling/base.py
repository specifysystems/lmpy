"""Module containing base class for data wranglers."""
from collections import namedtuple


# .....................................................................................
class _DataWrangler:
    """Data wrangler base class."""
    name = '_DataWrangler'
    version = '1.0'

    # ........................
    @classmethod
    def from_config(cls, config):
        """Get an instance generated from the provided configuration.

        Args:
            config (dict): A dictionary of configuration parameters.

        Returns:
            _DataWrangler: The instance created from the parameters.
        """
        return cls(**config)

    # ........................
    def get_report(self):
        """Get a report of the results of the wrangler.

        Returns:
            dict: A dictionary of reporting information.
        """
        return {
            'name': self.name,
            'version': self.version
        }
