"""k8s deployment file builders"""

import os
import time
from typing import Optional, Tuple

from pybars import Compiler  # type: ignore

from nestor_api.config.k8s import K8sConfiguration
from nestor_api.config.probes import ProbesDefaultConfiguration
from nestor_api.config.replicas import ReplicasDefaultConfiguration
import nestor_api.lib.config as config
import nestor_api.lib.docker as docker
import nestor_api.lib.io as io
import nestor_api.utils.dict as dict_utils
import nestor_api.utils.list as list_utils
import yaml_lib


def build_yaml(deployment_config: dict, templates_path: str, tag_to_deploy: str) -> str:
    """Builds the deployment.yaml corresponding to the provided k8s deployment configuration."""
    templates = load_templates(templates_path, TEMPLATES)

    yaml_sections = []

    processes = config.get_processes(deployment_config)
    for process in processes:
        sections = get_sections_for_process(process, deployment_config, tag_to_deploy, templates)
        yaml_sections.extend(sections)

    cronjobs = config.get_cronjobs(deployment_config)
    for cronjob in cronjobs:
        sections = get_sections_for_cronjob(cronjob, deployment_config, tag_to_deploy, templates)
        yaml_sections.extend(sections)

    return "\n".join(yaml_sections)


TEMPLATES = [
    "deployment",
    "hpa",
    "anti-affinity-node",
    "anti-affinity-zone",
    "service",
    "namespace",
    "cronjob",
    "job",
]


def _load_template(templates_path: str, template_compiler: Compiler, template_name: str):
    """Load a single handlebar template."""
    template_path = os.path.join(templates_path, f"{template_name}.yaml")
    file_content = io.read(template_path)
    return template_compiler.compile(file_content)


def load_templates(templates_path: str, template_names: list) -> dict:
    """Load the templates from the configuration path."""
    template_compiler = Compiler()
    return {
        template: _load_template(templates_path, template_compiler, template)
        for template in template_names
    }


def get_sections_for_process(
    process: dict, deployment_config: dict, tag_to_deploy: str, templates: dict
) -> list:
    """Build the deployment sections of a process."""
    process_name = process["name"]
    app_name, sanitized_process_name, metadata_name = get_sanitized_names(
        deployment_config, process_name
    )
    image_name = get_image_name(deployment_config, {"tag": tag_to_deploy})

    deployment_sections = []

    if process_name == "web":
        web_service = yaml_lib.parse_yaml(
            templates["service"](
                {
                    "app": app_name,
                    "name": app_name,
                    "image": image_name,
                    "target_port": K8sConfiguration.get_service_port(),
                    **deployment_config.get("templateVars", {}),
                }
            )
        )
        deployment_sections.append(web_service)

    deployment = yaml_lib.parse_yaml(
        templates["deployment"](
            {
                "app": app_name,
                "name": metadata_name,
                "image": image_name,
                "process": sanitized_process_name,
                "project": deployment_config["project"],
                **deployment_config.get("templateVars", {}),
            }
        )
    )

    timestamp = round(time.time() * 1000)  # timestamp in milliseconds
    deployment["spec"]["template"]["metadata"]["annotations"] = {"date": str(timestamp)}

    set_secret(deployment_config, deployment)

    hpa = set_replicas(deployment_config, process_name, deployment, templates)
    if hpa:
        deployment_sections.append(hpa)

    set_anti_affinity(deployment_config, process_name, deployment, templates)

    set_node_selector(deployment_config, process_name, deployment)

    set_resources(deployment_config, process_name, deployment)

    set_command(process, deployment)

    set_probes(deployment_config, process_name, deployment)

    deployment["spec"]["template"]["spec"]["containers"][0]["ports"] = [
        {"containerPort": K8sConfiguration.get_service_port()}
    ]

    set_environment_variables(deployment_config, deployment)

    deployment_sections.append(deployment)

    namespace = set_namespace(deployment_config, deployment_sections, templates)
    if namespace:
        deployment_sections.insert(0, namespace)

    return list_utils.flatten(
        [["---", yaml_lib.convert_to_yaml(section)] for section in deployment_sections]
    )


