"""Configuration library"""

import errno
import os

from nestor_api.config.config import Configuration
from nestor_api.lib.errors import AppConfigurationNotFoundError
import nestor_api.lib.io as io
import nestor_api.utils.dict as dict_utils

APPS_FOLDER = "apps"


def change_environment(environment: str, config_path=Configuration.get_config_path()):
    """Change the environment (branch) of the configuration"""
    io.execute("git stash", config_path)
    io.execute("git fetch origin", config_path)
    io.execute(f"git checkout {environment}", config_path)
    io.execute(f"git reset --hard origin/{environment}", config_path)


def create_temporary_config_copy():
    """Copy the configuration into a temporary directory and returns its path"""
    return io.create_temporary_copy(Configuration.get_config_path(), "config")


def get_app_config(app_name: str) -> dict:
    """Load the configuration of an app"""
    app_config_path = os.path.join(Configuration.get_config_path(), APPS_FOLDER, f"{app_name}.yaml")
    if not io.exists(app_config_path):
        raise AppConfigurationNotFoundError(app_name)

    app_config = io.from_yaml(app_config_path)
    environment_config = get_environment_config()

    config = dict_utils.deep_merge(environment_config, app_config)

    # To be done: Validate configuration using nestor-config-validator

    return __map_values(config)


def get_environment_config() -> dict:
    """Load the configuration of the current environment (global configuration)"""
    project_config_path = os.path.join(Configuration.get_config_path(), "project.yaml")
    if not io.exists(project_config_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), project_config_path)

    project_config = io.from_yaml(project_config_path)

    return __map_values(project_config)


def __map_values(config: dict) -> dict:
    # To be done: implement variable resolutions in values
    # example:
    #    base_domain: 'website.com'
    #    variables:
    #        API_URL: 'api.{{base_domain}}'     -->    'api.website.com'
    return config
