from unittest import TestCase
from unittest.mock import MagicMock, create_autospec, patch

from github import AuthenticatedUser, Branch

from nestor_api.adapters.git.abstract_git_provider import (
    AbstractGitProvider,
    GitProviderError,
    GitResource,
    GitResourceNotFoundError,
)
from nestor_api.lib.workflow.init import (
    _create_and_protect_branch,
    _get_workflow_branches,
    init_workflow,
)
from nestor_api.lib.workflow.typings import WorkflowInitStatus


class TestWorkflow(TestCase):
    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.init.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.init.config", autospec=True)
    @patch("nestor_api.lib.workflow.init._create_and_protect_branch", autospec=True)
    def test_init_workflow(
        self, _create_and_protect_branch_mock, config_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should correctly initialize all branches."""
        # Mocks
        config_mock.create_temporary_config_copy.return_value = "fake-path"
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
        result = init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_branch.assert_called_with("organization", "app-1", "master")
        non_blocking_clean_mock.assert_called_with("fake-path")
        self.assertEqual(
            result,
            (
                WorkflowInitStatus.SUCCESS,
                {
                    "integration": {"created": (True, True), "protected": (True, True)},
                    "staging": {"created": (False, True), "protected": (True, True)},
                    "production": {"created": (False, True), "protected": (False, True)},
                },
            ),
        )

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.init.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.init.config", autospec=True)
    @patch("nestor_api.lib.workflow.init._create_and_protect_branch", autospec=True)
    def test_init_workflow_without_master_branch(
        self, _create_and_protect_branch_mock, config_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should return fail status and empty report."""
        # Mocks
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        config_mock.get_app_config.return_value = {
            "workflow": ["integration", "staging", "production"]
        }
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        user.login = "some-user-login"
        git_provider_mock.get_user_info.return_value = user
        git_provider_mock.get_branch.side_effect = GitResourceNotFoundError(GitResource.BRANCH)

        # Test
        result = init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        _create_and_protect_branch_mock.assert_not_called()
        non_blocking_clean_mock.assert_called_with("fake-path")
        self.assertEqual(
            result, (WorkflowInitStatus.FAIL, {},),
        )

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.init.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.init.config", autospec=True)
    @patch("nestor_api.lib.workflow.init._create_and_protect_branch", autospec=True)
    def test_init_workflow_failing_to_create_or_protect_branch(
        self, _create_and_protect_branch_mock, config_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should return failed report if something goes wrong when
        creating/protecting branches."""
        # Mocks
        config_mock.create_temporary_config_copy.return_value = "fake-path"
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
        result = init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_branch.assert_called_with("organization", "app-1", "master")
        non_blocking_clean_mock.assert_called_with("fake-path")
        self.assertEqual(
            result, (WorkflowInitStatus.FAIL, {},),
        )

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    @patch("nestor_api.lib.workflow.init.non_blocking_clean", autospec=True)
    @patch("nestor_api.lib.workflow.init.config", autospec=True)
    def test_init_workflow_without_configured_workflow(
        self, config_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should create no branch."""
        # Mocks
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        config_mock.get_app_config.return_value = {}
        git_provider_mock = create_autospec(spec=AbstractGitProvider)

        # Test
        result = init_workflow("organization", "app-1", git_provider_mock)

        # Assertions
        git_provider_mock.get_user_info.assert_not_called()
        git_provider_mock.get_branch.assert_not_called()
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_not_called()
        non_blocking_clean_mock.assert_called_with("fake-path")
        self.assertEqual(result, (WorkflowInitStatus.SUCCESS, {}))

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    def test_create_and_protect_branch_with_non_existing_branch(self, _logger_mock):
        """Should create and protect branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        git_provider_mock.get_branch.side_effect = GitResourceNotFoundError(GitResource.BRANCH)
        branch = MagicMock(spec=Branch.Branch)
        branch.protected = False
        git_provider_mock.create_branch.return_value = branch

        # Test
        result = _create_and_protect_branch(
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

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    def test_create_and_protect_branch_with_non_existing_repo(self, _logger_mock):
        """Should raise an error."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        git_provider_mock.get_branch.side_effect = GitResourceNotFoundError(GitResource.REPOSITORY)

        # Test
        with self.assertRaises(GitResourceNotFoundError) as context:
            _create_and_protect_branch(
                "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
            )

        # Assertions
        self.assertEqual(context.exception.resource, GitResource.REPOSITORY)

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    def test_create_and_protect_branch_with_existing_protected_branch(self, _logger_mock):
        """Should not modify branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        staging_branch = MagicMock(spec=Branch.Branch)
        staging_branch.protected = True
        git_provider_mock.get_branch.return_value = staging_branch

        # Test
        result = _create_and_protect_branch(
            "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
        )

        # Assertions
        git_provider_mock.get_branch.assert_called_once_with("organization", "app-1", "staging")
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_not_called()
        self.assertEqual(result, {"created": (False, True), "protected": (False, True)})

    @patch("nestor_api.lib.workflow.init.Logger", autospec=True)
    def test_create_and_protect_branch_with_existing_unprotected_branch(self, _logger_mock):
        """Should only protect the branch."""
        # Mocks
        git_provider_mock = create_autospec(spec=AbstractGitProvider)
        staging_branch = MagicMock(spec=Branch.Branch)
        staging_branch.protected = False
        git_provider_mock.get_branch.return_value = staging_branch

        # Test
        result = _create_and_protect_branch(
            "organization", "app-1", "staging", "5ac5ee8", "some-user-login", git_provider_mock
        )

        # Assertions
        git_provider_mock.get_branch.assert_called_once_with("organization", "app-1", "staging")
        git_provider_mock.create_branch.assert_not_called()
        git_provider_mock.protect_branch.assert_called_once_with(
            "organization", "app-1", "staging", "some-user-login"
        )
        self.assertEqual(result, {"created": (False, True), "protected": (True, True)})

    def test_get_workflow_branches(self):
        """Should return the list of workflow branches."""
        fake_config = {"workflow": ["integration", "staging", "master"]}
        result = _get_workflow_branches(fake_config, "master")

        self.assertEqual(result, ["integration", "staging"])

    def test_get_workflow_branches_with_empty_config(self):
        """Should return an empty list."""
        result = _get_workflow_branches({}, "master")

        self.assertEqual(result, [])

    def test_get_workflow_branches_with_empty_workflow(self):
        """Should return an empty list."""
        result = _get_workflow_branches({"workflow": []}, "master")

        self.assertEqual(result, [])
