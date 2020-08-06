"""Kubernetes deployment library."""

import os

from nestor_api.config.k8s import K8sConfiguration
import nestor_api.lib.config as config
import nestor_api.lib.io as io
import nestor_api.utils.list as list_utils

from . import builders, cli
from .enums.k8s_resource_type import K8sResourceType

WEB_PROCESS_NAME = "web"


def deploy_app(deployment_config: dict, config_dir: str, tag_to_deploy: str) -> None:
    """Deploy a new version of an application on kubernetes
    following the provided configuration."""
    templates_path = os.path.join(config_dir, K8sConfiguration.get_templates_dir())
    templates = builders.load_templates(templates_path)

    # Awaiting for implementation
    # --> Fetch the previous configuration

    if has_process(deployment_config, WEB_PROCESS_NAME):
        deploy_app_ingress(deployment_config, WEB_PROCESS_NAME, templates)

    deployment_yaml = builders.build_deployment_yaml(deployment_config, templates, tag_to_deploy)
    write_and_deploy_configuration(deployment_config["cluster_name"], deployment_yaml)

    # Awaiting for implementation
    # --> Fetch the new configuration
    # --> Compare the 2 configurations and generate a report
    # --> Return the report


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
    if item["kind"] == "CronJob":
        item = item["spec"]["jobTemplate"]

    return item["spec"]["template"]["spec"]["containers"][0]["env"]


def get_deployment_status(deployment_config: dict) -> dict:
    """Retrieve the deployment status of a deployed application."""
    deployed_configuration = cli.fetch_resource_configuration(
        deployment_config["cluster_name"],
        deployment_config["namespace"],
        deployment_config["app"],
        [K8sResourceType.DEPLOYMENTS, K8sResourceType.CRONJOBS],
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
        if item["kind"] == "Deployment":
            process = _build_process_status(item)
            status["processes"].append(process)
        elif item["kind"] == "CronJob":
            cronjob = _build_cronjob_status(item)
            status["cronjobs"].append(cronjob)
        else:
            raise ValueError(f'Unknown item kind "{item["kind"]}"')

    # Take the first item, maybe the only one, to extract the environment variables
    # from it. The one we select is not important because they all share the same variables.
    status["env"] = _build_variable_status(items[0])

    return status


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
