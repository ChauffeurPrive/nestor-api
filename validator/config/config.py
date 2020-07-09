"""Nestor config validator configuration"""

from enum import Enum
import os


class Configuration:
    """Nestor_config_validator configuration"""

    @staticmethod
    def get_target_path():
        """Returns the target path of the project configuration"""
        return os.getenv("NESTOR_CONFIG_PATH")

    @staticmethod
    def get_validation_target():
        """Returns the type of validation target"""
        return os.getenv("NESTOR_VALIDATION_TARGET")


class SupportedValidations(Enum):
    """Enum of Supported validations by Nestor

    Args:
        Enum (Enum): Generic enumeration class
    """

    def __str__(self):
        return str(self.value)

    APPLICATIONS = "APPLICATIONS"
    PROJECTS = "PROJECTS"
