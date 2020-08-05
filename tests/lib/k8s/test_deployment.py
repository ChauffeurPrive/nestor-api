from unittest import TestCase
from unittest.mock import patch

import nestor_api.lib.k8s.deployment as k8s_lib


class TestK8sDeployment(TestCase):
    @patch("nestor_api.lib.k8s.deployment.write_and_deploy_configuration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.deploy_app_ingress", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.has_process", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.builders", autospec=True)
    def test_deploy_app_with_web_process(
        self,
        builders_mock,
        has_web_process_mock,
        k8s_config_mock,
        deploy_app_ingress_mock,
        write_and_deploy_configuration_mock,
    ):
        """Should correctly deploy an app with an ingress."""
        # Mocks
        k8s_config_mock.get_templates_dir.return_value = "templates-dir"
        builders_mock.load_templates.return_value = {}
        has_web_process_mock.return_value = True
        builders_mock.build_deployment_yaml.return_value = "deployment: app"

        # Setup
        deployment_config = {"cluster_name": "my-cluster"}

        # Test
        k8s_lib.deploy_app(deployment_config, "/config", "tag-to-deploy")

        # Assertions
        builders_mock.load_templates.assert_called_once_with("/config/templates-dir")

        deploy_app_ingress_mock.assert_called_once()
        write_and_deploy_configuration_mock.assert_called_once_with("my-cluster", "deployment: app")

    @patch("nestor_api.lib.k8s.deployment.write_and_deploy_configuration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.deploy_app_ingress", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.has_process", autospec=True)
    @patch("nestor_api.lib.k8s.deployment.builders", autospec=True)
    def test_deploy_app_without_web_process(
        self,
        builders_mock,
        has_web_process_mock,
        k8s_config_mock,
        deploy_app_ingress_mock,
        write_and_deploy_configuration_mock,
    ):
        """Should correctly deploy the app, but not deploy an ingress."""
        # Mocks
        k8s_config_mock.get_templates_dir.return_value = "templates-dir"
        builders_mock.load_templates.return_value = {}
        has_web_process_mock.return_value = False
        builders_mock.build_deployment_yaml.return_value = "deployment: app"

        # Setup
        deployment_config = {"cluster_name": "my-cluster"}

        # Test
        k8s_lib.deploy_app(deployment_config, "/config", "tag-to-deploy")

        # Assertions
        builders_mock.load_templates.assert_called_once_with("/config/templates-dir")

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
