"""Workflow library init."""

from typing import Dict, List, Tuple

from nestor_api.adapters.git.abstract_git_provider import (
    AbstractGitProvider,
    GitProviderError,
    GitResource,
    GitResourceNotFoundError,
)
from nestor_api.config.git import GitConfiguration
import nestor_api.lib.config as config
from nestor_api.utils.logger import Logger
from nestor_api.lib.workflow.utils import non_blocking_clean
from nestor_api.lib.workflow.typings import (
    BranchReport,
    CreationStatus,
    ProtectionStatus,
    Report,
    WorkflowInitStatus,
)


class StepNotExistingInWorkflowError(Exception):
    """The step does not exist in the workflow"""

    pass


def init_workflow(
    organization: str, app_name: str, git_provider: AbstractGitProvider
) -> Tuple[WorkflowInitStatus, Report]:
    """Initialize the workflow of an application's repository by creating
    all workflow branches. This function is idempotent which means it will not
    try to recreate a branch that already exists. However if a branch
    already exists but is not protected, it will be set to protected."""

    # Create temporary copy for avoiding concurrency problems
    config_path = config.create_temporary_config_copy()

    # Switch to staging environment in order to get application configuration
    config.change_environment("staging", config_path)

    # Get application configuration to get the list of workflow branches
    app_config = config.get_app_config(app_name, config_path)
    master_tag = GitConfiguration.get_master_tag()

    workflow_branches = _get_workflow_branches(app_config, master_tag)
    branches = {}
    status = WorkflowInitStatus.SUCCESS

    if len(workflow_branches) != 0:
        status = WorkflowInitStatus.FAIL
        try:
            # Get user_login linked to the GITHUB_TOKEN
            user_info = git_provider.get_user_info()
            user_login = user_info.login if user_info else None
            Logger.info({"user_login": user_login}, "User login retrieved")

            # Get the last commit's sha on master branch
            branch = git_provider.get_branch(organization, app_name, master_tag)
            master_head_sha = branch and branch.commit and branch.commit.sha
            Logger.info({"sha": master_head_sha}, "master last commit sha retrieved")

            # Sync all workflow branches with master's head and
            # protect them by limiting push rights to user_login
            for branch_name in workflow_branches:
                branches[branch_name] = _create_and_protect_branch(
                    organization, app_name, branch_name, master_head_sha, user_login, git_provider
                )
        except GitResourceNotFoundError as err:
            Logger.error(
                {"master_branch_name": master_tag, "err": err},
                "master last commit sha failed to be retrieved.",
            )
        except GitProviderError as err:
            Logger.error(
                {"organization": organization, "app_name": app_name, "err": err},
                "Fail to initialize workflow",
            )
        else:
            status = WorkflowInitStatus.SUCCESS

    # Clean temporary copy
    non_blocking_clean(config_path)

    return status, branches


# pylint: disable=too-many-arguments
def _create_and_protect_branch(
    organization: str,
    app_name: str,
    branch_name: str,
    master_sha: str,
    user_login: str,
    git_provider: AbstractGitProvider,
) -> BranchReport:
    """Try to create and protect a branch on a repository."""
    report: BranchReport = {}
    branch = None
    try:
        branch = git_provider.get_branch(organization, app_name, branch_name)
        Logger.info({"branch_name": branch_name}, "Branch already exists. Skipped creation.")
        report["created"] = CreationStatus(False, True)
    except GitResourceNotFoundError as err:
        if err.resource == GitResource.BRANCH:
            branch = git_provider.create_branch(organization, app_name, branch_name, master_sha)
            Logger.info({"branch_name": branch_name}, "Branch created")
            report["created"] = CreationStatus(True, True)
        else:
            raise

    if branch.protected is True:
        Logger.info(
            {"branch_name": branch_name}, "Branch is already protected. Skipped protection."
        )
        report["protected"] = ProtectionStatus(False, True)
    else:
        git_provider.protect_branch(organization, app_name, branch_name, user_login)
        Logger.info({"branch_name": branch_name}, "Branch protected")
        report["protected"] = ProtectionStatus(True, True)
    return report


def _get_workflow_branches(app_config: Dict, master_tag: str) -> List[str]:
    workflow_from_conf = app_config["workflow"] if "workflow" in app_config else []
    return [branch_name for branch_name in workflow_from_conf if branch_name != master_tag]
