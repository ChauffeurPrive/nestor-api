"""Module to encapsulate the load method from pyyaml"""

import yaml

from yaml_lib.duplicate_keys_loader import DuplicateKeysLoader


def parse_yaml(yaml_data: str) -> dict:
    """Parse yaml from a string"""
    return yaml.load(yaml_data, Loader=DuplicateKeysLoader)


def read_yaml(file_path: str) -> dict:
    """Loads a yaml file from a path using the DuplicateKeysLoader

    Args:
        file_path (str): The file path

    Returns:
        dict: The representation of the yaml file as a dict
    """
    with open(file_path, "r") as file_data:
        yaml_data = file_data.read()
    return parse_yaml(yaml_data)
