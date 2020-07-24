from unittest import TestCase

from nestor_api.adapters.git.github_git_provider import GitHubGitProvider
from nestor_api.adapters.git.provider import get_git_provider


class TestProvider(TestCase):
    def test_get_git_provider_with_github(self):
        git_provider = get_git_provider({"git": {"provider": "github"}})
        self.assertIsInstance(git_provider, GitHubGitProvider)

    def test_get_git_provider_without_defined(self):
        with self.assertRaisesRegex(
            NotImplementedError, "Adapter for this git provider is not implemented"
        ):
            get_git_provider({"git": {"provider": "some-git-provider"}})

    def test_get_git_provider_with_undefined_provider(self):
        with self.assertRaisesRegex(
            ValueError, "Git provider is not set in your project configuration file"
        ):
            get_git_provider({})
