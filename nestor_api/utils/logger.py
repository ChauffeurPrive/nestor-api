"""A simple logger implementation awaiting for proper implementation"""


class Logger:
    """A fake logger module to be able to collect logs later on"""

    @staticmethod
    def debug(context: dict, message: str):
        """Produce a log with debug level"""

    @staticmethod
    def error(context: dict, message: str):
        """Produce a log with error level"""

    @staticmethod
    def info(context: dict, message: str):
        """Produce a log with info level"""

    @staticmethod
    def warn(context: dict, message: str):
        """Produce a log with warn level"""
