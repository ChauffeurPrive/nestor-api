"""Kubernetes deployment library."""

import os
from typing import Optional

from nestor_api.config.k8s import K8sConfiguration
import nestor_api.lib.config as config
import nestor_api.lib.io as io
import nestor_api.utils.list as list_utils

from . import builders, cli
from .enums.k8s_resource_kind import K8sResourceKind

WEB_PROCESS_NAME = "web"


def deploy_app(deployment_config: dict, config_dir: str, tag_to_deploy: str) -> dict:
    """Deploy a new version of an application on kubernetes
    following the provided configuration."""
    templates_path = os.path.join(config_dir, K8sConfiguration.get_templates_dir())
    templates = builders.load_templates(templates_path)

    previous_status = get_deployment_status(deployment_config)

    if has_process(deployment_config, WEB_PROCESS_NAME):
        deploy_app_ingress(deployment_config, WEB_PROCESS_NAME, templates)

    deployment_yaml = builders.build_deployment_yaml(deployment_config, templates, tag_to_deploy)
    write_and_deploy_configuration(deployment_config["cluster_name"], deployment_yaml)

    new_status = get_deployment_status(deployment_config)
    status_changes = get_deployment_statuses_diff(previous_status, new_status)

    return status_changes


def deploy_app_ingress(deployment_config: dict, process_name: str, templates: dict):
    """Deploy the ingress configuration of an app."""
    ingress_yaml = builders.build_ingress_yaml(deployment_config, process_name, templates)
    write_and_deploy_configuration(deployment_config["cluster_name"], ingress_yaml)


def _build_process_status(item: dict) -> dict:
    return {
        "name": item["spec"]["template"]["metadata"]["labels"]["process"],
        "image": item["spec"]["template"]["spec"]["containers"][0]["image"],
        "command": item["spec"]["template"]["spec"]["containers"][0]["args"][2],
    }


def _build_cronjob_status(item: dict) -> dict:
    job = _build_process_status(item["spec"]["jobTemplate"])
    return {**job, "schedule": item["spec"]["schedule"]}


def _build_variable_status(item: dict) -> list:
    if item["kind"] == K8sResourceKind.CRONJOB.value:
        item = item["spec"]["jobTemplate"]

    return item["spec"]["template"]["spec"]["containers"][0]["env"]


def get_deployment_status(deployment_config: dict) -> dict:
    """Retrieve the deployment status of a deployed application."""
    deployed_configuration = cli.fetch_resource_configuration(
        deployment_config["cluster_name"],
        deployment_config["namespace"],
        deployment_config["app"],
        [K8sResourceKind.DEPLOYMENT, K8sResourceKind.CRONJOB],
    )
    items = deployed_configuration["items"]

    status: dict = {
        "processes": [],
        "cronjobs": [],
        "env": [],
    }
    if len(items) == 0:
        return status

    for item in items:
        if item["kind"] == K8sResourceKind.DEPLOYMENT.value:
            process = _build_process_status(item)
            status["processes"].append(process)
        elif item["kind"] == K8sResourceKind.CRONJOB.value:
            cronjob = _build_cronjob_status(item)
            status["cronjobs"].append(cronjob)
        else:
            raise ValueError(f'Unknown item kind "{item["kind"]}"')

    # Take the first item, maybe the only one, to extract the environment variables
    # from it. The one we select is not important because they all share the same variables.
    status["env"] = _build_variable_status(items[0])

    return status


def _get_name(item: dict) -> str:
    return item["name"]


def _compare_job_keys(job_1: dict, job_2: dict) -> Optional[dict]:
    differences = {}
    for key in job_1:
        if job_1[key] != job_2[key]:
            differences[key] = {"old": job_1[key], "new": job_2[key]}

    return {"name": _get_name(job_1), "values": differences} if len(differences) > 0 else None


def _compare_env_vars(var_1: dict, var_2: dict) -> Optional[dict]:
    value_1 = var_1["value"] if "value" in var_1 else var_1["valueFrom"]
    value_2 = var_2["value"] if "value" in var_2 else var_2["valueFrom"]
    return (
        None
        if value_1 == value_2
        else {"name": var_1["name"], "value": {"old": value_1, "new": value_2}}
    )


def get_deployment_statuses_diff(deployment_1: dict, deployment_2: dict) -> dict:
    """Compute the differences between 2 deployment statuses."""
    return {
        "processes": list_utils.compute_diff(
            deployment_1["processes"],
            deployment_2["processes"],
            key=_get_name,
            comparator=_compare_job_keys,
        ),
        "cronjobs": list_utils.compute_diff(
            deployment_1["cronjobs"],
            deployment_2["cronjobs"],
            key=_get_name,
            comparator=_compare_job_keys,
        ),
        "env": list_utils.compute_diff(
            deployment_1["env"], deployment_2["env"], key=_get_name, comparator=_compare_env_vars
        ),
    }


def has_process(deployment_config: dict, process_name: str) -> bool:
    """Returns `True` if the specified process is defined in the configuration."""
    processes = config.get_processes(deployment_config)
    process = list_utils.find(processes, lambda process: process["name"] == process_name)
    return process is not None


def write_and_deploy_configuration(cluster_name: str, yaml_config: str) -> None:
    """Write the kubernetes configuration into a local file and
    apply it on the cluster with the cli."""
    output_directory = io.create_temporary_directory()
    yaml_path = os.path.join(output_directory, "config.yaml")

    try:
        io.write(yaml_path, yaml_config)
        cli.apply_config(cluster_name, yaml_path)
    finally:
        io.remove(output_directory)
