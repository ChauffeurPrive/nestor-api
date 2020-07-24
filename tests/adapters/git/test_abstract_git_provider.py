# pylint: disable=abstract-class-instantiated

from unittest import TestCase
from unittest.mock import patch

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider


@patch.object(AbstractGitProvider, "__abstractmethods__", set())
class TestAbstractGitProvider(TestCase):
    def test_get_user_info(self):
        """Should raise a NotImplementedError."""
        git_provider = AbstractGitProvider()
        with self.assertRaises(NotImplementedError):
            git_provider.get_user_info()

    def test_get_branch(self):
        """Should raise a NotImplementedError."""
        git_provider = AbstractGitProvider()
        with self.assertRaises(NotImplementedError):
            git_provider.get_branch("organization", "app", "branch")

    def test_create_branch(self):
        """Should raise a NotImplementedError."""
        git_provider = AbstractGitProvider()
        with self.assertRaises(NotImplementedError):
            git_provider.create_branch("organization", "app", "branch", "ref")

    def test_protect_branch(self):
        """Should raise a NotImplementedError."""
        git_provider = AbstractGitProvider()
        with self.assertRaises(NotImplementedError):
            git_provider.protect_branch("organization", "app", "branch", "user_login")
