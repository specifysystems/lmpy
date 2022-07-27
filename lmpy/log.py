"""Module containing standardized logging class for lmpy."""
import logging
import os
import sys

FORMAT = ' '.join(["%(asctime)s", "%(levelname)-8s", "%(message)s"])
DATE_FORMAT = "%d %b %Y %H:%M"


# .....................................................................................
class Logger:
    """Class containing a logger for consistent logging."""

    # .......................
    def __init__(
            self, logger_name, log_filename=None, log_console=False,
            log_level=logging.DEBUG):
        """Constructor.

        Args:
            logger_name (str): A name for the logger.
            log_filename (str): A file location to write logging information.
            log_console (bool): Should logs be written to the console.
            log_level (int): What level of logs should be retained.
        """
        self.logger = None
        self.name = logger_name
        self.filename = None
        self.log_console = log_console
        self.log_level = log_level

        handlers = []
        if log_filename is not None:
            self.filename = log_filename
            os.makedirs(os.path.dirname(log_filename), exist_ok=True)
            handlers.append(logging.FileHandler(log_filename, mode="w"))
        if self.log_console:
            handlers.append(logging.StreamHandler(stream=sys.stdout))

        if len(handlers) > 0:
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(logging.DEBUG)

            formatter = logging.Formatter(FORMAT, DATE_FORMAT)
            for handler in handlers:
                handler.setLevel(self.log_level)
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
            self.logger.propagate = False

    # ........................
    def log(self, msg, refname="", log_level=logging.INFO):
        """Log a message.

        Args:
            msg (str): A message to write to the logger.
            refname (str): Class or function name to use in logging message.
            log_level (int): A level to use when logging the message.
        """
        if self.logger is not None:
            self.logger.log(log_level, refname + ': ' + msg)
