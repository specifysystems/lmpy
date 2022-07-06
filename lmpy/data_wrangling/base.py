"""Module containing base class for data wranglers."""
import logging


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
            logger (logging.Logger): An optional logger to use for logging output.
            **kwargs (dict): Dictionary of parameters.
        """
        self.report = {}
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
        self.report['name'] = self.name
        self.report['version'] = self.version
        return self.report

    # ........................
    def log(self, msg, log_level=logging.INFO):
        """Log a message.

        Args:
            msg (str): A message to write to the logger.
            log_level (int): A level to use when logging the message.
        """
        if self.logger is not None:
            # wrangler_message = self.name + ': ' + msg
            wrangler_message = 'test_dupes: ' + msg
            print("Printing", wrangler_message, f"Propagate is {self.logger.propagate}; {len(self.logger.handlers)} handlers", )
            self.logger.log(log_level, wrangler_message)
            # log_func = {
            #     logging.DEBUG: self.logger.debug,
            #     logging.INFO: self.logger.info,
            #     logging.WARNING: self.logger.warning,
            #     logging.ERROR: self.logger.error,
            #     logging.CRITICAL: self.logger.critical,
            # }
            # wrangler_message = self.name + ': ' + msg
            # if log_level in log_func.keys():
            #     log_func[log_level](wrangler_message)
            # else:
            #     self.logger.log(log_level, wrangler_message)
