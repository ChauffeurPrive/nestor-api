"""Configuration files validator"""

import os
from pathlib import Path

import jsonschema  # type: ignore

from validator.config.config import Configuration, SupportedValidations
from validator.errors.errors import InvalidTargetPathError
from validator.schemas.schema import SCHEMAS
import yaml_lib


def is_yaml_file(file_name):
    """Verifies if a file ends in a valid yaml extension

    Args:
        file_name (string): The file name

    Returns:
        boolean: Whether it ends in the supported yaml extensions
    """
    return file_name.endswith((".yaml", ".yml"))


def build_apps_path():
    """Builds the path for /apps folder"""
    target_path = Configuration.get_target_path()
    if target_path is None:
        raise InvalidTargetPathError(target_path)
    return os.path.join(target_path, "apps")


def build_project_conf_path():
    """Builds the path for project.yaml"""
    target_path = Configuration.get_target_path()
    if target_path is None:
        raise InvalidTargetPathError(target_path)
    return os.path.join(target_path, "project.yaml")


def validate_file(file_path: str, schema: dict) -> str:
    """Validates a file with a given schema

    Args:
        file_path (string): The path to the file
        schema (Dict): The schema format

    Returns:
        String: The validated file
    """
    yaml_file = yaml_lib.read_yaml(file_path)
    return jsonschema.validate(yaml_file, schema)


def validate_deployment_files():
    """Main validate function

    This function executes a specific validation configured with NESTOR_VALIDATION_TARGET
    to a list of files in a given path configured with NESTOR_CONFIG_PATH.

    Raises:
        Exception: If the configuration path has not been configured.
        Exception: If the configuration path does not exist
    """
    apps_path = build_apps_path()
    if not Path(apps_path).exists():
        raise NotADirectoryError(
            f"{apps_path} does not look like a valid configuration path. Verify the path exists"
        )

    validation_target = Configuration.get_validation_target()

    if validation_target == str(SupportedValidations.APPLICATIONS):
        # Validate each application file

        # We will only validate .yaml or .yml files
        files_in_dir = [
            f.lower()
            for f in os.listdir(apps_path)
            if os.path.isfile(os.path.join(apps_path, f))
            and not f.startswith(".")
            and is_yaml_file(f)
        ]

        for file in files_in_dir:
            application_config_file_path = os.path.join(apps_path, file)
            validate_file(application_config_file_path, SCHEMAS[validation_target])

    elif validation_target == str(SupportedValidations.PROJECTS):
        # Validate project.yaml
        project_config_file_path = build_project_conf_path()
        validate_file(project_config_file_path, SCHEMAS[validation_target])

    else:
        raise Exception(
            "There is no configuration to be validated. "
            + "Be sure to define a valid NESTOR_VALIDATION_TARGET"
        )
