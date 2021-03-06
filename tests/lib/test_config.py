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

    @patch("yaml_lib.read_yaml", autospec=True)
    @patch("nestor_api.lib.config.get_project_config", autospec=True)
    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_app_config(
        self, configuration_mock, get_project_config_mock, read_yaml_mock, io_mock
    ):
        # Mocks
        configuration_mock.get_config_app_folder.return_value = "apps"
        io_mock.exists.return_value = True
        read_yaml_mock.return_value = {
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
        read_yaml_mock.assert_called_once_with("tests/__fixtures__/config/apps/backoffice.yaml")
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

    def test_get_processes(self, _io_mock):
        app_config = {
            "name": "my-app",
            "processes": [
                {"name": "web", "start_command": "./web", "is_cronjob": False,},
                {"name": "cleaner", "start_command": "./clean", "is_cronjob": True,},
                {"name": "worker", "start_command": "./worker", "is_cronjob": False,},
            ],
        }

        applications = config.get_processes(app_config)

        self.assertEqual(
            applications,
            [
                {"name": "web", "start_command": "./web", "is_cronjob": False,},
                {"name": "worker", "start_command": "./worker", "is_cronjob": False,},
            ],
        )

    def test_get_cronjobs(self, _io_mock):
        app_config = {
            "name": "my-app",
            "processes": [
                {"name": "web", "start_command": "./web", "is_cronjob": False,},
                {"name": "cleaner", "start_command": "./clean", "is_cronjob": True,},
                {"name": "worker", "start_command": "./worker", "is_cronjob": False,},
            ],
        }

        cronjobs = config.get_cronjobs(app_config)

        self.assertEqual(
            cronjobs, [{"name": "cleaner", "start_command": "./clean", "is_cronjob": True,}]
        )

    def test_get_deployments(self, _io_mock):
        project_config = {
            "project": "my-project",
            "spec": {"spec_1": "default_spec_1", "spec_2": "default_spec_2",},
            "deployments": [
                {"cluster": "cluster_1", "spec": {"spec_1": "spec_deployment_1"}},
                {"cluster": "cluster_2", "spec": {"spec_2": "spec_deployment_2"}},
            ],
        }

        deployments = config.get_deployments(project_config)

        self.assertEqual(
            deployments,
            [
                {
                    "cluster": "cluster_1",
                    "project": "my-project",
                    "spec": {"spec_1": "spec_deployment_1", "spec_2": "default_spec_2"},
                },
                {
                    "cluster": "cluster_2",
                    "project": "my-project",
                    "spec": {"spec_1": "default_spec_1", "spec_2": "spec_deployment_2"},
                },
            ],
        )

    @patch("yaml_lib.read_yaml", autospec=True)
    @patch("nestor_api.lib.config.Configuration", autospec=True)
    def test_get_project_config(self, configuration_mock, read_yaml_mock, io_mock):
        # Mocks
        configuration_mock.get_config_project_filename.return_value = "project.yaml"
        io_mock.exists.return_value = True
        read_yaml_mock.return_value = {
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
        read_yaml_mock.assert_called_once_with("tests/__fixtures__/config/project.yaml")
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

    @patch("nestor_api.lib.config.os.path.isdir", autospec=True)
    @patch("nestor_api.lib.config.os.listdir", autospec=True)
    @patch("nestor_api.lib.config.get_app_config", autospec=True)
    def test_list_apps_config(self, get_app_config_mock, listdir_mock, isdir_mock, _io_mock):
        """Should return a dictionary of apps config."""
        isdir_mock.return_value = True
        listdir_mock.return_value = [
            "path/to/app-1.yml",
            "path/to/app-2.yaml",
            "path/to/app-3.ext",
            "path/to/dir/",
        ]

        def yaml_side_effect(arg):
            # pylint: disable=no-else-return
            if arg == "app-1":
                return {"name": "app-1", "config_key": "value for app-1"}
            elif arg == "app-2":
                return {"name": "app-2", "config_key": "value for app-2"}
            return None

        get_app_config_mock.side_effect = yaml_side_effect

        result = config.list_apps_config("test")
        self.assertEqual(
            result,
            {
                "app-1": {"name": "app-1", "config_key": "value for app-1"},
                "app-2": {"name": "app-2", "config_key": "value for app-2"},
            },
        )

    @patch("nestor_api.lib.config.os.path.isdir", autospec=True)
    def test_list_apps_config_with_incorrect_apps_path(self, is_dir_mock, _io_mock):
        """Should return a dictionary of apps config."""
        is_dir_mock.return_value = False

        with self.assertRaisesRegex(ValueError, "test/apps"):
            config.list_apps_config("test")
