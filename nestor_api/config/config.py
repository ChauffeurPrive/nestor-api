"""Nestor-api configuration"""

import os


class Configuration: # pylint: disable=too-few-public-methods
    """Nestor-api configuration"""
    config_path = os.getenv("NESTOR_CONFIG_PATH")
    pristine_path = os.getenv("NESTOR_PRISTINE_PATH", "/tmp/nestor/pristine")
    working_path = os.getenv("NESTOR_WORK_PATH", "/tmp/nestor/work")
