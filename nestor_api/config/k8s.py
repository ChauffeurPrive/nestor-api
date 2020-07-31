"""Nestor-api k8s configuration"""
import os


class K8sConfiguration:
    """k8s configuration"""

    @staticmethod
    def get_http_proxy() -> str:
        """Returns the k8s http proxy"""
        return os.environ["NESTOR_K8S_HTTP_PROXY"]

    @staticmethod
    def get_service_port() -> int:
        """Returns the port to expose on the k8s services."""
        return int(os.getenv("NESTOR_K8S_SERVICE_PORT", "8080"))

    @staticmethod
    def get_templates_dir() -> str:
        """Returns the subfolder in which the k8s templates are stored."""
        return os.getenv("NESTOR_K8S_TEMPLATE_FOLDER", "templates")
