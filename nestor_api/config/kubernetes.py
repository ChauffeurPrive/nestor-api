"""Nestor-api kubernetes configuration"""
import os


# pylint: disable=too-few-public-methods
class KubernetesConfiguration:
    """Kubernetes configuration"""

    @staticmethod
    def get_http_proxy() -> str:
        """Returns the kubernetes http proxy"""
        return os.environ["NESTOR_K8S_HTTP_PROXY"]
