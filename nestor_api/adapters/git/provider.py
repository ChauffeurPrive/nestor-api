"""Selector for git provider."""

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider
from nestor_api.adapters.git.github_git_provider import GitHubGitProvider


def get_git_provider(project_config: dict) -> AbstractGitProvider:
    """Retrieve git provider corresponding to project configuration"""
    provider = project_config.get("git", {}).get("provider")
    if provider is None:
        raise ValueError("Git provider is not set in your project configuration file")

    if provider == "github":
        return GitHubGitProvider()
    raise NotImplementedError("Adapter for this git provider is not implemented")
