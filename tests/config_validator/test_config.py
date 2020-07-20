import os
import unittest
from unittest.mock import patch

from validator.config.config import Configuration


class TestConfig(unittest.TestCase):
    @patch.dict(os.environ, {"NESTOR_CONFIG_PATH": "/some/path"})
    def test_config_get_target_path(self):
        self.assertEqual(Configuration.get_target_path(), "/some/path")

    @patch.dict(os.environ, {"NESTOR_VALIDATION_TARGET": "APPLICATIONS"})
    def test_config_get_validation_target(self):
        self.assertEqual(Configuration.get_validation_target(), "APPLICATIONS")
