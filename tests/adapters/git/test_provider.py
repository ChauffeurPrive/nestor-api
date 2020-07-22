from unittest import TestCase
from unittest.mock import patch

from nestor_api.adapters.git.github_git_provider import GitHubGitProvider
from nestor_api.adapters.git.provider import get_git_provider


@patch("nestor_api.adapters.git.provider.config", autospec=True)
class TestProvider(TestCase):
    def test_get_git_provider_with_github(self, config_mock):
        config_mock.get_project_config.return_value = {"git": {"provider": "github"}}
        git_provider = get_git_provider()
        config_mock.get_project_config.assert_called_once()
        self.assertIsInstance(git_provider, GitHubGitProvider)

    def test_get_git_provider_without_defined(self, config_mock):
        config_mock.get_project_config.return_value = {"git": {"provider": "some-git-provider"}}
        with self.assertRaisesRegex(
            NotImplementedError, "Adapter for this git provider is not implemented"
        ):
            get_git_provider()
        config_mock.get_project_config.assert_called_once()

    def test_get_git_provider_with_undefined_provider(self, config_mock):
        config_mock.get_project_config.return_value = {}
        with self.assertRaisesRegex(
            ValueError, "Git provider is not set in your project configuration file"
        ):
            get_git_provider()
        config_mock.get_project_config.assert_called_once()
