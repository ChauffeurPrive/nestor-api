import os
from pathlib import Path
from unittest import TestCase

import yaml_lib


class TestLoadYaml(TestCase):
    def test_parse_yaml(self):
        """Assert that parse_yaml can parse a valid yaml"""
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "example_valid_config.yaml"
        ).resolve()
        with open(yaml_fixture_path, "r") as file:
            file_data = file.read()

        result = yaml_lib.parse_yaml(file_data)

        self.assertEqual(
            result, {"test": "test"},
        )

    def test_read_yaml_disallow_duplicate_keys(self):
        """Assert that read_yaml disallows duplicate keys"""
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "yaml", "duplicated_keys.yaml"
        ).resolve()
        expected_message = "Found a duplicate key: name"

        with self.assertRaisesRegex(Exception, expected_message):
            yaml_lib.read_yaml(yaml_fixture_path)

    def test_read_yaml_valid(self):
        """Assert that read_yaml can read a valid yaml"""
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "example_valid_config.yaml"
        ).resolve()

        result = yaml_lib.read_yaml(yaml_fixture_path)
        self.assertEqual(
            result, {"test": "test"},
        )
