from unittest import TestCase
from unittest.mock import MagicMock, patch

from github import AuthenticatedUser, Branch

from nestor_api.adapters.git.github_git_provider import GitHubGitProvider


@patch("nestor_api.adapters.git.GitHubGitProvider.Github", autospec=True)
class TestGitHubGitProvider(TestCase):
    @patch("nestor_api.adapters.git.GitHubGitProvider.Configuration", autospec=True)
    def test_init(self, configuration_mock, github_mock):
        configuration_mock.get_git_provider_token.return_value = "some-token"
        GitHubGitProvider()
        github_mock.assert_called_once_with("some-token")

    def test_get_user_info(self, github_mock):
        fake_user = MagicMock(spec=AuthenticatedUser.AuthenticatedUser)
        instance = github_mock.return_value
        instance.get_user.return_value = fake_user

        github_provider = GitHubGitProvider()
        result = github_provider.get_user_info()

        instance.get_user.assert_called_once()
        self.assertEqual(result, fake_user)

    def test_get_branch(self, github_mock):
        fake_branch_result = MagicMock(spec=Branch.Branch)
        instance = github_mock.return_value
        instance.get_repo.return_value.get_branch.return_value = fake_branch_result
        github_provider = GitHubGitProvider()
        result = github_provider.get_branch("organization", "fake-project", "fake-branch")
        instance.get_repo.assert_called_once_with("organization/fake-project")
        instance.get_repo.return_value.get_branch.assert_called_once_with(branch="fake-branch")
        self.assertEqual(result, fake_branch_result)

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_create_branch(self, get_branch_mock, github_mock):
        fake_branch_result = MagicMock(spec=Branch.Branch)
        instance = github_mock.return_value
        get_branch_mock.return_value = fake_branch_result
        github_provider = GitHubGitProvider()
        result = github_provider.create_branch(
            "organization", "fake-project", "fake-branch", "fake-sha1"
        )
        instance.get_repo.assert_called_once_with("organization/fake-project")
        instance.get_repo.return_value.create_git_ref.assert_called_once_with(
            "refs/heads/fake-branch", "fake-sha1"
        )
        get_branch_mock.assert_called_once_with(
            github_provider, "organization", "fake-project", "fake-branch"
        )
        self.assertEqual(result, fake_branch_result)

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch(self, get_branch_mock, _github_mock):
        github_provider = GitHubGitProvider()

        github_provider.protect_branch("organization", "fake-project", "fake-branch", "user_login")
        get_branch_mock.assert_called_once_with(
            github_provider, "organization", "fake-project", "fake-branch"
        )
        get_branch_mock.return_value.edit_protection.assert_called_once_with(
            enforce_admins=False, user_push_restrictions=["user_login"]
        )

    @patch.object(GitHubGitProvider, "get_branch", autospec=True)
    def test_protect_branch_on_unexisting_branch(self, get_branch_mock, _github_mock):
        github_provider = GitHubGitProvider()
        get_branch_mock.return_value = None

        with self.assertRaisesRegex(Exception, "Branch not found"):
            github_provider.protect_branch(
                "organization", "fake-project", "fake-branch", "user_login"
            )
