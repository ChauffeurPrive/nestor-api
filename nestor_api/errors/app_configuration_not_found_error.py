"""Custom error"""


class AppConfigurationNotFoundError(FileNotFoundError):
    """Raised when a configuration file is missing for an app"""

    def __init__(self, app_name: str):
        super().__init__(f"Configuration file not found for app: {app_name}")
