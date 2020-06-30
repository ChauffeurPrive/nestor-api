"""Nestor-api configuration"""

import os


class Configuration:
    """Nestor-api configuration"""

    @staticmethod
    def get_config_path():
        """Returns the path of the project holding configurations"""
        return os.getenv("NESTOR_CONFIG_PATH")

    @staticmethod
    def get_config_app_folder():
        """Returns the name of the folder holding the applications configurations"""
        return os.getenv("NESTOR_CONFIG_APPS_FOLDER", "apps")

    @staticmethod
    def get_config_projet_filename():
        """Returns the name of the file holding the project's configuration"""
        return os.getenv("NESTOR_CONFIG_PROJECT_FILENAME", "project.yaml")

    @staticmethod
    def get_pristine_path():
        """Returns the path of the project holding pristines"""
        return os.getenv("NESTOR_PRISTINE_PATH", "/tmp/nestor/pristine")

    @staticmethod
    def get_working_path():
        """Returns the path of the project holding working copies"""
        return os.getenv("NESTOR_WORK_PATH", "/tmp/nestor/work")
