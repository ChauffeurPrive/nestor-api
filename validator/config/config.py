"""Nestor config validator configuration"""

import os


class Configuration:
    """Nestor_config_validator configuration"""
    target_path = os.getenv("NESTOR_TARGET_PATH")
    validation_target = os.getenv("NESTOR_VALIDATION_TARGET")
