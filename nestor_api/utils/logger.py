"""A simple logger implementation awaiting for proper implementation"""

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s-%(asctime)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
)


class Logger:
    """A logger module"""

    @staticmethod
    def debug(context=None, message=""):
        """Produce a log with debug level

        Args:
            context (dict): An object with relevant information for debugging
            message (str): Additional message for context/debugging
        """
        if context is None:
            logging.debug(message)
        else:
            logging.debug("%s %s", message, json.dumps(context))

    @staticmethod
    def info(context=None, message=""):
        """Produce a log with info level

        Args:
            context (dict): An object with relevant information for debugging
            message (str): Additional message for context/debugging
        """
        if context is None:
            logging.info(message)
        else:
            logging.info("%s %s", message, json.dumps(context))

    @staticmethod
    def warn(context=None, message=""):
        """Produce a log with warn level

        Args:
            context (dict): An object with relevant information for debugging
            message (str): Additional message for context/debugging
        """
        if context is None:
            logging.warning(message)
        else:
            logging.warning("%s %s", message, json.dumps(context))

    @staticmethod
    def error(context=None, message=""):
        """Produce a log with error level

        Args:
            context (dict): An object with relevant information for debugging
            message (str): Additional message for context/debugging
        """
        if context is None:
            logging.error(message, exc_info=True)
        else:
            logging.error("%s %s", message, json.dumps(context), exc_info=True)
