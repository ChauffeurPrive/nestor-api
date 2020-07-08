# pylint: disable=missing-class-docstring disable=missing-function-docstring disable=missing-module-docstring

from unittest import TestCase

import nestor_api.lib.app as app


class TestAppLib(TestCase):
    def test_get_version(self):
        version = app.get_version()
        self.assertEqual(version, "0.0.0")
