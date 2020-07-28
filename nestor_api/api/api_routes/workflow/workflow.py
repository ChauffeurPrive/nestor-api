"""Define the workflows routes."""
from http import HTTPStatus
import traceback

from nestor_api.adapters.git.provider import get_git_provider
import nestor_api.lib.config as config_lib
import nestor_api.lib.workflow as workflow_lib
from nestor_api.utils.logger import Logger


def init_workflow(organization, app):
    """Initialize workflow of an application."""
    Logger.debug(
        {"app": app, "organization": organization},
        "[/api/workflow/init/:org/:app] Workflow initialization started",
    )

    report = None
    try:
        # Retrieve project configuration
        project_config = config_lib.get_project_config()

        git_provider = get_git_provider(project_config)
        report_status, report = workflow_lib.init_workflow(organization, app, git_provider)

        if report_status == "fail":
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            message = "Workflow initialization failed"
        elif report_status == "success":
            status = HTTPStatus.OK
            message = "Workflow initialization succeeded"
        else:
            raise ValueError(f"Unexpected status: '{report_status}'")

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
        print(traceback.print_exc())
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
