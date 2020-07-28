"""Workflow library"""

from enum import Enum
from typing import Dict, Optional, Tuple

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider, GitProviderError
from nestor_api.config.git import GitConfiguration
import nestor_api.lib.config as config
import nestor_api.lib.git as git
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


class WorkflowInitStatus(Enum):
    """Enum for workflow initialization status."""

    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


def get_apps_to_move_forward(next_step: str) -> dict:
    """Get a dict of every apps keyed by their name and whose
    value indicates if the app should progress to next step
    or not."""
    # Copy the configuration to ensure strict isolation
    config_dir = config.create_temporary_config_copy()
    config.change_environment(next_step, config_dir)
    project_config = config.get_project_config()
    previous_step = get_previous_step(project_config, next_step)
    apps = config.list_apps_config()

    ready_to_progress_app: dict = {}

    for (app_name, app_config) in apps.items():
        repository_url = app_config["git"]["origin"]
        app_dir = git.create_working_repository(app_name, repository_url)
        ready_to_progress_app[app_name] = should_app_progress(app_dir, previous_step, next_step)
        io.remove(app_dir)

    return ready_to_progress_app


def should_app_progress(app_dir: str, current_step: Optional[str], next_step: str) -> bool:
    """Determines if an app can be advanced to the next step."""
    if current_step is None:
        return True
    return are_step_hashes_equal(app_dir, current_step, next_step)


def are_step_hashes_equal(app_dir: str, branch1: str, branch2: str) -> bool:
    """Compare branches hashes and return True if they are the sames, False otherwise."""
    branch1_hash = git.get_last_commit_hash(app_dir, branch1)
    branch2_hash = git.get_last_commit_hash(app_dir, branch2)
    return branch1_hash == branch2_hash


def get_previous_step(project_config: dict, target: str) -> Optional[str]:
    """ Returns the previous step in the defined workflow """
    index = project_config["workflow"].index(target)
    if index > 0:
        return project_config["workflow"][index - 1]
    return None


def init_workflow(
    organization: str, app_name: str, git_provider: AbstractGitProvider
) -> Tuple[WorkflowInitStatus, Dict[str, Dict[str, Tuple[bool, bool]]]]:
    """Initialize workflow for a given repo by creating all workflow branches.
    This function is idempotent which means it will not try to recreate a
    branch that already exist. However if a branch already exist but is not protected,
    it will be set to protected."""

    # Switch to staging environment in order to get application configuration
    config.change_environment("staging")

    # Get application configuration to get the list of workflow branches
    app_config = config.get_app_config(app_name)
    workflow_from_conf = app_config["workflow"] if app_config else []
    master_tag = GitConfiguration.get_master_tag()

    workflow_branches = [
        branch_name for branch_name in workflow_from_conf if branch_name != master_tag
    ]

    branches = {}
    status = WorkflowInitStatus.SUCCESS
    if len(workflow_branches) != 0:
        try:
            # Get user_login linked to the GITHUB_TOKEN
            user_info = git_provider.get_user_info()
            print(user_info)
            user_login = user_info.login if user_info else None
            Logger.info({"user_login": user_login}, "User login retrieved")

            # Get the last commit's sha on master branch
            branch = git_provider.get_branch(organization, app_name, master_tag)
            master_head_sha = branch and branch.commit and branch.commit.sha
            if not master_head_sha:
                Logger.error(
                    {"master_branch_name": master_tag},
                    "master last commit sha failed to be retrieved.",
                )
                raise Exception("Repository looks empty")
            Logger.info({"sha": master_head_sha}, "master last commit sha retrieved")

            # Sync all workflow branches with master's head and
            # protect them by limiting push rights to user_login
            for branch_name in workflow_branches:
                branches[branch_name] = _create_and_protect_branch(
                    organization, app_name, branch_name, master_head_sha, user_login, git_provider
                )

        except GitProviderError as err:
            Logger.error(
                {"organization": organization, "app_name": app_name, "err": err},
                "Fail to initialize workflow",
            )
            status = WorkflowInitStatus.FAIL
    return status, branches


# pylint: disable=too-many-arguments
def _create_and_protect_branch(
    organization: str,
    app_name: str,
    branch_name: str,
    master_sha: str,
    user_login: str,
    git_provider: AbstractGitProvider,
) -> Dict[str, Tuple[bool, bool]]:
    """Try to create and protect a branch on a repository"""
    report = {}
    branch = git_provider.get_branch(organization, app_name, branch_name)
    if branch is not None:
        Logger.info({"branch_name": branch_name}, "Branch already exists. Skipped creation.")
        report["created"] = (False, True)
    else:
        branch = git_provider.create_branch(organization, app_name, branch_name, master_sha)
        Logger.info({"branch_name": branch_name}, "Branch created")
        report["created"] = (True, True)

    if branch.protected is True:
        Logger.info(
            {"branch_name": branch_name}, "Branch is already protected. Skipped protection."
        )
        report["protected"] = (False, True)
    else:
        git_provider.protect_branch(organization, app_name, branch_name, user_login)
        Logger.info({"branch_name": branch_name}, "Branch protected")
        report["protected"] = (True, True)
    return report
