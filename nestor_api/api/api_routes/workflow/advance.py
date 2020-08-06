"""Define the workflow advance route."""

import nestor_api.lib.config as config_lib
import nestor_api.lib.io as io_lib
import nestor_api.lib.workflow as workflow_lib
from nestor_api.utils.logger import Logger


def advance_workflow(current_step):
    """Advance the workflow for all requested applications"""
    config_dir = None

    try:
        Logger.info(
            {"current_step": current_step},
            "[/api/workflow/progress/<current_step>] Pushing the application tags",
        )

        # Creating a copy of the working configuration directory
        config_dir = config_lib.create_temporary_config_copy()
        config_lib.change_environment("staging", config_dir)
        project_config = config_lib.get_project_config(config_dir)

        workflow_lib.advance_workflow(config_dir, project_config, current_step)

    except Exception as err:
        Logger.error(
            {"current_step": current_step, "err": str(err)},
            "[/api/workflow/progress/<current_step>] Error while progress the workflow for applications",
        )

    # Clean up
    try:
        if config_dir:
            io_lib.remove(config_dir)
    except Exception as err:
        Logger.error(
            {"err": str(err)}, "[/api/workflow/progress/<current_step>] Error during clean up",
        )
