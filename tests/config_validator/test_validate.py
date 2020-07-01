# pylint: disable=missing-function-docstring disable=missing-module-docstring

import os
from pathlib import Path

from jsonschema import ValidationError
import pytest

from tests.__fixtures__.example_schema import EXAMPLE_SCHEMA
from validator.config.config import Configuration
import validator.validate as config_validator


def test_build_app_path_with_env(monkeypatch):
    monkeypatch.setenv("NESTOR_TARGET_PATH", "/some/target/path")
    app_path = config_validator.build_app_path()
    assert app_path == "/some/target/path/apps"


def test_build_app_path_with_fallback(mocker):
    mocker.patch.object(Configuration, "get_target_path", return_value="/some/target/path")
    app_path = config_validator.build_app_path()
    assert app_path == "/some/target/path/apps"


def test_build_project_conf_path_with_env(monkeypatch):
    monkeypatch.setenv("NESTOR_TARGET_PATH", "/some/target/path")
    project_conf_path = config_validator.build_project_conf_path()
    assert project_conf_path == "/some/target/path/project.yaml"


def test_build_project_conf_path_with_fallback(mocker):
    mocker.patch.object(Configuration, "get_target_path", return_value="/some/target/path")
    app_path = config_validator.build_project_conf_path()
    assert app_path == "/some/target/path/project.yaml"


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
