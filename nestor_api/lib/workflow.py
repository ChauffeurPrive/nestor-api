"""Workflow library"""

from typing import Optional

import nestor_api.lib.config as config
import nestor_api.lib.git as git


def get_ready_to_progress_apps(next_step: str) -> dict:
    """Get a dict of every apps keyed by their name and whose
    value indicates if the app is ready to progress to next step
    or not."""
    # Copy the configuration to ensure strict isolation
    config_dir = config.create_temporary_config_copy()
    config.change_environment(next_step, config_dir)
    project_config = config.get_project_config()
    previous_step = config.get_previous_step(project_config, next_step)
    apps = config.list_apps_config()

    ready_to_progress_app: dict = {}

    for (app_name, app_config) in apps.items():
        repository_url = app_config["git"]["origin"]
        app_dir = git.create_working_repository(app_name, repository_url)
        ready_to_progress_app[app_name] = is_app_ready_to_progress(
            app_dir, previous_step, next_step
        )

    return ready_to_progress_app


def is_app_ready_to_progress(app_dir: str, current_step: Optional[str], next_step: str) -> bool:
    """Determines if an app can be advanced to the next step."""
    if current_step is None:
        return True
    return compare_step_hashes(app_dir, current_step, next_step)


def compare_step_hashes(app_dir: str, branch1: str, branch2: str) -> bool:
    """Compare branches hashes and return True if they are the sames, False otherwise."""
    git.branch(app_dir, branch1)
    branch1_hash = git.get_last_commit_hash(app_dir)
    git.branch(app_dir, branch2)
    branch2_hash = git.get_last_commit_hash(app_dir)
    return branch1_hash == branch2_hash
