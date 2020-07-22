"""Unit test for logger class"""

from unittest import TestCase
from unittest.mock import patch

from nestor_api.utils.logger import Logger


class TestLogger(TestCase):
    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_debug(self, logging_mock):
        Logger.debug({"user_id": 1234}, "Found user")
        logging_mock.debug.assert_called_once_with("%s %s", "Found user", '{"user_id": 1234}')

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_debug_with_no_context(self, logging_mock):
        Logger.debug(message="Found user")
        logging_mock.debug.assert_called_once_with("Found user")

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_info(self, logging_mock):
        Logger.info({"user_id": 1234}, "Found user")
        logging_mock.info.assert_called_once_with("%s %s", "Found user", '{"user_id": 1234}')

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_info_with_no_context(self, logging_mock):
        Logger.info(message="Found user")
        logging_mock.info.assert_called_once_with("Found user")

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_warn(self, logging_mock):
        Logger.warn({"user_id": 1234}, "Found user")
        logging_mock.warning.assert_called_once_with("%s %s", "Found user", '{"user_id": 1234}')

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_warn_with_no_context(self, logging_mock):
        Logger.warn(message="Found user")
        logging_mock.warning.assert_called_once_with("Found user")

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_error(self, logging_mock):
        Logger.error({"user_id": 1234}, "Found user")
        logging_mock.error.assert_called_once_with(
            "%s %s", "Found user", '{"user_id": 1234}', exc_info=True
        )

    @patch("nestor_api.utils.logger.logging", autospec=True)
    def test_logger_error_with_no_context(self, logging_mock):
        Logger.error(message="Found user")
        logging_mock.error.assert_called_once_with("Found user", exc_info=True)
