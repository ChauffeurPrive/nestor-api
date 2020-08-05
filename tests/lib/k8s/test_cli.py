import os
from unittest import TestCase
from unittest.mock import patch

import nestor_api.lib.k8s.cli as cli
from nestor_api.lib.k8s.enums.k8s_resource_type import K8sResourceType


class TestK8sCli(TestCase):
    @patch("nestor_api.lib.k8s.cli.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.cli.io", autospec=True)
    def test_fetch_resource_configuration_deployment(self, io_mock, config_mock):
        config_mock.get_http_proxy.return_value = "k8s-proxy.my-domain.com"
        io_mock.execute.return_value = '{"key": "value"}'

        result = cli.fetch_resource_configuration(
            "cluster", "namespace", "my-app", K8sResourceType.DEPLOYMENT
        )

        self.assertEqual(result, {"key": "value"})
        io_mock.execute.assert_called_once_with(
            (
                "kubectl "
                "--context cluster "
                "--namespace namespace "
                "get deployment "
                "--output=json "
                "--selector app=my-app"
            ),
            env={**os.environ, "HTTP_PROXY": "k8s-proxy.my-domain.com"},
        )

    @patch("nestor_api.lib.k8s.cli.K8sConfiguration", autospec=True)
    @patch("nestor_api.lib.k8s.cli.io", autospec=True)
    def test_apply_config(self, io_mock, config_mock):
        config_mock.get_http_proxy.return_value = "k8s-proxy.my-domain.com"

        cli.apply_config("cluster_name", "/path/to/config")

        io_mock.execute.assert_called_once_with(
            "kubectl --context cluster_name apply -f /path/to/config",
            env={**os.environ, "HTTP_PROXY": "k8s-proxy.my-domain.com"},
        )
