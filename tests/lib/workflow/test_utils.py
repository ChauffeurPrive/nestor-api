from unittest import TestCase
from unittest.mock import patch

from nestor_api.lib.workflow.utils import non_blocking_clean


class TestWorkflow(TestCase):
    @patch("nestor_api.lib.workflow.utils.io", autospec=True)
    def test_non_blocking_clean(self, io_mock):
        """Should clean the folder/file provided."""
        non_blocking_clean("some/path")
        io_mock.remove.assert_called_with("some/path")

    @patch("nestor_api.lib.workflow.utils.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.utils.io", autospec=True)
    def test_non_blocking_clean_with_error(self, io_mock, _logger_mock):
        """Should not raise an error."""
        io_mock.remove.side_effect = Exception("some error during removal")
        try:
            non_blocking_clean("some/path")
        except Exception as err:
            self.fail("_non_blocking_clean should not raise an error when cleaning fails")
