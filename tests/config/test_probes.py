import os
from unittest import TestCase
from unittest.mock import patch

from nestor_api.config.probes import ProbesDefaultConfiguration


class TestConfig(TestCase):
    @patch.dict(os.environ, {"NESTOR_PROBES_DEFAULT_DELAY": "2"})
    def test_get_default_delay_configured(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_delay(), 2)

    def test_get_default_delay_default(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_delay(), 30)

    @patch.dict(os.environ, {"NESTOR_PROBES_DEFAULT_PERIOD": "2"})
    def test_get_default_period_configured(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_period(), 2)

    def test_get_default_period_default(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_period(), 10)

    @patch.dict(os.environ, {"NESTOR_PROBES_DEFAULT_TIMEOUT": "2"})
    def test_get_default_timeout_configured(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_timeout(), 2)

    def test_get_default_timeout_default(self):
        self.assertEqual(ProbesDefaultConfiguration.get_default_timeout(), 1)
