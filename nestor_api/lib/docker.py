"""Docker library"""

import nestor_api.lib.git as git
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def build(app_name: str, repository: str, app_config: dict) -> str:
    """Build the docker image of the last version of the app"""
    image_tag = git.get_last_tag(repository)

    Logger.info(
        {"tag": f"{app_name}@{image_tag}"}, "Application name and version",
    )

    if has_docker_image(app_name, image_tag):
        Logger.info({}, "Docker image already built (skipped)")
        return image_tag

    commit_hash = git.get_commit_hash_from_tag(repository, image_tag)
    build_variables = app_config.get("docker", {}).get("build", {}).get("variables", {})
    build_variables["COMMIT_HASH"] = commit_hash

    # Application build environment variables:
    builds_args = []
    for key, value in build_variables.items():
        builds_args.append(f"--build-arg {key}={value}")

    builds_args_str = " ".join(builds_args)

    command = f"docker build --tag {app_name}:{image_tag} {builds_args_str} {repository}"

    Logger.debug({"command": command}, "Docker build command")

    try:
        io.execute(command)
    except Exception as err:
        Logger.error({"err": err}, "Error while building Docker image")
        raise err

    return image_tag


def has_docker_image(app_name: str, tag: str) -> bool:
    """Checks if the docker image already exists for a given app and tag"""
    stdout = io.execute(f"docker images {app_name}:{tag} --quiet")
    return len(stdout) != 0


def get_registry_image_tag(app_name: str, image_tag: str, registry: dict) -> str:
    """Returns the image name for a given organization, app and tag"""
    return f"{registry['organization']}/{app_name}:{image_tag}"


def push(app_name: str, image_tag: str, app_config: dict) -> None:
    """Push an image to the configured docker registry"""
    if not has_docker_image(app_name, image_tag):
        raise RuntimeError("Docker image not available")

    # This will need to be done a bit differently to work with other registries (GCP)
    # -> the config schema currently expects
    #   {docker: {registries: {[name: string]: {id: string, organization: string}[]}}}
    registry = app_config["docker"]["registries"]["docker.com"][0]

    # Create the tag
    image = get_registry_image_tag(app_name, image_tag, registry)

    io.execute(f"docker tag {app_name}:{image_tag} {image}")

    io.execute(f"docker push {image}")
