"""Custom Errors for Nestor Config Validator"""


class InvalidTargetPathError(Exception):
    """Exception raised when the target path (NESTOR_CONFIG_PATH) env is not set"""

    def __init__(self, target_path: str):
        super().__init__(
            f"The environment variable NESTOR_CONFIG_PATH is not set. Current value: ${target_path}"
        )


class ConfigurationNotValidError(Exception):
    """Exception raised when a configuration is invalid"""

    def __init__(self, validation_errors):
        self.validation_errors = validation_errors
        self.message = "Please fix the configuration with the help of the validationErrors property"
        super().__init__(self.validation_errors)

    def __str__(self):
        return f"{self.message} -> {self.validation_errors}"
