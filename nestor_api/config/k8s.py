"""Nestor-api k8s configuration"""
import os


# pylint: disable=too-few-public-methods
class K8sConfiguration:
    """k8s configuration"""

    @staticmethod
    def get_http_proxy() -> str:
        """Returns the k8s http proxy"""
        return os.environ["NESTOR_K8S_HTTP_PROXY"]
