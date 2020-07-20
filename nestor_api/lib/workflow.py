"""Workflow library"""

from typing import Optional

import nestor_api.lib.config as config
import nestor_api.lib.git as git
import nestor_api.lib.io as io


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
