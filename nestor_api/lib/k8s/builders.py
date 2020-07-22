"""k8s deployment file builders"""

from typing import Optional

from nestor_api.config.probes import ProbesDefaultConfiguration
import nestor_api.lib.docker as docker
import yaml_lib


def get_anti_affinity_node(app_config: dict, process_name: str, templates: dict) -> Optional[dict]:
    """Return the anti affinity for node configuration"""
    app_name = app_config["app"]
    is_anti_affinity_node_default_enabled = app_config["affinity"]["default"][
        "is_anti_affinity_node_enabled"
    ]
    is_anti_affinity_node_process_enabled = (
        app_config["affinity"].get(process_name, {}).get("is_anti_affinity_node_enabled", False)
    )

    anti_affinity_node = None

    if is_anti_affinity_node_default_enabled or is_anti_affinity_node_process_enabled:
        anti_affinity_node = yaml_lib.parse_yaml(
            templates["anti_affinity_node"]({"app": app_name, "process": process_name}),
        )

    return anti_affinity_node


def get_anti_affinity_zone(app_config: dict, process_name: str, templates: dict) -> Optional[dict]:
    """Return the anti affinity for zone configuration"""
    app_name = app_config["app"]
    is_anti_affinity_zone_default_enabled = app_config["affinity"]["default"][
        "is_anti_affinity_zone_enabled"
    ]
    is_anti_affinity_zone_process_enabled = (
        app_config["affinity"].get(process_name, {}).get("is_anti_affinity_zone_enabled", False)
    )

    anti_affinity_zone = None

    if is_anti_affinity_zone_default_enabled or is_anti_affinity_zone_process_enabled:
        anti_affinity_zone = yaml_lib.parse_yaml(
            templates["anti_affinity_zone"]({"app": app_name, "process": process_name}),
        )

    return anti_affinity_zone


def get_image_name(app_config, options):
    """Returns the definitive image name"""
    image_tag = options["tag"]
    branch = options.get("branch")

    if branch is not None:
        image_tag = branch

    return docker.get_registry_image_tag(app_config["app"], image_tag, app_config["registry"])


def get_probes(probes_config: dict, port: int):
    """Returns probes definition"""
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
            "httpGet": {"path": probe_to_configure["config"]["path"], "port": port,},
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


def get_sanitized_names(app_config: dict, process_name: str):
    """Return the names used in the Kubernetes templates: app, process name and metadata name."""
    app = app_config["app"]
    sanitized_process_name = process_name.replace("_", "-").lower()
    metadata_name = f"{app}----{sanitized_process_name}"

    return app, sanitized_process_name, metadata_name


def get_secret_variables(app_config) -> dict:
    """Returns the secret variables from configuration"""
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


def get_variables(app_config: dict) -> dict:
    """Environment variables update to support the 2 level of definition
    - ope for operational environment variables
    - app for application level environment variables
    """
    variables = app_config.get("variables", {})

    app_variables = variables.get("app", {})
    ope_variables = variables.get("ope", {})

    return {
        **app_variables,
        **ope_variables,
    }