def get_sections_for_cronjob(
    process: dict, deployment_config: dict, tag_to_deploy: str, templates: dict
) -> list:
    """Build the deployment sections of a cronjob."""
    process_name = process["name"]
    app_name, sanitized_process_name, metadata_name = get_sanitized_names(
        deployment_config, process_name
    )
    image_name = get_image_name(deployment_config, {"tag": tag_to_deploy})

    cronjob_sections = []

    cronjob = yaml_lib.parse_yaml(
        templates["cronjob"](
            {
                "app": app_name,
                "name": metadata_name,
                "image": image_name,
                "process": sanitized_process_name,
                "project": deployment_config["project"],
                **deployment_config.get("templateVars", {}),
            }
        )
    )
    cronjob["spec"]["schedule"] = deployment_config["crons"][process_name]["schedule"]
    cronjob["spec"]["concurrencyPolicy"] = deployment_config["crons"][process_name][
        "concurrency_policy"
    ]

    job = yaml_lib.parse_yaml(
        templates["job"](
            {
                "app": app_name,
                "name": metadata_name,
                "image": image_name,
                "process": sanitized_process_name,
                "project": deployment_config["project"],
            }
        )
    )

    set_secret(deployment_config, job)

    set_resources(deployment_config, process_name, job)

    set_command(process, job)

    set_environment_variables(deployment_config, job)
    set_node_selector(deployment_config, process_name, job)

    cronjob["spec"]["jobTemplate"]["spec"] = job["spec"]
    cronjob_sections.append(cronjob)

    namespace = set_namespace(deployment_config, cronjob_sections, templates)
    if namespace:
        cronjob_sections.insert(0, namespace)

    return list_utils.flatten(
        [["---", yaml_lib.convert_to_yaml(section)] for section in cronjob_sections]
    )


def get_anti_affinity_node(
    deployment_config: dict, process_name: str, templates: dict
) -> Optional[dict]:
    """Return the anti affinity for node configuration"""
    app_name = deployment_config["app"]
    is_anti_affinity_node_default_enabled = deployment_config["affinity"]["default"][
        "is_anti_affinity_node_enabled"
    ]
    is_anti_affinity_node_process_enabled = (
        deployment_config["affinity"]
        .get(process_name, {})
        .get("is_anti_affinity_node_enabled", False)
    )

    anti_affinity_node = None

    if is_anti_affinity_node_default_enabled or is_anti_affinity_node_process_enabled:
        anti_affinity_node = yaml_lib.parse_yaml(
            templates["anti-affinity-node"]({"app": app_name, "process": process_name}),
        )

    return anti_affinity_node


def get_anti_affinity_zone(
    deployment_config: dict, process_name: str, templates: dict
) -> Optional[dict]:
    """Return the anti affinity for zone configuration."""
    app_name = deployment_config["app"]
    is_anti_affinity_zone_default_enabled = deployment_config["affinity"]["default"][
        "is_anti_affinity_zone_enabled"
    ]
    is_anti_affinity_zone_process_enabled = (
        deployment_config["affinity"]
        .get(process_name, {})
        .get("is_anti_affinity_zone_enabled", False)
    )

    anti_affinity_zone = None

    if is_anti_affinity_zone_default_enabled or is_anti_affinity_zone_process_enabled:
        anti_affinity_zone = yaml_lib.parse_yaml(
            templates["anti-affinity-zone"]({"app": app_name, "process": process_name}),
        )

    return anti_affinity_zone


def get_image_name(deployment_config: dict, options: dict) -> str:
    """Returns the definitive image name."""
    image_name = deployment_config["docker"].get("image_name") or deployment_config["app"]
    registry = deployment_config["docker"]["registry"]
    image_tag = options["branch"] if "branch" in options else options["tag"]

    return docker.get_registry_image_tag(image_name, image_tag, registry)


