"""Custom error"""


class InvalidConfigurationKeyReference(Exception):
    """Raised when a configuration file contains invalid references"""

    def __init__(self, variable_name: str):
        super().__init__(f'Referenced variable "{variable_name}" should be a string')
