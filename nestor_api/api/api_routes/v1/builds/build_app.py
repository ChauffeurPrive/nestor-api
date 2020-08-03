"""Defines the builds route."""

from http import HTTPStatus
from threading import Thread

from nestor_api.config.config import Configuration
import nestor_api.lib.app as app
import nestor_api.lib.config as config
import nestor_api.lib.docker as docker
import nestor_api.lib.git as git
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


# pylint: disable=broad-except
def _differed_build(app_name: str):
    config_dir = None
    app_dir = None

    try:
        # Retrieve app's configuration
        config_dir = config.create_temporary_config_copy()
        config.change_environment(Configuration.get_config_default_branch(), config_dir)
        app_config = config.get_app_config(app_name, config_dir)
        Logger.debug(
            {"app": app_name, "config_directory": config_dir},
            "[/api/v1/builds/:app] Application's configuration retrieved",
        )

        # Retrieve app's repository
        app_dir = git.create_working_repository(app_name, app_config["git"]["origin"])
        git.branch(app_dir, app_config["workflow"][0])
        Logger.debug(
            {"app": app_name, "working_directory": app_dir},
            "[/api/v1/builds/:app] Application's repository retrieved",
        )

        try:
            # Create a new tag
            version = app.get_version(app_dir)
            git_tag = git.tag(app_dir, version)
            Logger.debug(
                {"app": app_name, "tag": git_tag}, "[/api/v1/builds/:app] New tag created",
            )
        except Exception as err:
            # The tag may already exist
            Logger.warn(
                {"app": app_name, "err": err}, "[/api/v1/builds/:app] Error while tagging the app"
            )

        # Build and publish the new docker image
        image_tag = docker.build(app_name, app_dir, app_config)
        Logger.debug(
            {"app": app_name, "image": image_tag}, "[/api/v1/builds/:app] Docker image created"
        )
        docker.push(app_name, image_tag, app_config)
        Logger.debug(
            {"app": app_name, "image": image_tag},
            "[/api/v1/builds/:app] Docker image published on registry",
        )

        # Send the new tag to git
        git.push(app_dir)
        Logger.debug({"app": app_name}, "[/api/v1/builds/:app] Tag pushed to Git")

    except Exception as err:
        Logger.error(
            {"app": app_name, "err": err},
            "[/api/v1/builds/:app] Error while tagging and building the app",
        )

    # Clean up temporary directories
    try:
        if config_dir is not None:
            io.remove(config_dir)
        if app_dir is not None:
            io.remove(app_dir)
    except Exception as err:
        Logger.error({"app": app_name, "err": err}, "[/api/v1/builds/:app] Error during cleanup")


def build_app(app_name: str):
    """Build the docker image of an application from the master branch with
    a unique tag and uploads it to the configured Docker registry."""
    Logger.info({"app": app_name}, "[/api/v1/builds/:app] Building an application image")

    Thread(target=_differed_build, args=[app_name]).start()

    return "Build processing", HTTPStatus.ACCEPTED
