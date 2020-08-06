"""Workflow library advance."""
from typing import Dict, Optional, Tuple

import nestor_api.lib.config as config
import nestor_api.lib.git as git
from nestor_api.utils.logger import Logger
from nestor_api.lib.workflow.utils import non_blocking_clean
from nestor_api.lib.workflow.errors import StepNotExistingInWorkflowError


def advance_workflow(config_dir: str, project_config: Dict, current_step: str):
    """Advance the application workflow to the next step"""
    progress_report = []
    next_step = get_next_step(project_config, current_step)

    for (app_name, app_config) in config.list_apps_config(config_dir).items():
        should_app_progress = False
        tag = None
        app_dir = None
        try:
            # Determine if app is ready to progress or not
            app_dir = git.create_working_repository(app_name, app_config["git"]["origin"])
            should_app_progress, tag = get_app_progress_report(app_dir, current_step, next_step)

            # If app is ready to progress, make it advance to the next step in the workflow
            Logger.info(
                {
                    "app": app_name,
                    "tag": tag,
                    "current_step": current_step,
                    "next_step": next_step,
                },
                "Advancing to the next workflow step"
                if should_app_progress
                else "App is already up-to-date. Skipping.",
            )
            if should_app_progress:
                git.branch(app_dir, next_step)
                git.rebase(app_dir, current_step, onto=tag)
                git.push(app_dir)

                processes = config.get_processes(app_config)
                cron_jobs = config.get_cronjobs(app_config)

                # TODO Unused but should be inserted in MongoDB.
                #  We should find a solution to retrieve it on the "other side"
                progress_report.append(
                    {
                        "name": app_name,
                        "tag": tag,
                        "step": next_step,
                        "processes": processes,
                        "cron_jobs": cron_jobs,
                    }
                )

                # TODO How to deal with those specific lines :
                #  https://github.com/transcovo/nestor-api/blob/master/src/processes/web/api/workflow/index.js#L165
        except Exception as err:
            Logger.error(
                {
                    "app_name": app_name,
                    "config_dir": config_dir,
                    "should_app_progress": should_app_progress,
                    "tag": tag,
                    "current_step": current_step,
                    "err": str(err),
                },
                "Error while advancing the workflow",
            )

        if app_dir is not None:
            non_blocking_clean(app_dir)

    return progress_report


def get_app_progress_report(app_dir: str, current_step: str, next_step: str) -> Tuple[bool, str]:
    """Determines if an app can be advanced to the next step."""

    # Switch to current step branch to retrieve last tag hash
    git.branch(app_dir, current_step)
    last_tag = git.get_last_tag(app_dir)

    # If the next_step branch is not existing then consider it ready-to-progress
    if not git.is_branch_existing(app_dir, next_step):
        should_app_progress = True
    else:
        last_tag_hash = git.get_commit_hash_from_tag(app_dir, last_tag)
        next_step_hash = git.get_last_commit_hash(app_dir, next_step)
        should_app_progress = last_tag_hash != next_step_hash
    return should_app_progress, last_tag


def get_next_step(project_config: dict, target: str) -> Optional[str]:
    """ Returns the next step in the defined workflow."""
    workflow = project_config["workflow"] if project_config else []
    try:
        index = workflow.index(target)
    except ValueError:
        raise StepNotExistingInWorkflowError()
    if index < (len(workflow) - 1):
        return project_config["workflow"][index + 1]
    return None
