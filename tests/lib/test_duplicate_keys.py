import os
from pathlib import Path
from unittest import TestCase

import yaml

from yaml_lib.duplicate_keys import YamlLoader  # type: ignore


class TestDetectDuplicateKeysInYaml(TestCase):
    def test_read_yaml_disallow_duplicate_keys(self):
        """Assert that read_yaml disallows duplicate keys"""
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "yaml", "duplicated_keys.yaml"
        ).resolve()

        with open(yaml_fixture_path, "r") as file_data:
            yaml_data = file_data.read()
            with self.assertRaises(Exception):
                yaml.load(yaml_data, Loader=YamlLoader)
