from unittest import TestCase
from unittest.mock import call, patch

from nestor_api.lib.workflow.advance import advance_workflow, get_app_progress_report, get_next_step
from nestor_api.lib.workflow.errors import (
    AppListingError,
    StepNotExistingInWorkflowError,
    WorkflowError,
)
from nestor_api.lib.workflow.typings import WorkflowAdvanceStatus


class TestWorkflow(TestCase):
    @patch("nestor_api.lib.workflow.advance.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.advance.git", autospec=True)
    @patch("nestor_api.lib.workflow.advance.config", autospec=True)
    @patch("nestor_api.lib.workflow.advance.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_app_progress_report", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_next_step", autospec=True)
    def test_advance_workflow(
        self,
        get_next_step_mock,
        get_app_progress_report_mock,
        non_blocking_clean_mock,
        config_mock,
        git_mock,
        _logger_mock,
    ):
        """Should properly advance workflow for all apps."""
        # Mocks
        get_next_step_mock.return_value = "step-2"
        fake_config_app_1 = {"git": {"origin": "fake-git-origin-for-app-1"}}
        fake_config_app_2 = {"git": {"origin": "fake-git-origin-for-app-2"}}
        config_mock.list_apps_config.return_value.items.return_value = [
            ("app-1", fake_config_app_1),
            ("app-2", fake_config_app_2),
        ]
        git_mock.create_working_repository.side_effect = ["app-1-dir", "app-2-dir"]
        get_app_progress_report_mock.side_effect = [
            (True, "0.0.0-sha-cf021d1"),
            (False, "0.0.0-sha-78fe3d7"),
        ]
        config_mock.get_processes.return_value = []
        config_mock.get_cronjobs.return_value = []
        fake_project_config = {}

        # Test
        result = advance_workflow("path/to/config", fake_project_config, "step-1")

        # Assertions
        get_next_step_mock.assert_called_with(fake_project_config, "step-1")
        config_mock.list_apps_config.assert_called_once_with("path/to/config")
        config_mock.list_apps_config.return_value.items.assert_called_once()
        git_mock.create_working_repository.assert_has_calls(
            [call("app-1", "fake-git-origin-for-app-1"), call("app-2", "fake-git-origin-for-app-2")]
        )
        get_app_progress_report_mock.assert_has_calls(
            [call("app-1-dir", "step-1", "step-2"), call("app-2-dir", "step-1", "step-2")]
        )
        git_mock.branch.assert_called_once_with("app-1-dir", "step-2")
        git_mock.rebase.assert_called_once_with("app-1-dir", "step-1", onto="0.0.0-sha-cf021d1")
        git_mock.push.assert_called_once_with("app-1-dir")
        config_mock.get_processes.assert_called_once_with(fake_config_app_1)
        config_mock.get_cronjobs.assert_called_once_with(fake_config_app_1)
        non_blocking_clean_mock.assert_has_calls([call("app-1-dir"), call("app-2-dir")])
        self.assertEqual(
            result,
            (
                WorkflowAdvanceStatus.SUCCESS,
                [
                    {
                        "name": "app-1",
                        "tag": "0.0.0-sha-cf021d1",
                        "step": "step-2",
                        "processes": [],
                        "cron_jobs": [],
                    }
                ],
            ),
        )

    @patch("nestor_api.lib.workflow.advance.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.advance.git", autospec=True)
    @patch("nestor_api.lib.workflow.advance.config", autospec=True)
    @patch("nestor_api.lib.workflow.advance.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_app_progress_report", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_next_step", autospec=True)
    def test_advance_workflow_with_app_failing(
        self,
        get_next_step_mock,
        get_app_progress_report_mock,
        non_blocking_clean_mock,
        config_mock,
        git_mock,
        _logger_mock,
    ):
        """Should return fail status if one of the app failed to advance workflow."""
        # Mocks
        get_next_step_mock.return_value = "step-2"
        config_mock.list_apps_config.return_value.items.return_value = [
            ("app-1", {"git": {"origin": "fake-git-origin-for-app-1"}}),
            ("app-2", {"git": {"origin": "fake-git-origin-for-app-2"}}),
        ]
        git_mock.create_working_repository.side_effect = [Exception("fake error"), "app-2-dir"]
        get_app_progress_report_mock.return_value = (True, "0.0.0-sha-cf021d1")
        config_mock.get_processes.return_value = []
        config_mock.get_cronjobs.return_value = []

        # Test
        result = advance_workflow("path/to/config", {}, "step-1")

        # Assertions
        git_mock.create_working_repository.assert_has_calls(
            [call("app-1", "fake-git-origin-for-app-1"), call("app-2", "fake-git-origin-for-app-2")]
        )
        non_blocking_clean_mock.assert_called_once_with("app-2-dir")
        self.assertEqual(
            result,
            (
                WorkflowAdvanceStatus.FAIL,
                [
                    {
                        "name": "app-2",
                        "tag": "0.0.0-sha-cf021d1",
                        "step": "step-2",
                        "processes": [],
                        "cron_jobs": [],
                    }
                ],
            ),
        )

    @patch("nestor_api.lib.workflow.advance.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_next_step", autospec=True)
    @patch("nestor_api.lib.workflow.advance.config", autospec=True)
    def test_advance_workflow_with_application_listing_failing(
        self, config_mock, _get_next_step_mock, _logger_mock,
    ):
        """Should raise an AppListingError if something fails when listing apps."""
        # Mocks
        config_mock.list_apps_config.side_effect = Exception("fake error")

        # Test
        with self.assertRaises(AppListingError):
            advance_workflow("path/to/config", {}, "step-1")

    @patch("nestor_api.lib.workflow.advance.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.advance.get_next_step", autospec=True)
    def test_advance_workflow_with_next_step_not_found(
        self, get_next_step_mock, _logger_mock,
    ):
        """Should raise a WorkflowError if there is no next step."""
        # Mocks
        get_next_step_mock.return_value = None

        # Test
        with self.assertRaisesRegex(WorkflowError, "Workflow is already in final step."):
            advance_workflow("path/to/config", {}, "step-1")

    @patch("nestor_api.lib.workflow.advance.git")
    def test_get_app_progress_report_with_app_ready_to_progress(self, git_mock):
        """Should generate a report indicating that the app is ready to progress."""
        # Mocks
        git_mock.get_last_tag.return_value = "0.0.0-sha-cf021d1"
        git_mock.get_commit_hash_from_tag.return_value = "cf021d1"
        git_mock.get_last_commit_hash.return_value = "78fe3d7"
        git_mock.is_branch_existing.return_value = True

        # Test
        result = get_app_progress_report("path_to/app_dir", "step-1", "step-2")

        # Assertions
        git_mock.branch.assert_called_with("path_to/app_dir", "step-1")
        git_mock.get_last_tag.assert_called_with("path_to/app_dir")
        git_mock.is_branch_existing.assert_called_with("path_to/app_dir", "step-2")
        git_mock.get_commit_hash_from_tag.assert_called_with("path_to/app_dir", "0.0.0-sha-cf021d1")
        git_mock.get_last_commit_hash.assert_called_with("path_to/app_dir", "step-2")

        self.assertEqual(result, (True, "0.0.0-sha-cf021d1"))

    @patch("nestor_api.lib.workflow.advance.git")
    def test_get_app_progress_report_with_app_up_to_date(self, git_mock):
        """Should generate a report indicating that the app is up-to-date."""
        # Mocks
        git_mock.get_last_tag.return_value = "0.0.0-sha-cf021d1"
        git_mock.get_commit_hash_from_tag.return_value = "cf021d1"
        git_mock.get_last_commit_hash.return_value = "cf021d1"
        git_mock.is_branch_existing.return_value = True

        # Test
        result = get_app_progress_report("path_to/app_dir", "step-1", "step-2")

        # Assertions
        git_mock.branch.assert_called_with("path_to/app_dir", "step-1")
        git_mock.get_last_tag.assert_called_with("path_to/app_dir")
        git_mock.is_branch_existing.assert_called_with("path_to/app_dir", "step-2")
        git_mock.get_commit_hash_from_tag.assert_called_with("path_to/app_dir", "0.0.0-sha-cf021d1")
        git_mock.get_last_commit_hash.assert_called_with("path_to/app_dir", "step-2")
        self.assertEqual(result, (False, "0.0.0-sha-cf021d1"))

    @patch("nestor_api.lib.workflow.advance.git")
    def test_get_app_progress_report_with_non_existing_next_step_branch(self, git_mock):
        """Should generate a report indicating that the app is ready to progress."""
        # Mocks
        git_mock.get_last_tag.return_value = "0.0.0-sha-cf021d1"
        git_mock.is_branch_existing.return_value = False

        # Test
        result = get_app_progress_report("path_to/app_dir", "step-1", "step-2")

        # Assertions
        git_mock.branch.assert_called_with("path_to/app_dir", "step-1")
        git_mock.get_last_tag.assert_called_with("path_to/app_dir")
        git_mock.is_branch_existing.assert_called_with("path_to/app_dir", "step-2")
        git_mock.get_commit_hash_from_tag.assert_not_called()
        git_mock.get_last_commit_hash.assert_not_called()
        self.assertEqual(result, (True, "0.0.0-sha-cf021d1"))

    def test_get_next_step_with_existing_next_step(self):
        """Should return the next step."""
        next_step = get_next_step({"workflow": ["step1", "step2", "step3"]}, "step2")
        self.assertEqual(next_step, "step3")

    def test_get_next_step_without_next_step(self):
        """Should return None as the next step does not exist."""
        next_step = get_next_step({"workflow": ["step1", "step2", "step3"]}, "step3")
        self.assertIsNone(next_step)

    def test_get_next_step_raises_error_with_incorrect_config(self):
        """Should raise an error if config is malformed."""
        with self.assertRaises(StepNotExistingInWorkflowError):
            get_next_step({}, "step1")