def get_probes(probes_config: dict, port: int) -> dict:
    """Returns probes definition."""
    # The probes configuration can either be unique or specific for liveness and readiness,
    # If it is unique, `probes_config` contains the config for both probes
    liveness_probe_config = probes_config.get("liveness")
    readiness_probe_config = probes_config.get("readiness")
    if liveness_probe_config is None and readiness_probe_config is None:
        liveness_probe_config = probes_config
        readiness_probe_config = probes_config

    probes = {}

    probes_to_configure = []

    if liveness_probe_config is not None:
        probes_to_configure.append({"name": "livenessProbe", "config": liveness_probe_config})
    if readiness_probe_config is not None:
        probes_to_configure.append({"name": "readinessProbe", "config": readiness_probe_config})

    for probe_to_configure in probes_to_configure:
        probe = {
            "httpGet": {"path": probe_to_configure["config"]["path"], "port": port},
            "initialDelaySeconds": probe_to_configure["config"].get(
                "delay", ProbesDefaultConfiguration.get_default_delay(),
            ),
            "periodSeconds": probe_to_configure["config"].get(
                "period", ProbesDefaultConfiguration.get_default_period(),
            ),
            "timeoutSeconds": probe_to_configure["config"].get(
                "timeout", ProbesDefaultConfiguration.get_default_timeout(),
            ),
        }
        probes[probe_to_configure["name"]] = probe

    return probes


def get_sanitized_names(deployment_config: dict, process_name: str) -> Tuple[str, str, str]:
    """Return the names used in the Kubernetes templates: app, process name and metadata name."""
    app = deployment_config["app"]
    sanitized_process_name = process_name.replace("_", "-").lower()
    metadata_name = f"{app}----{sanitized_process_name}"

    return app, sanitized_process_name, metadata_name


def get_secret_variables(app_config: dict) -> dict:
    """Returns the secret variables from configuration."""
    secret_variables = app_config.get("variables", {}).get("secret", {})

    formatted_secret_variables = {
        secret_name: {
            "secretKeyRef": {
                "name": secret_variables[secret_name]["name"],
                "key": secret_variables[secret_name]["key"],
            },
        }
        for secret_name in secret_variables.keys()
    }

    return formatted_secret_variables


def get_variables(deployment_config: dict) -> dict:
    """Environment variables update to support the 2 level of definition
    - ope for operational environment variables
    - app for application level environment variables
    """
    variables = deployment_config.get("variables", {})

    app_variables = variables.get("app", {})
    ope_variables = variables.get("ope", {})

    return {
        **app_variables,
        **ope_variables,
    }


def set_anti_affinity(
    deployment_config: dict, process_name: str, resource: dict, templates: dict
) -> None:
    """Attach the expected anti_affinity to the resource."""
    anti_affinity_node = get_anti_affinity_node(deployment_config, process_name, templates) or {}
    anti_affinity_zone = get_anti_affinity_zone(deployment_config, process_name, templates) or {}
    anti_affinity = dict_utils.deep_merge(anti_affinity_node, anti_affinity_zone, concat_lists=True)
    if len(anti_affinity) > 0:
        resource["spec"]["template"]["spec"]["affinity"] = anti_affinity


def set_command(process: dict, resource: dict) -> None:
    """Attach the expected command to the resource."""
    resource["spec"]["template"]["spec"]["containers"][0]["args"] = [
        "/bin/bash",
        "-c",
        process["start_command"],
    ]


