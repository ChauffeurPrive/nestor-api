"""Kubernetes' kubectl library."""

import json
import os
from typing import List

from nestor_api.config.k8s import K8sConfiguration
import nestor_api.lib.io as io

from .enums.k8s_resource_kind import K8sResourceKind


def _build_kubectl_env() -> dict:
    return {
        **os.environ,
        "HTTP_PROXY": K8sConfiguration.get_http_proxy(),
    }


def fetch_resource_configuration(
    cluster_name: str, namespace: str, app_name: str, resources: List[K8sResourceKind]
) -> dict:
    """Fetch a resource's configuration using kubectl."""
    resources_str = ",".join([str(resource) for resource in resources])
    command = (
        "kubectl "
        f"--context {cluster_name} "
        f"--namespace {namespace} "
        f"get {resources_str} "
        "--output=json "
        f"--selector app={app_name}"
    )
    env = _build_kubectl_env()

    stdout = io.execute(command, env=env)

    return json.loads(stdout)


def apply_config(cluster_name: str, yaml_path: str) -> None:
    """Apply the k8s configuration using kubectl."""
    command = "kubectl " f"--context {cluster_name} " f"apply -f {yaml_path}"
    env = _build_kubectl_env()

    io.execute(command, env=env)
