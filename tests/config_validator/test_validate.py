# pylint: disable=missing-function-docstring,missing-module-docstring

import os
from pathlib import Path

from jsonschema import ValidationError  # type: ignore
import pytest

from tests.__fixtures__.example_schema import EXAMPLE_SCHEMA  # type: ignore
from validator.config.config import Configuration
from validator.errors.errors import InvalidTargetPathError
import validator.validate as config_validator


def test_is_yaml_file():
    assert not config_validator.is_yaml_file("invalid_name")
    assert config_validator.is_yaml_file("filename.yaml")
    assert config_validator.is_yaml_file("filename.yml")


def test_build_apps_path_with_env(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_PATH", "/some/target/path")
    app_path = config_validator.build_apps_path()
    assert app_path == "/some/target/path/apps"


def test_build_apps_path_not_set(mocker):
    mocker.patch.object(Configuration, "get_target_path", return_value=None)
    with pytest.raises(InvalidTargetPathError):
        config_validator.build_apps_path()


def test_build_project_conf_path_with_env(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_PATH", "/some/target/path")
    project_conf_path = config_validator.build_project_conf_path()
    assert project_conf_path == "/some/target/path/project.yaml"


def test_build_project_conf_path_not_set(mocker):
    mocker.patch.object(Configuration, "get_target_path", return_value=None)
    with pytest.raises(InvalidTargetPathError):
        config_validator.build_project_conf_path()


def test_validate_valid_file():
    yaml_fixture_path = Path(
        os.path.dirname(__file__), "..", "__fixtures__", "example_valid_config.yaml"
    ).resolve()

    # Validate an exception is not raised on valid schemas
    try:
        result = config_validator.validate_file(yaml_fixture_path, EXAMPLE_SCHEMA)
        assert result is None
    except ValidationError as error:
        pytest.fail(f"It should have not raised an exception on a valid file ${error}")


def test_validate_invalid_file():
    yaml_fixture_path = Path(
        os.path.dirname(__file__), "..", "__fixtures__", "example_invalid_config.yaml"
    ).resolve()

    with pytest.raises(Exception):
        config_validator.validate_file(yaml_fixture_path, EXAMPLE_SCHEMA)


def test_validate_error_apps_dir_not_exists(mocker):
    mocker.patch.object(config_validator, "build_apps_path", return_value="some/target/path")
    expected_message = "some/target/path does not look like a valid configuration path. Verify the path exists"  # pylint: disable=line-too-long
    with pytest.raises(Exception, match=expected_message):
        config_validator.validate_deployment_files()


def test_validate_error_validation_target(mocker):
    fixtures_path = Path(os.path.dirname(__file__), "..", "__fixtures__").resolve()
    mocker.patch.object(config_validator, "build_apps_path", return_value=fixtures_path)
    mocker.patch.object(Configuration, "get_validation_target", return_value="SOME_VALUE")
    with pytest.raises(
        Exception,  # pylint: disable=bad-continuation
        match="There is no configuration to be validated. Be sure to define a valid NESTOR_VALIDATION_TARGET",  # pylint: disable=bad-continuation,line-too-long
    ):
        config_validator.validate_deployment_files()


def test_validate_applications(mocker):
    real_config_fixture_path = Path(
        os.path.dirname(__file__), "..", "__fixtures__", "validator", "apps"
    ).resolve()
    mocker.patch.object(config_validator, "build_apps_path", return_value=real_config_fixture_path)
    mocker.patch.object(Configuration, "get_validation_target", return_value="APPLICATIONS")
    try:
        config_validator.validate_deployment_files()
    except Exception as err:  # pylint: disable=broad-except
        pytest.fail(f"validate_deployment_files() raised an unexpected Exception {err}")


def test_validate_projects(mocker):
    real_config_fixture_path = Path(
        os.path.dirname(__file__), "..", "__fixtures__", "validator", "projects", "project.yaml"
    ).resolve()
    mocker.patch.object(config_validator, "build_apps_path", return_value=real_config_fixture_path)
    mocker.patch.object(
        config_validator, "build_project_conf_path", return_value=real_config_fixture_path
    )
    mocker.patch.object(Configuration, "get_validation_target", return_value="PROJECTS")
    try:
        config_validator.validate_deployment_files()
    except Exception as err:  # pylint: disable=broad-except
        pytest.fail(f"validate_deployment_files() raised an unexpected Exception {err}")
