from unittest import TestCase
from unittest.mock import MagicMock, patch

from github import AuthenticatedUser, Branch, GithubException

from nestor_api.adapters.git.abstract_git_provider import GitProviderError
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

    def test_get_branch(self, github_mock):
        """Should get the branch data."""
        # Mocks
        fake_branch_result = MagicMock(spec=Branch.Branch)
        instance = github_mock.return_value
        instance.get_repo.return_value.get_branch.return_value = fake_branch_result
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.get_branch("organization", "fake-project", "fake-branch")

        # Assertions
        instance.get_repo.assert_called_once_with("organization/fake-project")
        instance.get_repo.return_value.get_branch.assert_called_once_with(branch="fake-branch")
        self.assertEqual(result, fake_branch_result)

    def test_get_branch_not_found(self, github_mock):
        """Should return None when the branch is not found."""
        # Mocks
        instance = github_mock.return_value
        instance.get_repo.return_value.get_branch.side_effect = GithubException(
            404, "branch not found"
        )
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.get_branch("organization", "fake-project", "fake-branch")

        # Assertions
        instance.get_repo.assert_called_once_with("organization/fake-project")
        instance.get_repo.return_value.get_branch.assert_called_once_with(branch="fake-branch")
        self.assertIsNone(result)

    def test_get_branch_failing(self, github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        instance = github_mock.return_value
        instance.get_repo.return_value.get_branch.side_effect = GithubException(500, "fake error")
        github_provider = GitHubGitProvider()

        with self.assertRaises(GitProviderError):
            github_provider.get_branch("organization", "fake-project", "fake-branch")

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_create_branch(self, get_branch_mock, github_mock):
        """Should create the branch and return its data."""
        # Mocks
        fake_branch_result = MagicMock(spec=Branch.Branch)
        instance = github_mock.return_value
        get_branch_mock.return_value = fake_branch_result
        github_provider = GitHubGitProvider()

        # Test
        result = github_provider.create_branch(
            "organization", "fake-project", "fake-branch", "fake-sha1"
        )

        # Assertions
        instance.get_repo.assert_called_once_with("organization/fake-project")
        instance.get_repo.return_value.create_git_ref.assert_called_once_with(
            "refs/heads/fake-branch", "fake-sha1"
        )
        get_branch_mock.assert_called_once_with(
            github_provider, "organization", "fake-project", "fake-branch"
        )
        self.assertEqual(result, fake_branch_result)

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_create_branch_failing_to_retrieve_branch_data(self, get_branch_mock, _github_mock):
        """Should raise an error when failing to retrieve branch data."""
        get_branch_mock.return_value = None
        github_provider = GitHubGitProvider()

        with self.assertRaisesRegex(
            GitProviderError, "Could not retrieve branch after ref creation"
        ):
            github_provider.create_branch(
                "organization", "fake-project", "fake-branch", "fake-sha1"
            )

    def test_create_branch_failing(self, github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        # Mocks
        instance = github_mock.return_value
        instance.get_repo.side_effect = GithubException(500, "fake error")
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
        get_branch_mock.return_value = None

        with self.assertRaisesRegex(GitProviderError, "Branch not found"):
            github_provider.protect_branch(
                "organization", "fake-project", "fake-branch", "user_login"
            )

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch_failing(self, get_branch_mock, _github_mock):
        """Should raise a GitProviderError when an unhandled error occurs."""
        github_provider = GitHubGitProvider()
        get_branch_mock.side_effect = GithubException(500, "fake error")

        with self.assertRaises(GitProviderError):
            github_provider.protect_branch(
                "organization", "fake-project", "fake-branch", "user_login"
            )
