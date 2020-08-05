"""Kubernetes deployment library."""

import os

from nestor_api.config.k8s import K8sConfiguration
import nestor_api.lib.config as config
import nestor_api.lib.io as io
import nestor_api.utils.list as list_utils

from . import builders, cli

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
