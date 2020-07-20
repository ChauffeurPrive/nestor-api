from unittest import TestCase
from unittest.mock import patch


class TestApi(TestCase):
    @patch("nestor_api.api.flask_app.create_app", autospec=True)
    def test_api_instance(self, create_app_mock):
        import nestor_api.api.wsgi  # pylint: disable=import-outside-toplevel,unused-import

        create_app_mock.assert_called()
