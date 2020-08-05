"""Define the workflow advance route."""

import nestor_api.lib.config as config_lib
import nestor_api.lib.io as io_lib
import nestor_api.lib.workflow as workflow_lib
from nestor_api.utils.logger import Logger


def advance_workflow(current_step, tags, *, sync):
    """Advance the workflow for all requested applications"""
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
