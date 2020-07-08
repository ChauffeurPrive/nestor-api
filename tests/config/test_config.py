# pylint: disable=missing-function-docstring disable=missing-module-docstring

from nestor_api.config.config import Configuration


def test_get_config_path(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_PATH", "/a-custom-config-path")
    assert Configuration.get_config_path() == "/a-custom-config-path"


def test_get_pristine_path_configured(monkeypatch):
    monkeypatch.setenv("NESTOR_PRISTINE_PATH", "/a-custom-pristine-path")

    assert Configuration.get_pristine_path() == "/a-custom-pristine-path"


def test_get_pristine_path_default():
    assert Configuration.get_pristine_path() == "/tmp/nestor/pristine"


def test_get_working_path_configured(monkeypatch):
    monkeypatch.setenv("NESTOR_WORK_PATH", "/a-custom-working-path")

    assert Configuration.get_working_path() == "/a-custom-working-path"


def test_get_working_path_default():
    assert Configuration.get_working_path() == "/tmp/nestor/work"


def test_get_config_app_folder_configured(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_APPS_FOLDER", "/a-custom-apps-folder")

    assert Configuration.get_config_app_folder() == "/a-custom-apps-folder"


def test_get_config_app_folder_default():
    assert Configuration.get_config_app_folder() == "apps"


def test_get_config_project_filename_configured(monkeypatch):
    monkeypatch.setenv("NESTOR_CONFIG_PROJECT_FILENAME", "custom-name.yaml")

    assert Configuration.get_config_project_filename() == "custom-name.yaml"


def test_get_config_project_filename_default():
    assert Configuration.get_config_project_filename() == "project.yaml"
