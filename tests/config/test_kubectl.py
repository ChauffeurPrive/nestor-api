import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.kubernetes import KubernetesConfiguration


class TestKubernetesConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_K8S_HTTP_PROXY": "k8s-proxy.my-domain.com"})
    def test_get_http_proxy(self):
        self.assertEqual(KubernetesConfiguration.get_http_proxy(), "k8s-proxy.my-domain.com")

    @patch.dict(os.environ, {"NESTOR_K8S_HTTP_PROXY": ""})
    def test_get_http_proxy_not_existing(self):
        del os.environ["NESTOR_K8S_HTTP_PROXY"]
        with self.assertRaises(Exception):
            KubernetesConfiguration.get_http_proxy()
