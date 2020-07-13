# pylint: disable=bad-continuation

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from jsonschema import ValidationError  # type: ignore

from tests.__fixtures__.example_schema import EXAMPLE_SCHEMA  # type: ignore
from validator.errors.errors import InvalidTargetPathError
import validator.validate as config_validator


class TestValidateLibrary(unittest.TestCase):
    def test_is_yaml_file(self):
        self.assertFalse(config_validator.is_yaml_file("invalid_name"))
        self.assertTrue(config_validator.is_yaml_file("filename.yaml"))
        self.assertTrue(config_validator.is_yaml_file("filename.yml"))

    @patch.dict(os.environ, {"NESTOR_CONFIG_PATH": "/some/target/path"})
    def test_build_apps_path_with_env(self):
        app_path = config_validator.build_apps_path()
        self.assertEqual(app_path, "/some/target/path/apps")

    @patch("validator.config.config.Configuration.get_target_path")
    def test_build_apps_path_not_set(self, get_target_path_mock):
        get_target_path_mock.return_value = None
        with self.assertRaises(InvalidTargetPathError):
            config_validator.build_apps_path()

    @patch.dict(os.environ, {"NESTOR_CONFIG_PATH": "/some/target/path"})
    def test_build_project_conf_path_with_env(self):
        project_conf_path = config_validator.build_project_conf_path()
        self.assertEqual(project_conf_path, "/some/target/path/project.yaml")

    @patch("validator.config.config.Configuration.get_target_path")
    def test_build_project_conf_path_not_set(self, get_target_path_mock):
        get_target_path_mock.return_value = None
        with self.assertRaises(InvalidTargetPathError):
            config_validator.build_project_conf_path()

    def test_validate_valid_file(self):
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "example_valid_config.yaml"
        ).resolve()

        # Validate an exception is not raised on valid schemas
        try:
            result = config_validator.validate_file(yaml_fixture_path, EXAMPLE_SCHEMA)
            self.assertIsNone(result)
        except ValidationError as error:
            self.fail(f"It should have not raised an exception on a valid file ${error}")

    def test_validate_invalid_file(self):
        yaml_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "example_invalid_config.yaml"
        ).resolve()

        with self.assertRaises(Exception):
            config_validator.validate_file(yaml_fixture_path, EXAMPLE_SCHEMA)

    @patch("validator.validate.build_apps_path")
    def test_validate_error_apps_dir_not_exists(self, build_apps_path_mock):
        build_apps_path_mock.return_value = "some/target/path"
        expected_message = "some/target/path does not look like a valid configuration path. Verify the path exists"  # pylint: disable=line-too-long
        with self.assertRaisesRegex(Exception, expected_message):
            config_validator.validate_deployment_files()

    @patch("validator.validate.build_apps_path")
    @patch("validator.config.config.Configuration.get_validation_target")
    def test_validate_error_validation_target(
        self, get_validation_target_mock, build_apps_path_mock
    ):
        fixtures_path = Path(os.path.dirname(__file__), "..", "__fixtures__").resolve()
        build_apps_path_mock.return_value = fixtures_path
        get_validation_target_mock.return_value = "SOME_VALUE"

        with self.assertRaisesRegex(
            Exception,  # pylint: disable=bad-continuation
            "There is no configuration to be validated. Be sure to define a valid NESTOR_VALIDATION_TARGET",  # pylint: disable=bad-continuation,line-too-long
        ):
            config_validator.validate_deployment_files()

    @patch("validator.validate.build_apps_path")
    @patch("validator.config.config.Configuration.get_validation_target")
    def test_validate_applications(self, get_validation_target_mock, build_apps_path_mock):
        real_config_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "validator", "apps"
        ).resolve()
        build_apps_path_mock.return_value = real_config_fixture_path
        get_validation_target_mock.return_value = "APPLICATIONS"
        try:
            config_validator.validate_deployment_files()
        except Exception as err:  # pylint: disable=broad-except
            self.fail(f"validate_deployment_files() raised an unexpected Exception {err}")

    @patch("validator.validate.build_project_conf_path")
    @patch("validator.validate.build_apps_path")
    @patch("validator.config.config.Configuration.get_validation_target")
    def test_validate_projects(
        self, get_validation_target_mock, build_apps_path_mock, build_project_conf_path_mock,
    ):
        real_config_fixture_path = Path(
            os.path.dirname(__file__), "..", "__fixtures__", "validator", "projects", "project.yaml"
        ).resolve()
        build_apps_path_mock.return_value = real_config_fixture_path
        get_validation_target_mock.return_value = "PROJECTS"
        build_project_conf_path_mock.return_value = real_config_fixture_path

        try:
            config_validator.validate_deployment_files()
        except Exception as err:  # pylint: disable=broad-except
            self.fail(f"validate_deployment_files() raised an unexpected Exception {err}")
