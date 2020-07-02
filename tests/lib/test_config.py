# pylint: disable=missing-function-docstring disable=missing-module-docstring

from unittest.mock import call

import pytest

from nestor_api.config.config import Configuration
from nestor_api.errors.config.aggregated_configuration_error import AggregatedConfigurationError
from nestor_api.errors.config.app_configuration_not_found_error import AppConfigurationNotFoundError
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


def test_resolve_variables_deep():
    # pylint: disable=protected-access
    result = config._resolve_variables_deep(
        {
            "A": "value_a",
            "B": "value_b",
            "C": {
                "C1": "__{{A}}__",
                "C2": "__{{key_not_present}}__",
                "C3": "__{{A}}__{{B}}__{{key_not_present}}__",
                "C4": "A",
                "C5": "{{C1}}__{{key-with.special_characters}}",
            },
            "D": [
                "value_d1",
                "__{{A}}__",
                "__{{key_not_present}}__",
                "__{{A}}__{{B}}__{{key_not_present}}__",
            ],
            "E": [{"E1": {"E11": "deep__{{A}}__"}}],
            "F": 42,
            "key-with.special_characters": "amazing-value",
        }
    )

    assert result == {
        "A": "value_a",
        "B": "value_b",
        "C": {
            "C1": "__value_a__",
            "C2": "__{{key_not_present}}__",
            "C3": "__value_a__value_b__{{key_not_present}}__",
            "C4": "A",
            "C5": "{{C1}}__amazing-value",
        },
        "D": [
            "value_d1",
            "__value_a__",
            "__{{key_not_present}}__",
            "__value_a__value_b__{{key_not_present}}__",
        ],
        "E": [{"E1": {"E11": "deep__value_a__"}}],
        "F": 42,
        "key-with.special_characters": "amazing-value",
    }


def test_resolve_variables_deep_with_invalid_reference():
    with pytest.raises(AggregatedConfigurationError) as err:
        # pylint: disable=protected-access
        config._resolve_variables_deep(
            {
                "error": {},
                "simple_key": "__{{error}}__",
                "array": ["0", "1", "2__{{error}}__",],
                "dict": {"a": "val_a", "b": "{{error}}",},
                "deep_dict": {
                    "sub_dict": {"a": "val_a", "b": "{{error}}"},
                    "sub_array": [
                        {"a": "{{error}}", "b": "val_b"},
                        {"a": "val_a", "b": "{{error}}"},
                    ],
                },
            }
        )

    assert str(err.value) == "Invalid configuration"

    assert err.value.errors[0].path == "CONFIG.simple_key"
    assert err.value.errors[0].message == "Referenced variable should resolved to a string"

    assert err.value.errors[1].path == "CONFIG.array[2]"
    assert err.value.errors[1].message == "Referenced variable should resolved to a string"

    assert err.value.errors[2].path == "CONFIG.dict.b"
    assert err.value.errors[2].message == "Referenced variable should resolved to a string"

    assert err.value.errors[3].path == "CONFIG.deep_dict.sub_dict.b"
    assert err.value.errors[3].message == "Referenced variable should resolved to a string"

    assert err.value.errors[4].path == "CONFIG.deep_dict.sub_array[0].a"
    assert err.value.errors[4].message == "Referenced variable should resolved to a string"

    assert err.value.errors[5].path == "CONFIG.deep_dict.sub_array[1].b"
    assert err.value.errors[5].message == "Referenced variable should resolved to a string"
