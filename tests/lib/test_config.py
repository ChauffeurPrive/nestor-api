# pylint: disable=missing-function-docstring disable=missing-module-docstring

from unittest.mock import call

import pytest

from nestor_api.config.config import Configuration
from nestor_api.errors.app_configuration_not_found_error import AppConfigurationNotFoundError
import nestor_api.lib.config as config
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
def test_create_temporary_config_copy(mocker):
    spy = mocker.patch.object(io, "create_temporary_copy", return_value="/temporary/path")

    path = config.create_temporary_config_copy()

    spy.assert_called_once_with("/fixtures-nestor-config", "config")
    assert path == "/temporary/path"


def test_get_app_config(mocker):
    mocker.patch.object(Configuration, "get_config_path", return_value="tests/__fixtures__/config")

    app_config = config.get_app_config("backoffice")

    assert app_config == {
        "domain": "website.com",
        "sub_domain": "backoffice",
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
        config.get_app_config("app_not_here")


def test_get_project_config(mocker):
    mocker.patch.object(Configuration, "get_config_path", return_value="tests/__fixtures__/config")

    environment_config = config.get_project_config()

    assert environment_config == {
        "domain": "website.com",
        "variables": {
            "ope": {"VARIABLE_OPE_1": "ope_1", "VARIABLE_OPE_2": "ope_2"},
            "app": {"VARIABLE_APP_1": "app_1", "VARIABLE_APP_2": "app_2"},
        },
    }


@pytest.mark.usefixtures("config")
def test_get_project_config_when_not_found(mocker):
    mocker.patch.object(io, "exists", return_value=False)

    with pytest.raises(FileNotFoundError):
        config.get_project_config()
