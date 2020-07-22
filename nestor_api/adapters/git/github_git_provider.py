"""Git provider adapter for Github."""

from http import HTTPStatus
from typing import Optional, Union

from github import AuthenticatedUser, Branch, Github, GithubException, NamedUser

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider, GitProviderError
from nestor_api.config.config import Configuration


class GitHubGitProvider(AbstractGitProvider):
    """Git provider adapter for Github."""

    def __init__(self):
        self.__client = Github(Configuration.get_git_provider_token())

    def get_user_info(
        self,
    ) -> Union[NamedUser.NamedUser, AuthenticatedUser.AuthenticatedUser, None]:
        """Get logged in user information."""
        try:
            return self.__client.get_user()
        except GithubException:
            raise GitProviderError()

    def get_branch(
        self, organization: str, app_name: str, branch_name: str
    ) -> Optional[Branch.Branch]:
        """Get branch information."""
        try:
            repository = self.__client.get_repo(f"{organization}/{app_name}")
            return repository.get_branch(branch=branch_name)
        except GithubException as err:
            if err.status == HTTPStatus.NOT_FOUND:
                return None
            raise GitProviderError()

    def create_branch(
        self, organization: str, app_name: str, branch_name: str, ref: str
    ) -> Branch.Branch:
        """Create a branch."""
        try:
            repository = self.__client.get_repo(f"{organization}/{app_name}")
            repository.create_git_ref(f"refs/heads/{branch_name}", ref)
            return self.get_branch(organization, app_name, branch_name)
        except GithubException:
            raise GitProviderError()

    def protect_branch(
        self, organization: str, app_name: str, branch_name: str, user_login: str
    ) -> None:
        """Protect a branch."""
        try:
            branch = self.get_branch(organization, app_name, branch_name)
            if branch is None:
                raise Exception("Branch not found")
            branch.edit_protection(enforce_admins=False, user_push_restrictions=[user_login])
        except GithubException:
            raise GitProviderError()
