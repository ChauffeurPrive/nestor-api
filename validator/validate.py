"""Configuration files validator"""

import os
from pathlib import Path

import jsonschema
import yaml

from validator.config.config import Configuration
from validator.schemas.schema import SCHEMAS


def build_app_path():
    """Builds the path for /apps folder"""
    target_path = Configuration.get_target_path() or os.path.dirname(__file__)
    return os.path.join(target_path, "apps")


def build_project_conf_path():
    """Builds the path for project.yaml"""
    target_path = Configuration.get_target_path() or os.path.dirname(__file__)
    return os.path.join(target_path, "project.yaml")


def validate_file(file_path, schema):
    """Validates a file with a given schema

    Args:
        file_path (string): The path to the file
        schema (Dict): The schema format

    Returns:
        String: The validated file
    """
    with open(file_path, "r") as file:
        yaml_file_data = file.read()
        yaml_file = yaml.safe_load(yaml_file_data)
        return jsonschema.validate(yaml_file, schema)


def validate():
    """Main validate function

    Raises:
        Exception: If the configuration path has not been configured.
        Exception: [description]

    Returns:
        [type]: [description]
    """
    apps_path = build_app_path()
    project_config_file_path = build_project_conf_path()

    if not Path(apps_path).exists():
        raise Exception(
            f"{apps_path} does not look like a valid configuration path. Verify the path exists"
        )

    validations = []
    validation_target = Configuration.get_validation_target()

    if validation_target == "APPLICATIONS":
        # Validate each application file
        files_in_dir = [f for f in os.listdir() if os.path.isfile(f)]
        for file in files_in_dir:
            application_conf_file_path = os.path.join(apps_path, file)
            validation_result = validate_file(
                application_conf_file_path, SCHEMAS[validation_target]
            )

            # pylint: disable TODO Add log if the validation was successful or not
            validations.append(validation_result)
    elif validation_target == "PROJECT":
        # Validate on project.yaml
        validation_result = validate_file(project_config_file_path, SCHEMAS[validation_target])

        # pylint: disable TODO Add log if the validation was successful or not
        validations.append(validation_result)
    else:
        raise Exception(
            "There is no configuration to be validated. "
            + "Be sure to define a valid NESTOR_VALIDATION_TARGET"
        )

    # pylint: disable TODO pretty print validations
    return validations
