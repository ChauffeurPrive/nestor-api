# pylint: disable=missing-class-docstring disable=missing-function-docstring disable=missing-module-docstring

from unittest import TestCase
from unittest.mock import call, patch

import nestor_api.lib.workflow as workflow


class TestWorkflow(TestCase):
    @patch("nestor_api.lib.workflow.git")
    def test_compare_unequal_step_hashes(self, git_mock):
        """Should return False when step hashes are unequal."""
        git_mock.get_last_commit_hash.side_effect = ["hash-1", "hash-2"]
        result = workflow.compare_step_hashes("path_to/app_dir", "step-1", "step-2")
        self.assertEqual(git_mock.branch.call_count, 2)
        self.assertEqual(git_mock.get_last_commit_hash.call_count, 2)
        git_mock.branch.assert_has_calls(
            [call("path_to/app_dir", "step-1"), call("path_to/app_dir", "step-2")]
        )
        git_mock.get_last_commit_hash.assert_has_calls(
            [call("path_to/app_dir"), call("path_to/app_dir")]
        )
        self.assertFalse(result)

    @patch("nestor_api.lib.workflow.git")
    def test_compare_equal_step_hashes(self, git_mock):
        """Should return True when step hashes are equal."""
        git_mock.get_last_commit_hash.side_effect = ["hash-1", "hash-1"]
        result = workflow.compare_step_hashes("path_to/app_dir", "step-1", "step-2")
        self.assertEqual(git_mock.branch.call_count, 2)
        self.assertEqual(git_mock.get_last_commit_hash.call_count, 2)
        git_mock.branch.assert_has_calls(
            [call("path_to/app_dir", "step-1"), call("path_to/app_dir", "step-2")]
        )
        git_mock.get_last_commit_hash.assert_has_calls(
            [call("path_to/app_dir"), call("path_to/app_dir")]
        )
        self.assertTrue(result)

    @patch("nestor_api.lib.workflow.compare_step_hashes")
    def test_is_app_ready_to_progress(self, compare_step_hashes_mock):
        """Should forward to compare_step_hashes."""
        compare_step_hashes_mock.return_value = True
        result = workflow.is_app_ready_to_progress("path_to/app_dir", "step-1", "step-2")
        compare_step_hashes_mock.assert_called_once_with("path_to/app_dir", "step-1", "step-2")
        self.assertTrue(result)

    @patch("nestor_api.lib.workflow.is_app_ready_to_progress")
    @patch("nestor_api.lib.workflow.git", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    def test_get_ready_to_progress_apps(self, config_mock, git_mock, is_app_ready_to_progress_mock):
        """Should return a dict with app name as key and
        boolean for ability to progress as value."""

        # Mocks
        config_mock.create_temporary_config_copy.return_value = "config-path"
        config_mock.get_previous_step.return_value = "step-1"
        config_mock.get_project_config.return_value = {"some": "config"}
        config_mock.list_apps_config.return_value = {
            "app1": {"name": "app1", "git": {"origin": "fake-remote-url-1"}},
            "app2": {"name": "app2", "git": {"origin": "fake-remote-url-2"}},
            "app3": {"name": "app2", "git": {"origin": "fake-remote-url-3"}},
        }
        git_mock.create_working_repository.return_value = "path_to/app_dir"
        is_app_ready_to_progress_mock.return_value = True

        result = workflow.get_ready_to_progress_apps("step-2")

        # Assertions
        config_mock.change_environment.assert_called_once_with("step-2", "config-path")
        config_mock.get_project_config.assert_called_once()
        config_mock.get_previous_step.assert_called_once_with({"some": "config"}, "step-2")
        git_mock.create_working_repository.assert_has_calls(
            [call("app1"), call("app2"), call("app3"),]
        )
        is_app_ready_to_progress_mock.assert_has_calls(
            [
                call("path_to/app_dir", "step-1", "step-2"),
                call("path_to/app_dir", "step-1", "step-2"),
                call("path_to/app_dir", "step-1", "step-2"),
            ]
        )
        self.assertEqual(result, {"app1": True, "app2": True, "app3": True})
