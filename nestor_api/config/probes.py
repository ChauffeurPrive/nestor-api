"""Probes default configuration"""

import os


class ProbesDefaultConfiguration:
    """Probes default configuration"""

    @staticmethod
    def get_default_delay():
        """Returns the probes default delay"""
        return int(os.getenv("NESTOR_PROBES_DEFAULT_DELAY", "30"))

    @staticmethod
    def get_default_period():
        """Returns the probes default period"""
        return int(os.getenv("NESTOR_PROBES_DEFAULT_PERIOD", "10"))

    @staticmethod
    def get_default_timeout():
        """Returns the probes default timeout"""
        return int(os.getenv("NESTOR_PROBES_DEFAULT_TIMEOUT", "1"))
