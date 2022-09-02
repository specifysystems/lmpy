"""Module containing base class for data wranglers."""


# .....................................................................................
class _DataWrangler:
    """Data wrangler base class."""
    name = '_DataWrangler'
    version = '1.0'

    # ........................
    def __init__(self, *args, logger=None, **kwargs):
        """Base class constructor.

        Args:
            *args (tuple): Positional arguments.
            logger (lmpy.log.Logger): An optional local logger to use for logging output
                with consistent options
            **kwargs (dict): Dictionary of parameters.
        """
        self.report = {
            'name': self.name,
            'version': self.version
        }
        self.logger = logger

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
        return self.report
