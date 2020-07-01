"""Nestor config validator configuration"""

import os


class Configuration:
    """Nestor_config_validator configuration"""

    @staticmethod
    def get_target_path():
        """Returns the target path of the project configuration"""
        return os.getenv("NESTOR_TARGET_PATH")

    @staticmethod
    def get_validation_target():
        """Returns the type of validation target"""
        return os.getenv("NESTOR_VALIDATION_TARGET")
