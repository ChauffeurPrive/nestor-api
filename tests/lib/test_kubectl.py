import os
from unittest import TestCase
from unittest.mock import patch

import nestor_api.lib.kubectl as kubectl


class TestKubectl(TestCase):
    @patch("nestor_api.lib.kubectl.KubernetesConfiguration")
    @patch("nestor_api.lib.kubectl.io")
    def test_fetch_resource_configuration_deployment(self, io_mock, config_mock):
        config_mock.get_http_proxy.return_value = "k8s-proxy.my-domain.com"
        io_mock.execute.return_value = '{"key": "value"}'

        result = kubectl.fetch_resource_configuration(
            "cluster", "namespace", "app", kubectl.KubernetesResourceType.DEPLOYMENT
        )

        self.assertEqual(result, {"key": "value"})
        io_mock.execute.assert_called_once_with(
            (
                "kubectl "
                "--context cluster "
                "--namespace namespace "
                "get deployment "
                "--output=json "
                "--selector app=app"
            ),
            env={**os.environ, "HTTP_PROXY": "k8s-proxy.my-domain.com",},
        )