def set_environment_variables(deployment_config: dict, resource: dict) -> None:
    """Format and attach the environment variables to the resource."""
    secret_variables = get_secret_variables(deployment_config)
    variables = get_variables(deployment_config)
    variables["PORT"] = str(K8sConfiguration.get_service_port())

    environment_variables = [{"name": key, "value": value} for key, value in variables.items()]
    environment_variables += [
        {"name": key, "valueFrom": value} for key, value in secret_variables.items()
    ]

    resource["spec"]["template"]["spec"]["containers"][0]["env"] = environment_variables


def set_namespace(deployment_config: dict, resources: list, templates: dict) -> Optional[dict]:
    """Attach the expected namespace to the deployment and return the namespace."""
    namespace = None
    namespace_name = deployment_config.get("namespace")

    if namespace_name is not None:
        for resource in resources:
            resource["metadata"]["namespace"] = namespace_name
        namespace = yaml_lib.parse_yaml(templates["namespace"]({"name": namespace_name}),)

    return namespace


def set_node_selector(deployment_config: dict, process_name: str, resource: dict) -> None:
    """Attach the correct nodeSelector to the resource."""
    node_selector = deployment_config["nodeSelector"].get(process_name) or deployment_config[
        "nodeSelector"
    ].get("default")
    if node_selector is not None:
        resource["spec"]["template"]["spec"]["nodeSelector"] = node_selector


def set_probes(deployment_config: dict, process_name: str, resource: dict) -> None:
    """Attach the process' probes to the resource if configured."""
    if process_name in deployment_config["probes"]:
        probes_config = deployment_config["probes"][process_name]
        probes = get_probes(probes_config, K8sConfiguration.get_service_port())
        if "livenessProbe" in probes:
            resource["spec"]["template"]["spec"]["containers"][0]["livenessProbe"] = probes[
                "livenessProbe"
            ]
        if "readinessProbe" in probes:
            resource["spec"]["template"]["spec"]["containers"][0]["readinessProbe"] = probes[
                "readinessProbe"
            ]


def set_replicas(
    deployment_config: dict, process_name: str, recipe: dict, templates: dict
) -> Optional[dict]:
    """Attach the correct Replicas values to the recipe object and return the corresponding
    `hpa` if applicable."""
    scales = deployment_config["scales"]
    scales_config = scales[process_name] if process_name in scales else scales["default"]
    min_replicas = scales_config.get(
        "minReplicas", ReplicasDefaultConfiguration.get_default_min_replicas()
    )
    max_replicas = scales_config.get(
        "maxReplicas", ReplicasDefaultConfiguration.get_default_max_replicas()
    )
    target_cpu_utilization_percentage = scales_config.get(
        "targetCPUUtilizationPercentage",
        ReplicasDefaultConfiguration.get_default_target_cpu_utilization_percentage(),
    )

    if min_replicas == 0:
        recipe["spec"]["replicas"] = 0
        return None

    # Create the HorizontalPodAutoscaler for this deployment

    app, sanitized_process_name, metadata_name = get_sanitized_names(
        deployment_config, process_name
    )

    template_vars = {
        "app": app,
        "process": sanitized_process_name,
        "name": metadata_name,
        "minReplicas": min_replicas,
        "maxReplicas": max_replicas,
        "targetCPUUtilizationPercentage": target_cpu_utilization_percentage,
        **deployment_config.get("templateVars", {}),
    }

    return yaml_lib.parse_yaml(templates["hpa"](template_vars))


def set_resources(deployment_config: dict, process_name: str, recipe: dict) -> None:
    """Attach the expected resources to the kubernetes recipe."""
    resources = deployment_config.get("resources", {})
    resources_config = (
        resources[process_name] if process_name in resources else resources.get("default")
    )

    if resources_config is not None:
        recipe["spec"]["template"]["spec"]["containers"][0]["resources"] = resources_config


def set_secret(deployment_config: dict, resource: dict) -> None:
    """Attach the secret to the resource if present in the configuration."""
    if "secret" in deployment_config:
        resource["spec"]["template"]["spec"]["imagePullSecrets"] = [
            {"name": deployment_config["secret"]}
        ]
