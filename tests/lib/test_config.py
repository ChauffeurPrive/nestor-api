import unittest
from unittest.mock import call, patch

from nestor_api.errors.config.aggregated_configuration_error import AggregatedConfigurationError
from nestor_api.errors.config.app_configuration_not_found_error import AppConfigurationNotFoundError
import nestor_api.lib.config as config


@patch("nestor_api.lib.config.io", autospec=True)
class TestConfigLibrary(unittest.TestCase):
    def test_change_environment(self, io_mock):
        config.change_environment("environment", "path/to/config")

        io_mock.execute.assert_has_calls(
            [
                call("git stash", "path/to/config"),
                call("git fetch origin", "path/to/config"),
                call("git checkout environment", "path/to/config"),
                call("git reset --hard origin/environment", "path/to/config"),
            ]
        )

    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_create_temporary_config_copy(self, configuration_mock, io_mock):
        io_mock.create_temporary_copy.return_value = "/temporary/path"
        configuration_mock.get_config_path.return_value = "tests/__fixtures__/config"

        path = config.create_temporary_config_copy()

        io_mock.create_temporary_copy.assert_called_once_with("tests/__fixtures__/config", "config")
        self.assertEqual(path, "/temporary/path")

    @patch("nestor_api.lib.config.get_project_config", autospec=True)
    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_app_config(self, configuration_mock, get_project_config_mock, io_mock):
        # Mocks
        configuration_mock.get_config_app_folder.return_value = "apps"
        io_mock.exists.return_value = True
        io_mock.from_yaml.return_value = {
            "sub_domain": "backoffice",
            "variables": {
                "ope": {"VARIABLE_OPE_2": "ope_2_override", "VARIABLE_OPE_3": "ope_3"},
                "app": {"VARIABLE_APP_2": "app_2_override", "VARIABLE_APP_3": "app_3"},
            },
        }
        get_project_config_mock.return_value = {
            "domain": "website.com",
            "variables": {
                "ope": {"VARIABLE_OPE_1": "ope_1", "VARIABLE_OPE_2": "ope_2"},
                "app": {"VARIABLE_APP_1": "app_1", "VARIABLE_APP_2": "app_2"},
            },
        }

        # Test
        app_config = config.get_app_config("backoffice", "tests/__fixtures__/config")

        # Assertions
        io_mock.exists.assert_called_once_with("tests/__fixtures__/config/apps/backoffice.yaml")
        io_mock.from_yaml.assert_called_once_with("tests/__fixtures__/config/apps/backoffice.yaml")
        get_project_config_mock.assert_called_once()
        self.assertEqual(
            app_config,
            {
                "domain": "website.com",
                "sub_domain": "backoffice",
                "variables": {
                    "ope": {
                        "VARIABLE_OPE_1": "ope_1",
                        "VARIABLE_OPE_2": "ope_2_override",
                        "VARIABLE_OPE_3": "ope_3",
                    },
                    "app": {
                        "VARIABLE_APP_1": "app_1",
                        "VARIABLE_APP_2": "app_2_override",
                        "VARIABLE_APP_3": "app_3",
                    },
                },
            },
        )

    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_app_config_when_not_found(self, configuration_mock, io_mock):
        io_mock.exists.return_value = False
        configuration_mock.get_config_app_folder.return_value = "apps"

        with self.assertRaises(AppConfigurationNotFoundError) as context:
            config.get_app_config("some-app", "/some/path")

        self.assertEqual("Configuration file not found for app: some-app", str(context.exception))

    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_project_config(self, configuration_mock, io_mock):
        # Mocks
        configuration_mock.get_config_project_filename.return_value = "project.yaml"
        io_mock.exists.return_value = True
        io_mock.from_yaml.return_value = {
            "domain": "website.com",
            "variables": {
                "ope": {"VARIABLE_OPE_1": "ope_1", "VARIABLE_OPE_2": "ope_2"},
                "app": {"VARIABLE_APP_1": "app_1", "VARIABLE_APP_2": "app_2"},
            },
        }

        # Test
        environment_config = config.get_project_config("tests/__fixtures__/config")

        # Assertions
        io_mock.exists.assert_called_once_with("tests/__fixtures__/config/project.yaml")
        io_mock.from_yaml.assert_called_once_with("tests/__fixtures__/config/project.yaml")
        self.assertEqual(
            environment_config,
            {
                "domain": "website.com",
                "variables": {
                    "ope": {"VARIABLE_OPE_1": "ope_1", "VARIABLE_OPE_2": "ope_2"},
                    "app": {"VARIABLE_APP_1": "app_1", "VARIABLE_APP_2": "app_2"},
                },
            },
        )

    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_project_config_when_not_found(self, configuration_mock, io_mock):
        io_mock.exists.return_value = False
        configuration_mock.get_config_project_filename.return_value = "project.yaml"

        with self.assertRaises(FileNotFoundError) as context:
            config.get_project_config("/some/path")

        self.assertEqual(
            "[Errno 2] No such file or directory: '/some/path/project.yaml'", str(context.exception)
        )

    @patch.dict("nestor_api.lib.config.os.environ", {"VALUE_IN_ENV": "value_in_env"})
    def test_resolve_variables_deep(self, _io_mock):
        result = config._resolve_variables_deep(
            {
                "A": "value_a",
                "B": "value_b",
                "C": {
                    "C1": "__{{A}}__",
                    "C2": "__{{key_not_present}}__",
                    "C3": "__{{A}}__{{B}}__{{key_not_present}}__",
                    "C4": "A",
                    "C5": "{{C1}}__{{key-with.special_characters}}",
                },
                "D": [
                    "value_d1",
                    "__{{A}}__",
                    "__{{key_not_present}}__",
                    "__{{A}}__{{B}}__{{key_not_present}}__",
                ],
                "E": [{"E1": {"E11": "deep__{{A}}__"}}],
                "F": 42,
                "key-with.special_characters": "amazing-value",
                "env_var": "$VALUE_IN_ENV",
                "env_var_missing": "$VALUE_NOT_IN_ENV",
            }
        )

        self.assertEqual(
            result,
            {
                "A": "value_a",
                "B": "value_b",
                "C": {
                    "C1": "__value_a__",
                    "C2": "__{{key_not_present}}__",
                    "C3": "__value_a__value_b__{{key_not_present}}__",
                    "C4": "A",
                    "C5": "{{C1}}__amazing-value",
                },
                "D": [
                    "value_d1",
                    "__value_a__",
                    "__{{key_not_present}}__",
                    "__value_a__value_b__{{key_not_present}}__",
                ],
                "E": [{"E1": {"E11": "deep__value_a__"}}],
                "F": 42,
                "key-with.special_characters": "amazing-value",
                "env_var": "value_in_env",
                "env_var_missing": "$VALUE_NOT_IN_ENV",
            },
        )

    def test_resolve_variables_deep_with_invalid_reference(self, _io_mock):
        with self.assertRaises(AggregatedConfigurationError) as context:
            config._resolve_variables_deep(
                {
                    "error": {},
                    "simple_key": "__{{error}}__",
                    "array": ["0", "1", "2__{{error}}__",],
                    "dict": {"a": "val_a", "b": "{{error}}",},
                    "deep_dict": {
                        "sub_dict": {"a": "val_a", "b": "{{error}}"},
                        "sub_array": [
                            {"a": "{{error}}", "b": "val_b"},
                            {"a": "val_a", "b": "{{error}}"},
                        ],
                    },
                }
            )

            err = context.exception
            self.assertEqual(
                err,
                {
                    "value": "Invalid configuration",
                    "errors": [
                        {
                            "path": "CONFIG.simple_key",
                            "message": "Referenced variable should resolved to a string",
                        },
                        {
                            "path": "CONFIG.array[2]",
                            "message": "Referenced variable should resolved to a string",
                        },
                        {
                            "path": "CONFIG.dict.b",
                            "message": "Referenced variable should resolved to a string",
                        },
                        {
                            "path": "CONFIG.deep_dict.sub_dict.b",
                            "message": "Referenced variable should resolved to a string",
                        },
                        {
                            "path": "CONFIG.deep_dict.sub_array[0].a",
                            "message": "Referenced variable should resolved to a string",
                        },
                        {
                            "path": "CONFIG.deep_dict.sub_array[1].b",
                            "message": "Referenced variable should resolved to a string",
                        },
                    ],
                },
            )
