import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.k8s import K8sConfiguration


class TestK8sConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_K8S_HTTP_PROXY": "k8s-proxy.my-domain.com"})
    def test_get_http_proxy(self):
        self.assertEqual(K8sConfiguration.get_http_proxy(), "k8s-proxy.my-domain.com")

    @patch.dict(os.environ, {"NESTOR_K8S_HTTP_PROXY": ""})
    def test_get_http_proxy_not_existing(self):
        del os.environ["NESTOR_K8S_HTTP_PROXY"]
        with self.assertRaises(KeyError):
            K8sConfiguration.get_http_proxy()

    @patch.dict(os.environ, {"NESTOR_K8S_TEMPLATE_FOLDER": ""})
    def test_get_templates_dir_default(self):
        del os.environ["NESTOR_K8S_TEMPLATE_FOLDER"]
        template_dir = K8sConfiguration.get_templates_dir()
        self.assertEqual(template_dir, "templates")

    @patch.dict(os.environ, {"NESTOR_K8S_TEMPLATE_FOLDER": "custom"})
    def test_get_templates_dir_configured(self):
        template_dir = K8sConfiguration.get_templates_dir()
        self.assertEqual(template_dir, "custom")
