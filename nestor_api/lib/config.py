"""Configuration library"""

import copy
import errno
import os
import re
from typing import Optional

from nestor_api.config.config import Configuration
from nestor_api.errors.config.aggregated_configuration_error import AggregatedConfigurationError
from nestor_api.errors.config.app_configuration_not_found_error import AppConfigurationNotFoundError
from nestor_api.errors.config.configuration_error import ConfigurationError
import nestor_api.lib.io as io
import nestor_api.utils.dict as dict_utils


def change_environment(environment: str, config_path=Configuration.get_config_path()):
    """Change the environment (branch) of the configuration"""
    io.execute("git stash", config_path)
    io.execute("git fetch origin", config_path)
    io.execute(f"git checkout {environment}", config_path)
    io.execute(f"git reset --hard origin/{environment}", config_path)


def create_temporary_config_copy() -> str:
    """Copy the configuration into a temporary directory and returns its path"""
    return io.create_temporary_copy(Configuration.get_config_path(), "config")


def get_app_config(app_name: str, config_path: str = Configuration.get_config_path()) -> dict:
    """Load the configuration of an app"""
    app_config_path = os.path.join(
        config_path, Configuration.get_config_app_folder(), f"{app_name}.yaml",
    )
    if not io.exists(app_config_path):
        raise AppConfigurationNotFoundError(app_name)

    app_config = io.read_yaml(app_config_path)
    project_config = get_project_config(config_path)

    config = dict_utils.deep_merge(project_config, app_config)

    # Awaiting for implementation
    # validate configuration using nestor-config-validator

    return _resolve_variables_deep(config)


def get_project_config(config_path: str = Configuration.get_config_path()) -> dict:
    """Load the global configuration of the project"""
    project_config_path = os.path.join(config_path, Configuration.get_config_project_filename())
    if not io.exists(project_config_path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), project_config_path)

    project_config = io.read_yaml(project_config_path)

    return _resolve_variables_deep(project_config)


def _resolve_variable(template: str, variables: dict, path: str) -> str:
    final_value = template

    # Resolve pattern '{{variable}}'
    referenced_names = re.findall(r"{{([\w\-.]+)}}", template)
    if len(referenced_names) > 0:
        for var_name in referenced_names:
            var_value = variables.get(var_name)
            if var_value is not None:
                if not isinstance(var_value, str):
                    raise ConfigurationError(
                        path, "Referenced variable should resolved to a string"
                    )

                final_value = re.sub(f"{{{{{var_name}}}}}", var_value, final_value)
        return final_value

    # Resolve pattern '$ENV_VAR'
    env_variables = re.findall(r"^\$(\w+)$", template)
    if len(env_variables) > 0:
        env_var = os.environ.get(env_variables[0])
        if env_var is not None:
            final_value = env_var
        return final_value

    # Awaiting for implementation
    # -> Resolve vault definitions "!vault:xxx"

    return final_value


def _resolve_variables_deep(config: dict) -> dict:
    def __resolve_list(list_values, variables, path, errors):
        resolved_values = []
        for idx, value in enumerate(list_values):
            resolved, errors = __resolve(value, variables, f"{path}[{idx}]", errors)
            resolved_values.append(resolved)
        return resolved_values, errors

    def __resolve_dict(dict_values, variables, path, errors):
        for key in dict_values:
            resolved_value, errors = __resolve(dict_values[key], variables, f"{path}.{key}", errors)
            dict_values[key] = resolved_value
        return dict_values, errors

    def __resolve_str(value, variables, path, errors):
        try:
            resolved_value = _resolve_variable(value, variables, path)
            return resolved_value, errors
        except ConfigurationError as err:
            errors.append(err)
            return value, errors

    def __resolve(value, variables, path, errors):
        if isinstance(value, list):
            return __resolve_list(value, variables, path, errors)
        if isinstance(value, dict):
            return __resolve_dict(value, variables, path, errors)
        if isinstance(value, str):
            return __resolve_str(value, variables, path, errors)
        return value, errors

    # The top-level of config is used as `variables`
    resolved_config, errors = __resolve(copy.deepcopy(config), config, "CONFIG", [])

    if len(errors) > 0:
        raise AggregatedConfigurationError(errors)

    return resolved_config


def get_previous_step(config_object: dict, target: str) -> Optional[str]:
    """ Returns the previous step in the defined workflow """
    index = config_object["workflow"].index(target)
    if index > 0:
        return config_object["workflow"][index - 1]
    return None


# pylint: disable=bad-continuation
def list_apps_config(
    config_path=Configuration.get_config_path(), apps_path=Configuration.get_config_app_folder()
) -> dict:
    """Retrieves all of the application names."""
    apps_path = os.path.join(config_path, apps_path)

    if not os.path.isdir(apps_path):
        raise ValueError(apps_path)
    apps_files = [f for f in os.listdir(apps_path) if os.path.isfile(os.path.join(apps_path, f))]
    apps_config = [io.from_yaml(file) for file in apps_files]
    return {app_config["name"]: app_config for app_config in apps_config}
