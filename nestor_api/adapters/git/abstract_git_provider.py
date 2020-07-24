"""Abstract adapter for git provider."""

from abc import ABC, abstractmethod


class AbstractGitProvider(ABC):
    """Abstract adapter for git provider."""

    @abstractmethod
    def get_user_info(self):
        """Get logged in user information."""
        raise NotImplementedError()

    @abstractmethod
    def get_branch(self, organization: str, app_name: str, branch_name: str):
        """Get branch information."""
        raise NotImplementedError()

    @abstractmethod
    def create_branch(self, organization: str, app_name: str, branch_name: str, ref: str):
        """Create a branch."""
        raise NotImplementedError()

    @abstractmethod
    def protect_branch(self, organization: str, app_name: str, branch_name: str, user_login: str):
        """Protect a branch."""
        raise NotImplementedError()


class GitProviderError(Exception):
    """Base error for git provider."""
