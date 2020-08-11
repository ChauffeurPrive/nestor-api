"""Define the workflow advance route."""

from http import HTTPStatus

from nestor_api.config.config import Configuration
import nestor_api.lib.config as config_lib
import nestor_api.lib.workflow as workflow_lib
from nestor_api.utils.error_handling import non_blocking_clean
from nestor_api.utils.logger import Logger


def advance_workflow(current_step):
    """Advance the workflow for all applications able to be advanced."""
    Logger.info(
        {"current_step": current_step},
        "[/api/workflow/progress/<current_step>] Workflow advance started",
    )

    try:
        # Creating a copy of the working configuration directory
        config_dir = config_lib.create_temporary_config_copy()
        config_lib.change_environment(Configuration.get_config_default_branch(), config_dir)
        project_config = config_lib.get_project_config(config_dir)

        report_status, report = workflow_lib.advance_workflow(
            config_dir, project_config, current_step
        )

        status, message = _get_status_and_message(report_status)

        # Clean up
        non_blocking_clean(config_dir, message_prefix="[/api/workflow/progress/<current_step>]")

        # HTTP Response
        Logger.info(
            {"current_step": current_step, "report": report},
            f"[/api/workflow/progress/<current_step>] {message}",
        )
        return (
            {"current_step": current_step, "report": report, "message": message},
            status,
        )
    # pylint: disable=broad-except
    except Exception as err:
        Logger.error(
            {"current_step": current_step, "err": str(err)},
            "[/api/workflow/progress/<current_step>] Workflow advance failed",
        )

        # HTTP Response
        return (
            {"current_step": current_step, "err": str(err), "message": "Workflow advance failed",},
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def _get_status_and_message(report_status: workflow_lib.WorkflowAdvanceStatus):
    """Return status and message according to provided report status."""
    if report_status == workflow_lib.WorkflowAdvanceStatus.SUCCESS:
        status = HTTPStatus.OK
        message = "Workflow advance succeeded"
    else:
        status = HTTPStatus.INTERNAL_SERVER_ERROR
        message = "Workflow advance failed"
    return status, message
