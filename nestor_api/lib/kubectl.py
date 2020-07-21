"""Kubernetes' kubectl library"""

from enum import Enum
import json
import os

from nestor_api.config.kubernetes import KubernetesConfiguration
import nestor_api.lib.io as io


class KubernetesResourceType(Enum):
    """An enum representing the different resources kinds"""

    DEPLOYMENT = "deployment"

    def __str__(self):
        return str(self.value)


def _build_kubectl_env() -> dict:
    return {
        **os.environ,
        "HTTP_PROXY": KubernetesConfiguration.get_http_proxy(),
    }


# pylint: disable=bad-continuation
def fetch_resource_configuration(
    cluster_name: str, namespace: str, app_name: str, resource_type: KubernetesResourceType
) -> dict:
    """Fetch a resource configuration using kubectl"""
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
