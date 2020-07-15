"""git library"""

import semver

import nestor_api.lib.io as io
from nestor_api.utils.logger import Logger


def branch(repository_dir: str, branch_name: str) -> None:
    """Checkout a branch of a repository"""
    Logger.debug({"path": repository_dir}, "[git#branch] Repository path")

    stdout = io.execute(f"git branch --list {branch_name}", repository_dir)

    exists = len(stdout) > 0

    io.execute(f'git checkout{"" if exists else " -b"} {branch_name}', repository_dir)


def create_working_repository(app_name: str, git_url: str) -> str:
    """Create a working copy of an app's repository"""
    pristine_directory = update_pristine_repository(app_name, git_url)

    repository_dir = io.create_temporary_copy(pristine_directory, app_name)

    Logger.debug(
        {"app": app_name, "repository": repository_dir},
        "[git#create_working_directory] Created a working repository",
    )

    return repository_dir


def get_last_tag(repository_dir: str) -> str:
    """Retrieves the last tag of a repository (locally)"""
    return io.execute("git describe --always --abbrev=0", repository_dir)


def get_remote_url(repository_dir: str, remote_name: str = "origin") -> str:
    """Retrieves the remote url of a repository"""
    return io.execute(f"git remote get-url {remote_name}", repository_dir)


def get_last_commit_hash(repository_dir: str) -> str:
    """Retrieves the last commit hash of a repository (locally)"""
    return io.execute("git rev-parse --short HEAD", repository_dir)


def get_commit_hash_from_tag(repository_dir: str, tag_name: str) -> str:
    """Returns the commit hash associated to the given tag"""
    return io.execute(f"git rev-list -1 {tag_name}", repository_dir)


def push(repository_dir: str, branch_name: str = "HEAD") -> None:
    """Push to the remote repository"""
    io.execute(f"git push origin {branch_name} --tags --follow-tags", repository_dir)


def tag(repository_dir: str, tag_name: str, tag_message: str = "Nestor auto-tag") -> str:
    """Add a tag to the repository"""
    commit_hash = get_last_commit_hash(repository_dir)

    final_tag = f"{tag_name}-sha-{commit_hash}"

    if not semver.VersionInfo.isvalid(final_tag):
        raise RuntimeError(f'Invalid version tag: "{final_tag}".')

    io.execute(f"git tag -a {final_tag} {commit_hash} -m {tag_message}", repository_dir)

    return final_tag


def update_pristine_repository(app_name: str, git_url: str) -> str:
    """Update the pristine repository of an application"""
    repository_dir = io.get_pristine_path(app_name)

    update_repository(repository_dir, git_url)

    Logger.debug(
        {"app": app_name, "repository": repository_dir},
        "[git#update_pristine_repository] Updated a pristine repository",
    )

    return repository_dir


def update_repository(repository_dir: str, git_url: str, revision: str = "origin/master") -> None:
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
