"""Docker library"""

import nestor_api.lib.config as config
import nestor_api.lib.git as git
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def build(app_name, context):
    """Build the docker image of the last version of the app
    Example:
        > app_name = "my-app"
        > context = {"repository": "/path_to/my-app-doc", "commit_hash": "a2b3c4"}
        > build(app_name, context)
    """
    repository = context["repository"]
    image_tag = git.get_last_tag(repository)

    Logger.info(
        {"tag": f"{app_name}@{image_tag}"}, "Application name and version",
    )

    if has_docker_image(app_name, image_tag):
        Logger.info({}, "Docker image already built (skipped)")
        return image_tag

    app_config = config.get_app_config(app_name)
    commit_hash = context["commit_hash"]
    build_variables = app_config["build"]["variables"]

    # Application build environment variables:
    builds_args = []
    for key, value in build_variables.items():
        builds_args.append(f"--build-arg {key}={value}")

    builds_args.append(f"--build-arg COMMIT_HASH={commit_hash}")
    builds_args_str = " ".join(builds_args)

    command = f"docker build --tag {app_name}:{image_tag} {builds_args_str} {repository}"

    Logger.debug({"command": command}, "Docker build command")

    try:
        io.execute(command)
    except Exception as err:
        Logger.error({"err": err}, "Error while building Docker image")
        raise err

    return image_tag


def has_docker_image(app_name, tag):
    """Checks if the docker image already exists for a given app and tag"""
    stdout = io.execute(f"docker images {app_name}:{tag} --quiet")
    return len(stdout) != 0


def get_registry_image_tag(app_name, image_tag, registry):
    """Returns the image name for a given organization, app and tag"""
    return f"{registry['organization']}/{app_name}:{image_tag}"


def push(app_name, repository):
    """Push an image to the configured docker registry"""

    # This will need to be done a bit differently to work with GCP registry

    app_config = config.get_app_config(app_name)

    image_tag = git.get_last_tag(repository)

    if not has_docker_image(app_name, image_tag):
        raise RuntimeError("Docker image not available")

    registry = app_config["docker"]["registry"]

    # Create the tag
    image = get_registry_image_tag(app_name, image_tag, registry)

    io.execute(f"docker tag {app_name}:{image_tag} {image}")

    io.execute(f"docker push {image}")
