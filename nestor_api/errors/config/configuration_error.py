"""Custom errors"""


class ConfigurationError(Exception):
    """Raised when an error is encountered during the configuration resolution."""

    def __init__(self, path: str, message: str):
        super().__init__(f"Invalid configuration: {path}: {message}")
        self.path = path
        self.message = message
