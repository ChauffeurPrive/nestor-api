"""git library"""

import semver

import nestor_api.lib.config as config
import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def branch(repository_dir, branch_name):
    """Checkout a branch of a repository"""
    Logger.debug({"path": repository_dir}, "[git#branch] Repository path")

    stdout = io.execute(f"git branch --list {branch_name}", repository_dir)

    exists = len(stdout) > 0

    io.execute(f'git checkout{"" if exists else " -b"} {branch_name}', repository_dir)


def create_working_repository(app_name):
    """Checkout a branch of a repository"""
    # First, update the pristine repository for this app
    pristine_directory = update_pristine_repository(app_name)

    repository_dir = io.create_temporary_copy(pristine_directory, app_name)

    Logger.debug(
        {app_name, repository_dir}, "[git#create_working_directory] Created a working repository",
    )

    return repository_dir


def get_last_tag(repository_dir):
    """Retrieves the last tag of a repository (locally)"""
    return io.execute("git describe --always --abbrev=0", repository_dir)


def get_remote_url(repository_dir, remote_name="origin"):
    """Retrieves the remote url of a repository"""
    return io.execute(f"git remote get-url {remote_name}", repository_dir)


def get_last_commit_hash(repository_dir):
    """Retrieves the last commit hash of a repository (locally)"""
    return io.execute("git rev-parse --short HEAD", repository_dir)


def push(repository_dir, branch_name="HEAD"):
    """Push to the remote repository"""
    io.execute(f"git push origin {branch_name} --tags --follow-tags", repository_dir)


def tag(repository_dir, app_name, tag_name):
    """Add a tag to the repository"""
    app_config = config.get_app_config(app_name)

    # Move to the corresponding environment branch
    branch(repository_dir, app_config.get("workflow")[0])

    # Extract the last commit hash:
    commit_hash = get_last_commit_hash(repository_dir)

    final_tag = f"{tag_name}-sha-{commit_hash}"

    if not semver.VersionInfo.isvalid(final_tag):
        raise RuntimeError(f'Invalid version tag: "{final_tag}".')

    io.execute(f"git tag -a {final_tag} {commit_hash}", repository_dir)

    return final_tag


def update_pristine_repository(app_name):
    """Update the pristine repository of an application"""
    app_config = config.get_app_config(app_name)

    repository_dir = io.get_pristine_path(app_name)

    update_repository(repository_dir, app_config.get("git").get("origin"))

    Logger.debug(
        {app_name, repository_dir},
        "[git#update_pristine_repository] Updated a pristine repository",
    )

    return repository_dir


def update_repository(repository_dir, git_url, revision="origin/master"):
    """Get the latest version of a revision or clone the repository"""
    should_clone = True

    if io.exists(repository_dir):
        # If the target directory already exists
        remote_url = None

        try:
            remote_url = get_remote_url(repository_dir)
        except Exception:  # pylint: disable=broad-except
            # If the directory is not a git repository, `get_remote_url` will throw
            pass

        if remote_url == git_url:
            # If the remotes are the same, clean and fetch
            io.execute("git clean -dfx", repository_dir)
            io.execute("git fetch --all", repository_dir)

            # No need to clone
            should_clone = False
        else:
            # If the remotes mismatch, remove the old one
            io.remove(repository_dir)

    if should_clone:
        io.execute(f"git clone {git_url} {repository_dir}")
    io.execute(f"git reset --hard {revision}", repository_dir)
