# pylint: disable=missing-class-docstring disable=missing-function-docstring disable=missing-module-docstring

import subprocess
from unittest.mock import call

import pytest

import nestor_api.lib.config as config
import nestor_api.lib.git as git
import nestor_api.lib.io as io


@pytest.mark.usefixtures("config")
# pylint: disable=no-self-use
class TestGitLibrary:
    def test_branch_existing(self, mocker):
        mocker.patch.object(
            io, "execute", side_effect=["* feature/branch remotes/origin/feature/branch", ""],
        )

        git.branch("/path_to/a_git_repository", "feature/branch")

        io.execute.assert_has_calls(
            [
                call("git branch --list feature/branch", "/path_to/a_git_repository",),
                call("git checkout feature/branch", "/path_to/a_git_repository"),
            ]
        )

    def test_branch_not_existing(self, mocker):
        mocker.patch.object(io, "execute", side_effect=["", ""])

        git.branch("/path_to/a_git_repository", "feature/branch")

        io.execute.assert_has_calls(
            [
                call("git branch --list feature/branch", "/path_to/a_git_repository",),
                call("git checkout -b feature/branch", "/path_to/a_git_repository"),
            ]
        )

    def test_create_working_repository(self, mocker):
        mocker.patch.object(config, "get_app_config", return_value={})
        mocker.patch.object(
            git, "update_pristine_repository", return_value="/fixtures-nestor-pristine/my-app",
        )
        mocker.patch.object(
            io, "create_temporary_copy", return_value="/fixtures-nestor-work/my-app-11111111111111",
        )

        repository_dir = git.create_working_repository("my-app")

        git.update_pristine_repository.assert_called_once_with("my-app")

        io.create_temporary_copy.assert_called_once_with(
            "/fixtures-nestor-pristine/my-app", "my-app"
        )

        assert repository_dir == "/fixtures-nestor-work/my-app-11111111111111"

    def test_get_last_commit_hash(self, mocker):
        mocker.patch.object(io, "execute", return_value="1ab2c3d")

        last_commit_hash = git.get_last_commit_hash("/path_to/a_git_repository")

        assert last_commit_hash == "1ab2c3d"

        io.execute.assert_called_once_with(
            "git rev-parse --short HEAD", "/path_to/a_git_repository"
        )

    def test_get_last_tag(self, mocker):
        mocker.patch.object(io, "execute", return_value="1.0.0-sha-a2b3c4")

        last_tag = git.get_last_tag("/path_to/a_git_repository")

        assert last_tag == "1.0.0-sha-a2b3c4"

        io.execute.assert_called_once_with(
            "git describe --always --abbrev=0", "/path_to/a_git_repository"
        )

    def test_get_remote_url_with_default_remote_name(self, mocker):
        mocker.patch.object(io, "execute", return_value="git@github.com:org/repo.git")

        remote_url = git.get_remote_url("/path_to/a_git_repository")

        assert remote_url == "git@github.com:org/repo.git"

        io.execute.assert_called_once_with(
            "git remote get-url origin", "/path_to/a_git_repository",
        )

    def test_get_remote_url_with_remote_name(self, mocker):
        mocker.patch.object(io, "execute", return_value="git@github.com:org/repo.git")

        remote_url = git.get_remote_url("/path_to/a_git_repository", "custom_remote_name")

        assert remote_url == "git@github.com:org/repo.git"

        io.execute.assert_called_once_with(
            "git remote get-url custom_remote_name", "/path_to/a_git_repository",
        )

    def test_push(self, mocker):
        mocker.patch.object(io, "execute", return_value="git@github.com:org/repo.git")

        git.push("/path_to/a_git_repository", "feature/branch")

        io.execute.assert_called_once_with(
            "git push origin feature/branch --tags --follow-tags", "/path_to/a_git_repository",
        )

    def test_tag(self, mocker):
        mocker.patch.object(
            config,
            "get_app_config",
            return_value={"workflow": ["master", "staging", "production"]},
        )
        mocker.patch.object(io, "execute", side_effect=["", "", "1ab2c3d", ""])

        tag = git.tag("/path_to/a_git_repository", "my-app", "1.0.0")

        config.get_app_config.assert_called_once_with("my-app")

        assert io.execute.call_count == 4
        assert io.execute.mock_calls[3] == call(
            "git tag -a 1.0.0-sha-1ab2c3d 1ab2c3d", "/path_to/a_git_repository"
        )

        assert tag == "1.0.0-sha-1ab2c3d"

    def test_tag_with_invalid_version(self, mocker):
        mocker.patch.object(
            config,
            "get_app_config",
            return_value={"workflow": ["master", "staging", "production"]},
        )
        mocker.patch.object(io, "execute", side_effect=["", "", "1ab2c3d", ""])

        with pytest.raises(RuntimeError):
            git.tag("/path_to/a_git_repository", "my-app", "1.0")

    def test_update_pristine_repository(self, mocker):
        mocker.patch.object(
            config,
            "get_app_config",
            return_value={"git": {"origin": "git@github.com:org/repo.git"}},
        )
        mocker.patch.object(git, "update_repository", return_value="")

        repository_dir = git.update_pristine_repository("my-app")

        config.get_app_config.assert_called_once_with("my-app")
        git.update_repository.assert_called_once_with(
            "/fixtures-nestor-pristine/my-app", "git@github.com:org/repo.git"
        )

        assert repository_dir == "/fixtures-nestor-pristine/my-app"

    def test_update_repository_clone_if_not_existing_default_revision(self, mocker):
        mocker.patch.object(io, "exists", return_value=False)
        mocker.patch.object(io, "execute", side_effect=["", ""])

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io.exists.assert_called_once_with("/path_to/a_git_repository")
        io.execute.assert_has_calls(
            [
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_clone_if_not_existing_branch_revision(self, mocker):
        mocker.patch.object(io, "exists", return_value=False)
        mocker.patch.object(io, "execute", side_effect=["", ""])

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/repo.git", "feature/branch"
        )

        io.exists.assert_called_once_with("/path_to/a_git_repository")
        io.execute.assert_has_calls(
            [
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard feature/branch", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_remote_mismatch(self, mocker):
        mocker.patch.object(io, "exists", return_value=True)
        mocker.patch.object(io, "execute", side_effect=["git@github.com:org/repo.git", "", ""])
        mocker.patch.object(io, "remove")

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/another_repo_url.git"
        )

        io.exists.assert_called_once_with("/path_to/a_git_repository")
        io.remove.assert_called_once_with("/path_to/a_git_repository")
        io.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clone git@github.com:org/another_repo_url.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_remote_match_update(self, mocker):
        mocker.patch.object(io, "exists", return_value=True)
        mocker.patch.object(io, "execute", side_effect=["git@github.com:org/repo.git", "", "", ""])

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io.exists.assert_called_once_with("/path_to/a_git_repository")
        io.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clean -dfx", "/path_to/a_git_repository"),
                call("git fetch --all", "/path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_directory_is_not_repository(self, mocker):
        mocker.patch.object(io, "exists", return_value=True)
        mocker.patch.object(io, "remove")
        mocker.patch.object(
            io,
            "execute",
            side_effect=[subprocess.CalledProcessError(1, "git remote get-url origin"), "", "",],
        )

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io.exists.assert_called_once_with("/path_to/a_git_repository")
        io.remove.assert_called_once_with("/path_to/a_git_repository")
        io.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )
