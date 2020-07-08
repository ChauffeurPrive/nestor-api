# pylint: disable=missing-function-docstring disable=missing-module-docstring

import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.config import Configuration


class TestConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_CONFIG_PATH": "/a-custom-config-path"})
    def test_get_config_path(self):
        self.assertEqual(Configuration.get_config_path(), "/a-custom-config-path")

    @patch.dict(os.environ, {"NESTOR_PRISTINE_PATH": "/a-custom-pristine-path"})
    def test_get_pristine_path_configured(self):
        self.assertEqual(Configuration.get_pristine_path(), "/a-custom-pristine-path")

    def test_get_pristine_path_default(self):
        self.assertEqual(Configuration.get_pristine_path(), "/tmp/nestor/pristine")

    @patch.dict(os.environ, {"NESTOR_WORK_PATH": "/a-custom-working-path"})
    def test_get_working_path_configured(self):
        self.assertEqual(Configuration.get_working_path(), "/a-custom-working-path")

    def test_get_working_path_default(self):
        self.assertEqual(Configuration.get_working_path(), "/tmp/nestor/work")

    @patch.dict(os.environ, {"NESTOR_CONFIG_APPS_FOLDER": "/a-custom-apps-folder"})
    def test_get_config_app_folder_configured(self):
        self.assertEqual(Configuration.get_config_app_folder(), "/a-custom-apps-folder")

    def test_get_config_app_folder_default(self):
        self.assertEqual(Configuration.get_config_app_folder(), "apps")

    @patch.dict(os.environ, {"NESTOR_CONFIG_PROJECT_FILENAME": "custom-name.yaml"})
    def test_get_config_project_filename_configured(self):
        self.assertEqual(Configuration.get_config_project_filename(), "custom-name.yaml")

    def test_get_config_project_filename_default(self):
        self.assertEqual(Configuration.get_config_project_filename(), "project.yaml")
