from unittest import TestCase
from unittest.mock import MagicMock, call, create_autospec, patch

from github import AuthenticatedUser, Branch

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider, GitProviderError
import nestor_api.lib.workflow as workflow


class TestWorkflow(TestCase):
    @patch("nestor_api.lib.workflow.git")
    def test_are_step_hashes_equal_with_unequal_values(self, git_mock):
        """Should return False when step hashes are unequal."""
        # Mocks
        git_mock.get_last_commit_hash.side_effect = ["hash-1", "hash-2"]

        # Test
        result = workflow.are_step_hashes_equal("path_to/app_dir", "step-1", "step-2")

        # Assertions
        self.assertEqual(git_mock.get_last_commit_hash.call_count, 2)
        git_mock.get_last_commit_hash.assert_has_calls(
            [call("path_to/app_dir", "step-1"), call("path_to/app_dir", "step-2")]
        )
        self.assertFalse(result)

    @patch("nestor_api.lib.workflow.git")
    def test_are_step_hashes_equal_with_equal_values(self, git_mock):
        """Should return True when step hashes are equal."""
        # Mocks
        git_mock.get_last_commit_hash.side_effect = ["hash-1", "hash-1"]

        # Test
        result = workflow.are_step_hashes_equal("path_to/app_dir", "step-1", "step-2")

        # Assertions
        self.assertEqual(git_mock.get_last_commit_hash.call_count, 2)
        git_mock.get_last_commit_hash.assert_has_calls(
            [call("path_to/app_dir", "step-1"), call("path_to/app_dir", "step-2")]
        )
        self.assertTrue(result)

    @patch("nestor_api.lib.workflow.are_step_hashes_equal")
    def test_should_app_progress(self, are_step_hashes_equal_mock):
        """Should forward to compare_step_hashes."""
        are_step_hashes_equal_mock.return_value = True
        result = workflow.should_app_progress("path_to/app_dir", "step-1", "step-2")
        are_step_hashes_equal_mock.assert_called_once_with("path_to/app_dir", "step-1", "step-2")
        self.assertTrue(result)

    @patch("nestor_api.lib.workflow.are_step_hashes_equal")
    def test_should_app_progress_without_current_step(self, are_step_hashes_equal_mock):
        """Should return true without forwarding to compare_step_hashes."""
        are_step_hashes_equal_mock.return_value = True
        result = workflow.should_app_progress("path_to/app_dir", None, "step-2")
        are_step_hashes_equal_mock.assert_not_called()
        self.assertTrue(result)

    @patch("nestor_api.lib.workflow.get_previous_step")
    @patch("nestor_api.lib.workflow.should_app_progress")
    @patch("nestor_api.lib.workflow.git", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    @patch("nestor_api.lib.workflow.io", autospec=True)
    def test_get_apps_to_move_forward(
        self, io_mock, config_mock, git_mock, should_app_progress_mock, get_previous_step_mock
    ):
        """Should return a dict with app name as key and
        boolean for ability to progress as value."""

        # Mocks
        config_mock.create_temporary_config_copy.return_value = "config-path"
        get_previous_step_mock.return_value = "step-1"
        config_mock.get_project_config.return_value = {"some": "config"}
        config_mock.list_apps_config.return_value = {
            "app1": {"name": "app1", "git": {"origin": "fake-remote-url-1"}},
            "app2": {"name": "app2", "git": {"origin": "fake-remote-url-2"}},
            "app3": {"name": "app2", "git": {"origin": "fake-remote-url-3"}},
        }
        git_mock.create_working_repository.return_value = "path_to/app_dir"
        should_app_progress_mock.side_effect = [True, True, False]

        # Test
        result = workflow.get_apps_to_move_forward("step-2")

        # Assertions
        config_mock.change_environment.assert_called_once_with("step-2", "config-path")
        config_mock.get_project_config.assert_called_once()
        get_previous_step_mock.assert_called_once_with({"some": "config"}, "step-2")
        git_mock.create_working_repository.assert_has_calls(
            [
                call("app1", "fake-remote-url-1"),
                call("app2", "fake-remote-url-2"),
                call("app3", "fake-remote-url-3"),
            ]
        )
        should_app_progress_mock.assert_has_calls(
            [
                call("path_to/app_dir", "step-1", "step-2"),
                call("path_to/app_dir", "step-1", "step-2"),
                call("path_to/app_dir", "step-1", "step-2"),
            ]
        )
        self.assertEqual(io_mock.remove.call_count, 3)
        self.assertEqual(result, {"app1": True, "app2": True, "app3": False})

    def test_get_previous_step_with_previous_step(self):
        """Should answer with the previous step."""
        previous_step = workflow.get_previous_step(
            {"workflow": ["step1", "step2", "step3"]}, "step2"
        )
        self.assertEqual(previous_step, "step1")

    def test_get_previous_step_without_previous_step(self):
        """Should answer with None as the previous step does not exist."""
        previous_step = workflow.get_previous_step(
            {"workflow": ["step1", "step2", "step3"]}, "step1"
        )
        self.assertIsNone(previous_step)

    def test_get_previous_step_raises_error_with_incorrect_config(self):
        """Should raise an error if config is malformed."""
        with self.assertRaises(KeyError):
            workflow.get_previous_step({}, "step1")

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    @patch("nestor_api.lib.workflow._create_and_protect_branch", autospec=True)
    def test_init_workflow(self, _create_and_protect_branch_mock, config_mock, _logger_mock):
        """Should correctly initialize all branches."""
        # Mocks
        config_mock.get_app_config.return_value = {
            "workflow": ["integration", "staging", "production"]
        }
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        user.login = "some-user-login"
        git_provider_mock.get_user_info.return_value = user
        master_branch = MagicMock(spec=Branch.Branch)
        master_branch.commit.sha = "5ac5ee8"
        git_provider_mock.get_branch.return_value = master_branch
        _create_and_protect_branch_mock.side_effect = [
            {"created": (True, True), "protected": (True, True)},
            {"created": (False, True), "protected": (True, True)},
            {"created": (False, True), "protected": (False, True)},
        ]

        # Test
        result = workflow.init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_branch.assert_called_with("organization", "app-1", "master")
        self.assertEqual(
            result,
            (
                workflow.WorkflowInitStatus.SUCCESS,
                {
                    "integration": {"created": (True, True), "protected": (True, True)},
                    "staging": {"created": (False, True), "protected": (True, True)},
                    "production": {"created": (False, True), "protected": (False, True)},
                },
            ),
        )

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    @patch("nestor_api.lib.workflow._create_and_protect_branch", autospec=True)
    def test_init_workflow_without_master_branch_commit(
        self, _create_and_protect_branch_mock, config_mock, _logger_mock
    ):
        """Should fail if master does not have any commit."""
        # Mocks
        config_mock.get_app_config.return_value = {
            "workflow": ["integration", "staging", "production"]
        }
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        user.login = "some-user-login"
        git_provider_mock.get_user_info.return_value = user
        master_branch = MagicMock(spec=Branch.Branch)
        master_branch.commit = None
        git_provider_mock.get_branch.return_value = master_branch

        # Test
        with self.assertRaisesRegex(Exception, "Repository looks empty"):
            workflow.init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        _create_and_protect_branch_mock.assert_not_called()

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    @patch("nestor_api.lib.workflow._create_and_protect_branch", autospec=True)
    def test_init_workflow_failing_to_create_or_protect_branch(
        self, _create_and_protect_branch_mock, config_mock, _logger_mock
    ):
        """Should return failed report if something goes wrong when
        creating/protecting branches."""
        # Mocks
        config_mock.get_app_config.return_value = {
            "workflow": ["integration", "staging", "production"]
        }
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        user.login = "some-user-login"
        git_provider_mock.get_user_info.return_value = user
        master_branch = MagicMock(spec=Branch.Branch)
        master_branch.commit.sha = "5ac5ee8"
        git_provider_mock.get_branch.return_value = master_branch
        _create_and_protect_branch_mock.side_effect = GitProviderError("error")

        # Test
        result = workflow.init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_branch.assert_called_with("organization", "app-1", "master")
        self.assertEqual(
            result, (workflow.WorkflowInitStatus.FAIL, {},),
        )

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.config", autospec=True)
    def test_init_workflow_without_configured_workflow(self, config_mock, _logger_mock):
        """Should create no branches."""
        # Mocks
        config_mock.get_app_config.return_value = {}
        git_provider_mock = create_autospec(spec=AbstractGitProvider)

        # Test
        result = workflow.init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_user_info.assert_not_called()
        git_provider_mock.get_branch.assert_not_called()
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_not_called()
        self.assertEqual(result, (workflow.WorkflowInitStatus.SUCCESS, {}))

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    def test_create_and_protect_branch_with_unexisting_branch(self, _logger_mock):
        """Should create and protect branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        git_provider_mock.get_branch.return_value = None
        branch = MagicMock(spec=Branch.Branch)
        branch.protected = False
        git_provider_mock.create_branch.return_value = branch

        # Test
        result = workflow._create_and_protect_branch(
            "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
        )

        # Assertions
        git_provider_mock.get_branch.assert_called_once_with("organization", "app-1", "staging")
        git_provider_mock.create_branch.assert_called_once_with(
            "organization", "app-1", "staging", "5ac5ee8"
        )
        git_provider_mock.protect_branch.assert_called_once_with(
            "organization", "app-1", "staging", "some-user-login"
        )
        self.assertEqual(result, {"created": (True, True), "protected": (True, True)})

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    def test_create_and_protect_branch_with_existing_protected_branch(self, _logger_mock):
        """Should not modify branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        staging_branch = MagicMock(spec=Branch.Branch)
        staging_branch.protected = True
        git_provider_mock.get_branch.return_value = staging_branch

        # Test
        result = workflow._create_and_protect_branch(
            "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
        )

        # Assertions
        git_provider_mock.get_branch.assert_called_once_with("organization", "app-1", "staging")
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_not_called()
        self.assertEqual(result, {"created": (False, True), "protected": (False, True)})

    @patch("nestor_api.lib.workflow.Logger", autospec=True)
    def test_create_workflow_with_existing_unprotected_branch(self, _logger_mock):
        """Should only protect the branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        staging_branch = MagicMock(spec=Branch.Branch)
        staging_branch.protected = False
        git_provider_mock.get_branch.return_value = staging_branch

        # Test
        result = workflow._create_and_protect_branch(
            "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
        )

        # Assertions
        git_provider_mock.get_branch.assert_called_once_with("organization", "app-1", "staging")
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_called_once_with(
            "organization", "app-1", "staging", "some-user-login"
        )
        self.assertEqual(result, {"created": (False, True), "protected": (True, True)})
