from unittest import TestCase
from unittest.mock import ANY, patch

from nestor_api.utils.error_handling import non_blocking_clean


@patch("nestor_api.utils.error_handling.Logger", autospec=True)
@patch("nestor_api.utils.error_handling.io", autospec=True)
class TestWorkflow(TestCase):
    def test_non_blocking_clean(self, io_mock, _logger_mock):
        """Should clean the folder/file provided."""
        non_blocking_clean("some/path")
        io_mock.remove.assert_called_with("some/path")

    def test_non_blocking_clean_with_error(self, io_mock, _logger_mock):
        """Should not raise an error."""
        io_mock.remove.side_effect = Exception("some error during removal")
        try:
            non_blocking_clean("some/path")
        # pylint: disable=broad-except
        except Exception:
            self.fail("_non_blocking_clean should not raise an error when cleaning fails")

    def test_non_blocking_clean_with_error_and_message_prefix(self, io_mock, logger_mock):
        """Should append message prefix to log."""
        io_mock.remove.side_effect = Exception("some error during removal")

        non_blocking_clean("some/path", message_prefix="[prefix]")

        logger_mock.warn.assert_called_with(
            ANY, "[prefix] Error trying to clean temporary directory / file"
        )
