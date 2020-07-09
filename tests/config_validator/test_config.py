# pylint: disable=missing-function-docstring,missing-module-docstring

from validator.config.config import Configuration


def test_config_get_target_path(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_PATH", "/some/path")
    assert Configuration.get_target_path() == "/some/path"


def test_config_get_validation_target(monkeypatch):
    monkeypatch.setenv("NESTOR_VALIDATION_TARGET", "APPLICATIONS")
    assert Configuration.get_validation_target() == "APPLICATIONS"
