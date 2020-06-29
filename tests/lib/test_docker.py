# pylint: disable=missing-function-docstring disable=missing-module-docstring

import subprocess
from unittest.mock import call

import pytest

import nestor_api.lib.config as config
import nestor_api.lib.docker as docker
import nestor_api.lib.git as git
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def test_build_already_built(mocker):
    mocker.patch.object(docker, "has_docker_image", return_value=True)
    mocker.patch.object(git, "get_last_tag", return_value="1.0.0-sha-a2b3c4")
    context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}

    image_tag = docker.build("my-app", context)

    git.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
    docker.has_docker_image.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")

    assert image_tag == "1.0.0-sha-a2b3c4"


def test_build(mocker):
    app_config = {"build": {"variables": {"var1": "val1", "var2": "val2"}}}

    mocker.patch.object(docker, "has_docker_image", return_value=False)
    mocker.patch.object(git, "get_last_tag", return_value="1.0.0-sha-a2b3c4")
    mocker.patch.object(config, "get_app_config", return_value=app_config)
    mocker.patch.object(io, "execute", return_value="")

    context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}

    image_tag = docker.build("my-app", context)

    git.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
    docker.has_docker_image.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
    config.get_app_config.assert_called_once_with("my-app")
    io.execute.assert_called_once_with(
        "docker build"
        " --tag my-app:1.0.0-sha-a2b3c4"
        " --build-arg var1=val1"
        " --build-arg var2=val2"
        " --build-arg COMMIT_HASH=a2b3c4"
        " /path_to/a_git_repository"
    )

    assert image_tag == "1.0.0-sha-a2b3c4"


def test_build_failure(mocker):
    app_config = {"build": {"variables": {"var1": "val1", "var2": "val2"}}}

    mocker.patch.object(docker, "has_docker_image", return_value=False)
    mocker.patch.object(git, "get_last_tag", return_value="1.0.0-sha-a2b3c4")
    mocker.patch.object(config, "get_app_config", return_value=app_config)

    exception = subprocess.CalledProcessError(1, "Docker build failed")
    mocker.patch.object(io, "execute", side_effect=[exception])
    mocker.patch.object(Logger, "error")

    context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}

    with pytest.raises(Exception, match="Docker build failed"):
        docker.build("my-app", context)

    git.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
    docker.has_docker_image.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
    config.get_app_config.assert_called_once_with("my-app")
    io.execute.assert_called_once_with(
        "docker build"
        " --tag my-app:1.0.0-sha-a2b3c4"
        " --build-arg var1=val1"
        " --build-arg var2=val2"
        " --build-arg COMMIT_HASH=a2b3c4"
        " /path_to/a_git_repository"
    )
    Logger.error.assert_called_once_with(
        {"err": exception},
        "Error while building Docker image"
    )


def test_get_registry_image_tag():
    registry_image_tag = docker.get_registry_image_tag(
        "my-app",
        "my-tag",
        {"organization": "my-organization"}
    )

    assert registry_image_tag == "my-organization/my-app:my-tag"


def test_has_docker_image_existing(mocker):
    mocker.patch.object(io, "execute", return_value="001122334455")

    has_image = docker.has_docker_image("my-app", "my-tag")

    io.execute.assert_called_once_with("docker images my-app:my-tag --quiet")
    assert has_image


def test_has_docker_image_not_existing(mocker):
    mocker.patch.object(io, "execute", return_value="")

    has_image = docker.has_docker_image("my-app", "my-tag")

    io.execute.assert_called_once_with("docker images my-app:my-tag --quiet")
    assert not has_image


def test_push_no_image(mocker):
    mocker.patch.object(
        config, "get_app_config",
        return_value={"docker": {"registry": {"organization": "my-organization"}}}
    )
    mocker.patch.object(git, "get_last_tag", return_value="1.0.0-sha-a2b3c4")
    mocker.patch.object(io, "execute", return_value="")

    with pytest.raises(RuntimeError, match="Docker image not available"):
        docker.push("my-app", "/path_to/a_git_repository")

    config.get_app_config.assert_called_once_with("my-app")
    git.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
    io.execute.assert_called_once_with('docker images my-app:1.0.0-sha-a2b3c4 --quiet')


def test_push(mocker):
    mocker.patch.object(
        config, "get_app_config",
        return_value={"docker": {"registry": {"organization": "my-organization"}}}
    )
    mocker.patch.object(git, "get_last_tag", return_value="1.0.0-sha-a2b3c4")
    mocker.patch.object(io, "execute", side_effect=["001122334455", "", ""])

    docker.push("my-app", "/path_to/a_git_repository")

    config.get_app_config.assert_called_once_with("my-app")
    git.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
    io.execute.assert_has_calls([
        call('docker images my-app:1.0.0-sha-a2b3c4 --quiet'),
        call('docker tag my-app:1.0.0-sha-a2b3c4 my-organization/my-app:1.0.0-sha-a2b3c4'),
        call('docker push my-organization/my-app:1.0.0-sha-a2b3c4')
    ])
