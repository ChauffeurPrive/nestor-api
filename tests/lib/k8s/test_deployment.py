from unittest import TestCase
from unittest.mock import patch

import nestor_api.lib.k8s.deployment as k8s_lib
from nestor_api.lib.k8s.enums.k8s_resource_type import K8sResourceType
import tests.__fixtures__.k8s as k8s_fixtures


class TestK8sDeployment(TestCase):
    @patch("nestor_api.lib.k8s.deployment.write_and_deploy_configuration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.deploy_app_ingress", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.get_deployement_statuses_diff", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.get_deployment_status", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.has_process", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.builders", autospec=True)
    def test_deploy_app_with_web_process(
        self,
        builders_mock,
        has_web_process_mock,
        k8s_config_mock,
        get_deployement_status_mock,
        get_deployement_statuses_diff_mock,
        deploy_app_ingress_mock,
        write_and_deploy_configuration_mock,
    ):
        """Should correctly deploy an app with an ingress."""
        # Mocks
        k8s_config_mock.get_templates_dir.return_value = "templates-dir"
        builders_mock.load_templates.return_value = {}
        has_web_process_mock.return_value = True
        builders_mock.build_deployment_yaml.return_value = "deployment: app"
        report = {}
        get_deployement_statuses_diff_mock.return_value = report

        # Setup
        deployment_config = {"cluster_name": "my-cluster"}

        # Test
        result = k8s_lib.deploy_app(deployment_config, "/config", "tag-to-deploy")

        # Assertions
        self.assertEqual(result, report)

        builders_mock.load_templates.assert_called_once_with("/config/templates-dir")

        self.assertEqual(get_deployement_status_mock.call_count, 2)
        get_deployement_statuses_diff_mock.assert_called_once()
        deploy_app_ingress_mock.assert_called_once()
        write_and_deploy_configuration_mock.assert_called_once_with("my-cluster", "deployment: app")

    @patch("nestor_api.lib.k8s.deployment.write_and_deploy_configuration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.deploy_app_ingress", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.get_deployement_statuses_diff", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.get_deployment_status", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.has_process", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.builders", autospec=True)
    def test_deploy_app_without_web_process(
        self,
        builders_mock,
        has_web_process_mock,
        k8s_config_mock,
        get_deployement_status_mock,
        get_deployement_statuses_diff_mock,
        deploy_app_ingress_mock,
        write_and_deploy_configuration_mock,
    ):
        """Should correctly deploy the app, but not deploy an ingress."""
        # Mocks
        k8s_config_mock.get_templates_dir.return_value = "templates-dir"
        builders_mock.load_templates.return_value = {}
        has_web_process_mock.return_value = False
        builders_mock.build_deployment_yaml.return_value = "deployment: app"
        report = {}
        get_deployement_statuses_diff_mock.return_value = report

        # Setup
        deployment_config = {"cluster_name": "my-cluster"}

        # Test
        result = k8s_lib.deploy_app(deployment_config, "/config", "tag-to-deploy")

        # Assertions
        self.assertEqual(result, report)

        builders_mock.load_templates.assert_called_once_with("/config/templates-dir")

        self.assertEqual(get_deployement_status_mock.call_count, 2)
        get_deployement_statuses_diff_mock.assert_called_once()

        deploy_app_ingress_mock.assert_not_called()
        write_and_deploy_configuration_mock.assert_called_once_with("my-cluster", "deployment: app")

    @patch("nestor_api.lib.k8s.deployment.builders", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.write_and_deploy_configuration", autospec=True)
    def test_deploy_app_ingress(self, write_and_deploy_configuration_mock, builders_mock):
        """Should correctly deploy an application's ingress."""
        builders_mock.build_ingress_yaml.return_value = "ingress: app"
        deployment_config = {"cluster_name": "my-cluster"}

        k8s_lib.deploy_app_ingress(deployment_config, "web", {})

        write_and_deploy_configuration_mock.assert_called_once_with("my-cluster", "ingress: app")

    def test_has_process_when_true(self):
        """Should return True."""
        deployment_config = {
            "processes": [
                {"name": "worker", "is_cronjob": False},
                {"name": "cronjob", "is_cronjob": True},
                {"name": "web", "is_cronjob": False},
            ]
        }

        result = k8s_lib.has_process(deployment_config, "web")

        self.assertTrue(result)

    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_get_deployment_status(self, cli_mock):
        """Should correctly retrieve and format the deployment status."""
        cli_mock.fetch_resource_configuration.return_value = {
            "items": [
                k8s_fixtures.DEPLOYMENT_STATUS_ITEM_PROCESS,
                k8s_fixtures.DEPLOYMENT_STATUS_ITEM_CRONJOB,
            ],
        }
        deployment_config = {
            "cluster_name": "my-cluster",
            "namespace": "my-namespace",
            "app": "my-app",
        }

        report = k8s_lib.get_deployment_status(deployment_config)

        self.assertEqual(
            report,
            {
                "processes": [
                    {
                        "name": "my-process",
                        "image": "0.1.0-sha-1ab23cd",
                        "command": "npm start:process",
                    },
                ],
                "cronjobs": [
                    {
                        "name": "my-cron",
                        "image": "0.1.0-sha-1ab23cd",
                        "command": "npm start:cron",
                        "schedule": "0 0 * * *",
                    },
                ],
                "env": [
                    {"name": "VAR_A", "value": "VALUE_A"},
                    {"name": "VAR_B", "value": "VALUE_B"},
                ],
            },
        )
        cli_mock.fetch_resource_configuration.assert_called_once_with(
            "my-cluster",
            "my-namespace",
            "my-app",
            [K8sResourceType.DEPLOYMENTS, K8sResourceType.CRONJOBS],
        )

    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_get_deployment_status_when_nothing(self, cli_mock):
        """Should return an empty deployment status."""
        cli_mock.fetch_resource_configuration.return_value = {
            "items": [],
        }
        deployment_config = {
            "cluster_name": "my-cluster",
            "namespace": "my-namespace",
            "app": "my-app",
        }

        report = k8s_lib.get_deployment_status(deployment_config)

        self.assertEqual(
            report, {"processes": [], "cronjobs": [], "env": []},
        )
        cli_mock.fetch_resource_configuration.assert_called_once_with(
            "my-cluster",
            "my-namespace",
            "my-app",
            [K8sResourceType.DEPLOYMENTS, K8sResourceType.CRONJOBS],
        )

    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_get_deployment_status_when_only_crons(self, cli_mock):
        """Should correctly retrieve the env from the cronjob."""
        cli_mock.fetch_resource_configuration.return_value = {
            "items": [k8s_fixtures.DEPLOYMENT_STATUS_ITEM_CRONJOB],
        }
        deployment_config = {
            "cluster_name": "my-cluster",
            "namespace": "my-namespace",
            "app": "my-app",
        }

        report = k8s_lib.get_deployment_status(deployment_config)

        self.assertEqual(
            report,
            {
                "processes": [],
                "cronjobs": [
                    {
                        "name": "my-cron",
                        "image": "0.1.0-sha-1ab23cd",
                        "command": "npm start:cron",
                        "schedule": "0 0 * * *",
                    },
                ],
                "env": [
                    {"name": "VAR_A", "value": "VALUE_A"},
                    {"name": "VAR_B", "value": "VALUE_B"},
                ],
            },
        )
        cli_mock.fetch_resource_configuration.assert_called_once_with(
            "my-cluster",
            "my-namespace",
            "my-app",
            [K8sResourceType.DEPLOYMENTS, K8sResourceType.CRONJOBS],
        )

    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_get_deployment_status_when_unknown_item(self, cli_mock):
        """Should raise an Error when an unknown item is encountered."""
        cli_mock.fetch_resource_configuration.return_value = {
            "items": [{"kind": "Unknown"}],
        }
        deployment_config = {
            "cluster_name": "my-cluster",
            "namespace": "my-namespace",
            "app": "my-app",
        }

        with self.assertRaisesRegex(Exception, 'Unknown item kind "Unknown"'):
            k8s_lib.get_deployment_status(deployment_config)

    def test_get_deployment_statuses_diff_when_no_diff(self):
        """Should return a report with no differences."""
        previous_status = {
            "processes": [
                {"name": "proc-1", "image": "0.1.0-sha-1ab", "command": "npm start:proc-1"},
            ],
            "cronjobs": [
                {
                    "name": "cron-1",
                    "image": "0.1.0-sha-1ab23cd",
                    "command": "npm start:cron",
                    "schedule": "0 0 * * *",
                },
            ],
            "env": [
                {"name": "VAR_A", "value": "VALUE_A"},
                {"name": "VAR_B", "valueFrom": {"name": "my-app", "key": "VAR_B"}},
            ],
        }
        new_status = previous_status

        diff = k8s_lib.get_deployement_statuses_diff(previous_status, new_status)

        self.assertEqual(
            diff,
            {
                "processes": {"added": [], "modified": [], "removed": []},
                "cronjobs": {"added": [], "modified": [], "removed": []},
                "env": {"added": [], "modified": [], "removed": []},
            },
        )

    def test_get_deployment_statuses_diff_with_changes(self):
        """Should return a complete report with the differences."""
        previous_status = {
            "processes": [
                {"name": "proc-1", "image": "0.1.0-sha-1ab", "command": "npm start:proc-1"},
                {"name": "proc-2", "image": "0.1.0-sha-1ab", "command": "npm start:proc-2"},
            ],
            "cronjobs": [
                {
                    "name": "cron-2",
                    "image": "0.1.0-sha-1ab",
                    "command": "npm start:cron-2",
                    "schedule": "0 0 * * *",
                },
                {
                    "name": "cron-3",
                    "image": "0.1.0-sha-1ab",
                    "command": "npm start:cron-3",
                    "schedule": "0 * * * *",
                },
            ],
            "env": [{"name": "VAR_A", "value": "VALUE_A"}, {"name": "VAR_B", "value": "VALUE_B"}],
        }
        new_status = {
            "processes": [
                {"name": "proc-1", "image": "0.1.0-sha-2cd", "command": "npm start:proc-1"},
            ],
            "cronjobs": [
                {
                    "name": "cron-1",
                    "image": "0.1.0-sha-2cd",
                    "command": "npm start:cron-1",
                    "schedule": "0 * * * *",
                },
                {
                    "name": "cron-2",
                    "image": "0.1.0-sha-2cd",
                    "command": "npm start:cron-2",
                    "schedule": "0 0 * * *",
                },
            ],
            "env": [
                {"name": "VAR_B", "valueFrom": {"name": "my-app", "key": "VAR_B"}},
                {"name": "VAR_C", "value": "VALUE_C"},
            ],
        }

        diff = k8s_lib.get_deployement_statuses_diff(previous_status, new_status)

        self.assertEqual(
            diff,
            {
                "processes": {
                    "added": [],
                    "modified": [
                        {
                            "name": "proc-1",
                            "values": {"image": {"old": "0.1.0-sha-1ab", "new": "0.1.0-sha-2cd"}},
                        },
                    ],
                    "removed": [
                        {"name": "proc-2", "image": "0.1.0-sha-1ab", "command": "npm start:proc-2"},
                    ],
                },
                "cronjobs": {
                    "added": [
                        {
                            "name": "cron-1",
                            "image": "0.1.0-sha-2cd",
                            "command": "npm start:cron-1",
                            "schedule": "0 * * * *",
                        },
                    ],
                    "modified": [
                        {
                            "name": "cron-2",
                            "values": {"image": {"old": "0.1.0-sha-1ab", "new": "0.1.0-sha-2cd"}},
                        },
                    ],
                    "removed": [
                        {
                            "name": "cron-3",
                            "image": "0.1.0-sha-1ab",
                            "command": "npm start:cron-3",
                            "schedule": "0 * * * *",
                        },
                    ],
                },
                "env": {
                    "added": [{"name": "VAR_C", "value": "VALUE_C"}],
                    "modified": [
                        {
                            "name": "VAR_B",
                            "value": {"old": "VALUE_B", "new": {"key": "VAR_B", "name": "my-app"}},
                        },
                    ],
                    "removed": [{"name": "VAR_A", "value": "VALUE_A"}],
                },
            },
        )

    def test_has_process_when_false(self):
        """Should return False."""
        deployment_config = {
            "processes": [
                {"name": "worker", "is_cronjob": False},
                {"name": "cronjob", "is_cronjob": True},
            ]
        }

        result = k8s_lib.has_process(deployment_config, "web")

        self.assertFalse(result)

    def test_has_process_when_the_name_is_a_cron(self):
        """Should not consider a cron with the correct name."""
        deployment_config = {
            "processes": [
                {"name": "worker", "is_cronjob": False},
                {"name": "cronjob", "is_cronjob": True},
                {"name": "web", "is_cronjob": True},
            ]
        }

        result = k8s_lib.has_process(deployment_config, "web")

        self.assertFalse(result)

    @patch("nestor_api.lib.k8s.deployment.io", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_write_and_deploy_configuration(self, cli_mock, io_mock):
        """Should correctly write and apply the config."""
        io_mock.create_temporary_directory.return_value = "/tmp"

        k8s_lib.write_and_deploy_configuration("cluster_name", "yaml_data")

        io_mock.write.assert_called_once_with("/tmp/config.yaml", "yaml_data")
        cli_mock.apply_config.assert_called_once_with("cluster_name", "/tmp/config.yaml")
        io_mock.remove.assert_called()

    @patch("nestor_api.lib.k8s.deployment.io", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.cli", autospec=True)
    def test_write_and_deploy_configuration_with_error(self, cli_mock, io_mock):
        """Should clean the temporary directory, even when an error occurs."""
        io_mock.create_temporary_directory.return_value = "/tmp"
        cli_mock.apply_config.side_effect = Exception("An unfortunate error")

        with self.assertRaises(Exception):
            k8s_lib.write_and_deploy_configuration("cluster_name", "yaml_data")

        io_mock.remove.assert_called_once()
