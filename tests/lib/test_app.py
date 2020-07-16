from unittest import TestCase

import nestor_api.lib.app as app


class TestAppLib(TestCase):
    def test_get_version(self):
        version = app.get_version("/some/app/path")
        self.assertEqual(version, "0.0.0")
