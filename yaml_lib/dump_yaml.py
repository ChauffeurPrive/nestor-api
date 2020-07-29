"Module encapsulating the dump methods from pyyaml."

import yaml


def convert_to_yaml(data: dict) -> str:
    """Converts a dictionary into a valid yaml string"""
    return yaml.safe_dump(data)
