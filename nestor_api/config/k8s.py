"""Nestor-api k8s configuration"""
import os


class K8sConfiguration:
    """k8s configuration"""

    @staticmethod
    def get_http_proxy() -> str:
        """Returns the k8s http proxy"""
        return os.environ["NESTOR_K8S_HTTP_PROXY"]

    @staticmethod
    def get_templates_dir() -> str:
        """Returns the name of the config sub-folder in which to look for templates."""
        return os.getenv("NESTOR_K8S_TEMPLATE_FOLDER", "templates")
