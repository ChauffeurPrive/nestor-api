"""Kubernetes' kubectl library"""

import json
import os

from nestor_api.config.k8s import K8sConfiguration
import nestor_api.lib.io as io

from .enums.k8s_resource_type import K8sResourceType


def _build_kubectl_env() -> dict:
    return {
        **os.environ,
        "HTTP_PROXY": K8sConfiguration.get_http_proxy(),
    }


# pylint: disable=bad-continuation
def fetch_resource_configuration(
    cluster_name: str, namespace: str, app_name: str, resource_type: K8sResourceType
) -> dict:
    """Fetch a resource's configuration using kubectl"""
    command = (
        "kubectl "
        f"--context {cluster_name} "
        f"--namespace {namespace} "
        f"get {str(resource_type)} "
        "--output=json "
        f"--selector app={app_name}"
    )
    env = _build_kubectl_env()

    stdout = io.execute(command, env=env)

    return json.loads(stdout)
