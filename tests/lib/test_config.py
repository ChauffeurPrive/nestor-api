# pylint: disable=missing-function-docstring disable=missing-module-docstring

from unittest.mock import call

import pytest

from nestor_api.config.config import Configuration
import nestor_api.lib.config as config
from nestor_api.lib.errors import AppConfigurationNotFoundError
import nestor_api.lib.io as io


def test_change_environment(mocker):
    spy = mocker.patch.object(io, "execute")

    config.change_environment("environment", "path/to/config")

    spy.assert_has_calls(
        [
            call("git stash", "path/to/config"),
            call("git fetch origin", "path/to/config"),
            call("git checkout environment", "path/to/config"),
            call("git reset --hard origin/environment", "path/to/config"),
        ]
    )


@pytest.mark.usefixtures("config")
def test_create_temporary_directory(mocker):
    spy = mocker.patch.object(io, "create_temporary_copy")

    config.create_temporary_config_copy()

    spy.assert_called_once_with("/fixtures-nestor-config", "config")


def test_get_app_config(mocker):
    mocker.patch.object(Configuration, "get_config_path", return_value="tests/__fixtures__/config")

    app_config = config.get_app_config("app")

    assert app_config == {
        "domain": "website.com",
        "sub_domain": "app",
        "variables": {
            "ope": {
                "VARIABLE_OPE_1": "ope_1",
                "VARIABLE_OPE_2": "ope_2_override",
                "VARIABLE_OPE_3": "ope_3",
            },
            "app": {
                "VARIABLE_APP_1": "app_1",
                "VARIABLE_APP_2": "app_2_override",
                "VARIABLE_APP_3": "app_3",
            },
        },
    }


@pytest.mark.usefixtures("config")
def test_get_app_config_when_not_found(mocker):
    mocker.patch.object(io, "exists", return_value=False)

    with pytest.raises(AppConfigurationNotFoundError):
        config.get_app_config("app")


def test_get_environment_config(mocker):
    mocker.patch.object(Configuration, "get_config_path", return_value="tests/__fixtures__/config")

    environment_config = config.get_environment_config()

    assert environment_config == {
        "domain": "website.com",
        "variables": {
            "ope": {"VARIABLE_OPE_1": "ope_1", "VARIABLE_OPE_2": "ope_2"},
            "app": {"VARIABLE_APP_1": "app_1", "VARIABLE_APP_2": "app_2"},
        },
    }


@pytest.mark.usefixtures("config")
def test_get_environment_config_when_not_found(mocker):
    mocker.patch.object(io, "exists", return_value=False)

    with pytest.raises(FileNotFoundError):
        config.get_environment_config()
