"""Custom error"""

from typing import List

from .configuration_error import ConfigurationError


class AggregatedConfigurationError(Exception):
    """Raised when errors are encountered while resolving the configuration.
    It contains an aggregation of all encountered errors.
    """

    def __init__(self, errors: List[ConfigurationError]):
        super().__init__("Invalid configuration")
        self.errors = errors
