from unittest import TestCase
from unittest.mock import MagicMock, patch

from github import AuthenticatedUser, Branch, GithubException, Repository

from nestor_api.adapters.git.abstract_git_provider import (
    GitProviderError,
    GitResource,
    GitResourceNotFoundError,
)
from nestor_api.adapters.git.github_git_provider import GitHubGitProvider


@patch("nestor_api.adapters.git.github_git_provider.Github", autospec=True)
class TestGitHubGitProvider(TestCase):
    @patch("nestor_api.adapters.git.github_git_provider.GitConfiguration", autospec=True)
    def test_init(self, git_configuration_mock, github_mock):
        """Should init the Github client."""
        git_configuration_mock.get_git_provider_token.return_value = "some-token"
        GitHubGitProvider()
        github_mock.assert_called_once_with("some-token")

    def test_get_user_info(self, github_mock):
        """Should get the user data."""
        # Mocks
        fake_user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        instance = github_mock.return_value
        instance.get_user.return_value = fake_user
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.get_user_info()

        # Assertions
        instance.get_user.assert_called_once()
        self.assertEqual(result, fake_user)

    def test_get_user_info_failing(self, github_mock):
        """Should raise a GitProviderError when failing."""
        instance = github_mock.return_value
        instance.get_user.side_effect = GithubException(500, "fake error")
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitProviderError):
            github_provider.get_user_info()

    def test_get_repository(self, github_mock):
        """Should get the repository information."""
        fake_repo = MagicMock(spec=Repository.Repository)
        instance = github_mock.return_value
        instance.get_repo.return_value = fake_repo
        github_provider = GitHubGitProvider()

        result = github_provider._get_repository("organization", "fake-project")

        self.assertEqual(result, fake_repo)
        instance.get_repo.assert_called_with("organization/fake-project")

    def test_get_repository_on_non_existing_repository(self, github_mock):
        """Should raise a GitResourceNotFoundError error."""
        instance = github_mock.return_value
        instance.get_repo.side_effect = GithubException(404, "fake error")
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitResourceNotFoundError) as context:
            github_provider._get_repository("organization", "fake-project")

        self.assertEqual(context.exception.resource, GitResource.REPOSITORY)

    def test_get_repository_failing(self, github_mock):
        """Should raise a GitProviderError error."""
        instance = github_mock.return_value
        instance.get_repo.side_effect = GithubException(500, "fake error")
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitProviderError):
            github_provider._get_repository("organization", "fake-project")

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    def test_get_branch(self, get_repository_mock, _github_mock):
        """Should get the branch data."""
        # Mocks
        fake_branch_result = MagicMock(spec=Branch.Branch)
        get_repository_mock.return_value.get_branch.return_value = fake_branch_result
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.get_branch("organization", "fake-project", "fake-branch")

        # Assertions
        get_repository_mock.assert_called_once_with(github_provider, "organization", "fake-project")
        get_repository_mock.return_value.get_branch.assert_called_once_with(branch="fake-branch")
        self.assertEqual(result, fake_branch_result)

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    def test_get_branch_not_found(self, get_repository_mock, _github_mock):
        """Should raise a GitResourceNotFoundError error
        when the branch is not found."""
        # Mocks
        get_repository_mock.return_value.get_branch.side_effect = GithubException(
            404, "branch not found"
        )
        github_provider = GitHubGitProvider()

        # Tests
        with self.assertRaises(GitResourceNotFoundError) as context:
            github_provider.get_branch("organization", "fake-project", "fake-branch")

        # Assertions
        self.assertEqual(context.exception.resource, GitResource.BRANCH)
        get_repository_mock.assert_called_once_with(github_provider, "organization", "fake-project")
        get_repository_mock.return_value.get_branch.assert_called_once_with(branch="fake-branch")

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    def test_get_branch_failing(self, get_repository_mock, _github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        get_repository_mock.return_value.get_branch.side_effect = GithubException(500, "fake error")
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitProviderError):
            github_provider.get_branch("organization", "fake-project", "fake-branch")

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_create_branch(self, get_branch_mock, get_repository_mock, _github_mock):
        """Should create the branch and return its data."""
        # Mocks
        fake_branch_result = MagicMock(spec=Branch.Branch)
        get_branch_mock.return_value = fake_branch_result
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.create_branch(
            "organization", "fake-project", "fake-branch", "fake-sha1"
        )

        # Assertions
        get_repository_mock.assert_called_once_with(github_provider, "organization", "fake-project")
        get_repository_mock.return_value.create_git_ref.assert_called_once_with(
            "refs/heads/fake-branch", "fake-sha1"
        )
        get_branch_mock.assert_called_once_with(
            github_provider, "organization", "fake-project", "fake-branch"
        )
        self.assertEqual(result, fake_branch_result)

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_create_branch_failing_to_retrieve_branch_data(
        self, get_branch_mock, get_repository_mock, _github_mock
    ):
        """Should raise an error when failing to retrieve branch data."""
        get_branch_mock.side_effect = GitResourceNotFoundError(GitResource.BRANCH)
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitResourceNotFoundError) as context:
            github_provider.create_branch(
                "organization", "fake-project", "fake-branch", "fake-sha1"
            )

        get_repository_mock.assert_called_with(github_provider, "organization", "fake-project")
        self.assertEqual(context.exception.resource, GitResource.BRANCH)

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    def test_create_branch_with_error_retrieving_repository(
        self, get_repository_mock, _github_mock
    ):
        """Should rethrow error."""
        # Mocks
        error = GitProviderError()
        get_repository_mock.side_effect = error
        github_provider = GitHubGitProvider()

        # Test
        with self.assertRaises(GitProviderError) as context:
            github_provider.create_branch(
                "organization", "fake-project", "fake-branch", "fake-sha1"
            )

        self.assertEqual(error, context.exception)

    @patch.object(GitHubGitProvider, "_get_repository", autospec=True)
    def test_create_branch_with_error_creating_ref(self, get_repository_mock, _github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        # Mocks
        fake_repository_result = MagicMock(spec=Repository.Repository)
        get_repository_mock.return_value = fake_repository_result
        get_repository_mock.return_value.create_git_ref.side_effect = GithubException(
            500, "fake error"
        )
        github_provider = GitHubGitProvider()

        # Test
        with self.assertRaises(GitProviderError):
            github_provider.create_branch(
                "organization", "fake-project", "fake-branch", "fake-sha1"
            )

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch(self, get_branch_mock, _github_mock):
        """Should protect the branch."""
        github_provider = GitHubGitProvider()

        github_provider.protect_branch("organization", "fake-project", "fake-branch", "user_login")
        get_branch_mock.assert_called_once_with(
            github_provider, "organization", "fake-project", "fake-branch"
        )
        get_branch_mock.return_value.edit_protection.assert_called_once_with(
            enforce_admins=False, user_push_restrictions=["user_login"]
        )

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch_on_non_existing_branch(self, get_branch_mock, _github_mock):
        """Should raise an error when trying to protect an non existing branch."""
        github_provider = GitHubGitProvider()
        get_branch_mock.side_effect = GitResourceNotFoundError(GitResource.BRANCH)

        with self.assertRaises(GitResourceNotFoundError) as context:
            github_provider.protect_branch(
                "organization", "fake-project", "fake-branch", "user_login"
            )

        self.assertEqual(context.exception.resource, GitResource.BRANCH)

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch_failing(self, get_branch_mock, _github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        github_provider = GitHubGitProvider()
        get_branch_mock.side_effect = GithubException(500, "fake error")

        with self.assertRaises(GitProviderError):
            github_provider.protect_branch(
                "organization", "fake-project", "fake-branch", "user_login"
            )
