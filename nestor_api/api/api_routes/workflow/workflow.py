"""Define the workflows routes."""
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


def advance_workflow(current_step, tags, *, sync):
    """Advance the workflow for all applications requested in body"""
    config_dir = None
    apps = []

    try:
        Logger.info(
            {"current_step": current_step, "tags": tags},
            "[/api/workflow/progress/<current_step>] Pushing the application tags",
        )

        if not sync:
            # return early response here
            pass

        # Creating a copy of the working configuration directory
        config_dir = config_lib.create_temporary_config_copy()

        Logger.debug(
            {"config_dir": config_dir},
            "[/api/workflow/progress/<current_step>] Changing environment to staging",
        )
        config_lib.change_environment("staging", config_dir)

        for (tag, app_name) in tags:
            try:
                app_dir = workflow_lib.advance_workflow_app(app_name, config_dir, tag, current_step)
                apps.append((app_name, app_dir))
            except Exception as err:
                Logger.error(
                    {
                        "app_name": app_name,
                        "config_dir": config_dir,
                        "tag": tag,
                        "current_step": current_step,
                        "err": str(err),
                    },
                    "[/api/workflow/progress/<current_step>] Error while advancing the workflow",
                )
        if sync:
            # Send response
            pass

    except Exception as err:
        Logger.error(
            {"current_step": current_step, "err": str(err)},
            "[/api/workflow/progress/<current_step>] Error while progress the workflow for applications",
        )

        if sync:
            # Handle error
            pass

    # Clean up
    try:
        if config_dir:
            io_lib.remove(config_dir)

        for (app_name, app_dir) in apps:
            io_lib.remove(app_dir)

    except Exception as err:
        Logger.error(
            {"err": str(err)}, "[/api/workflow/progress/<current_step>] Error during clean up",
        )
