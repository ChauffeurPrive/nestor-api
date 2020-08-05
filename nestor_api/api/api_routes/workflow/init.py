"""Define the workflow initialization route."""
from http import HTTPStatus

from nestor_api.adapters.git.provider import get_git_provider
from nestor_api.config.config import Configuration
import nestor_api.lib.config as config_lib
import nestor_api.lib.io as io_lib
import nestor_api.lib.workflow as workflow_lib
from nestor_api.utils.logger import Logger


def init_workflow(organization, app):
    """Initialize the workflow of an application."""
    Logger.debug(
        {"app": app, "organization": organization},
        "[/api/workflow/init/:org/:app] Workflow initialization started",
    )

    report = None
    try:
        # Retrieve project configuration
        config_dir = config_lib.create_temporary_config_copy()
        config_lib.change_environment(Configuration.get_config_default_branch(), config_dir)
        project_config = config_lib.get_project_config(config_dir)

        git_provider = get_git_provider(project_config)
        report_status, report = workflow_lib.init_workflow(organization, app, git_provider)

        if report_status == workflow_lib.WorkflowInitStatus.FAIL:
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            message = "Workflow initialization failed"
        elif report_status == workflow_lib.WorkflowInitStatus.SUCCESS:
            status = HTTPStatus.OK
            message = "Workflow initialization succeeded"
        else:
            raise ValueError(f"Unexpected status: '{report_status}'")

        # Clean the temporary directory
        try:
            io_lib.remove(config_dir)
        # pylint: disable=broad-except
        except Exception as err:
            Logger.warn(
                {"config_dir": config_dir, "err": err}, "Failed to clean temporary config dir"
            )

        # HTTP Response
        Logger.info(
            {"organization": organization, "app": app, "report": report},
            f"[/api/workflow/init/:org/:app] {message}",
        )
        return (
            {"organization": organization, "app": app, "report": report, "message": message},
            status,
        )
    # pylint: disable=broad-except
    except Exception as err:
        Logger.error(
            {"organization": organization, "app": app, "report": report, "err": str(err)},
            "[/api/workflow/init/:org/:app] Workflow initialization failed",
        )

        # HTTP Response
        return (
            {
                "organization": organization,
                "app": app,
                "err": str(err),
                "message": "Workflow initialization failed",
            },
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )
