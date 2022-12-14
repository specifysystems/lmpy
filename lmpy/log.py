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


# .....................................................................................
def _log_level_str(log_level):
    if log_level == logging.INFO:
        level = 'INFO'
    elif log_level == logging.DEBUG:
        level = 'DEBUG'
    elif log_level in (logging.WARN, logging.WARNING):
        level = 'WARN'
    elif log_level == logging.ERROR:
        level = 'ERROR'
    elif log_level == logging.CRITICAL:
        level = 'CRITICAL'
    elif log_level == logging.FATAL:
        level = 'FATAL'
    return level


# .....................................................................................
def logit(logger, msg, refname="", log_level=logging.INFO):
    """Log or print a message.

    Args:
        logger (lmpy.log.Logger): A logger to use for logging output
        msg (str): A message to write to the logger.
        refname (str): Class or function name to use in logging message.
        log_level (int): A level to use when logging the message.
    """
    if logger is not None:
        logger.log(msg, refname=refname, log_level=log_level)
    else:
        level = _log_level_str(log_level)
        print(f"{refname} {level}: {msg}")
