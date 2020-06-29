# pylint: disable=missing-class-docstring disable=missing-function-docstring disable=missing-module-docstring

import subprocess
from unittest.mock import patch, call

import pytest

import nestor_api.lib.git as git


@pytest.mark.usefixtures("config")
# pylint: disable=no-self-use
@patch('nestor_api.lib.git.io', autospec=True)
class TestGitLibrary:
    def test_branch_existing(self, io_mock):
        io_mock.execute.side_effect = ["* feature/branch remotes/origin/feature/branch", ""]

        git.branch("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_has_calls([
            call(
                "git branch --list feature/branch",
                "/path_to/a_git_repository"
            ),
            call(
                "git checkout feature/branch",
                "/path_to/a_git_repository"
            )
        ])

    def test_branch_not_existing(self, io_mock):
        io_mock.execute.side_effect = ["", ""]

        git.branch("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_has_calls([
            call(
                "git branch --list feature/branch",
                "/path_to/a_git_repository"
            ),
            call(
                "git checkout -b feature/branch",
                "/path_to/a_git_repository"
            )
        ])

    @patch('nestor_api.lib.git.update_pristine_repository', autospec=True)
    @patch('nestor_api.lib.git.config', autospec=True)
    def test_create_working_repository(self, config_mock, update_pristine_repository_mock, io_mock):
        config_mock.get_app_config.return_value = {}
        update_pristine_repository_mock.return_value = "/fixtures-nestor-pristine/my-app"
        io_mock.create_temporary_copy.return_value = "/fixtures-nestor-work/my-app-11111111111111"

        repository_dir = git.create_working_repository("my-app")

        update_pristine_repository_mock.assert_called_once_with("my-app")
        io_mock.create_temporary_copy.assert_called_once_with("/fixtures-nestor-pristine/my-app", "my-app")
        assert repository_dir == "/fixtures-nestor-work/my-app-11111111111111"

    def test_get_last_commit_hash(self, io_mock):
        io_mock.execute.return_value = "1ab2c3d"

        last_commit_hash = git.get_last_commit_hash("/path_to/a_git_repository")

        assert last_commit_hash == "1ab2c3d"
        io_mock.execute.assert_called_once_with(
            "git rev-parse --short HEAD",
            "/path_to/a_git_repository"
        )

    def test_get_last_tag(self, io_mock):
        io_mock.execute.return_value = "1.0.0-sha-a2b3c4"

        last_tag = git.get_last_tag("/path_to/a_git_repository")

        assert last_tag == "1.0.0-sha-a2b3c4"
        io_mock.execute.assert_called_once_with(
            "git describe --always --abbrev=0",
            "/path_to/a_git_repository"
        )

    def test_get_remote_url_with_default_remote_name(self, io_mock):
        io_mock.execute.return_value = "git@github.com:org/repo.git"

        remote_url = git.get_remote_url("/path_to/a_git_repository")

        assert remote_url == "git@github.com:org/repo.git"
        io_mock.execute.assert_called_once_with(
            "git remote get-url origin",
            "/path_to/a_git_repository",
        )

    def test_get_remote_url_with_remote_name(self, io_mock):
        io_mock.execute.return_value = "git@github.com:org/repo.git"

        remote_url = git.get_remote_url("/path_to/a_git_repository", "custom_remote_name")

        assert remote_url == "git@github.com:org/repo.git"
        io_mock.execute.assert_called_once_with(
            "git remote get-url custom_remote_name",
            "/path_to/a_git_repository",
        )

    def test_push(self, io_mock):
        io_mock.execute.return_value = "git@github.com:org/repo.git"

        git.push("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_called_once_with(
            "git push origin feature/branch --tags --follow-tags",
            "/path_to/a_git_repository",
        )

    @patch('nestor_api.lib.git.config', autospec=True)
    def test_tag(self, config_mock, io_mock):
        config_mock.get_app_config.return_value = {"workflow": ["master", "staging", "production"]}
        io_mock.execute.side_effect = ["", "", "1ab2c3d", ""]

        tag = git.tag("/path_to/a_git_repository", "my-app", "1.0.0")

        config_mock.get_app_config.assert_called_once_with("my-app")
        assert io_mock.execute.call_count == 4
        assert io_mock.execute.mock_calls[3] == call(
            "git tag -a 1.0.0-sha-1ab2c3d 1ab2c3d",
            "/path_to/a_git_repository"
        )
        assert tag == "1.0.0-sha-1ab2c3d"

    @patch('nestor_api.lib.git.config', autospec=True)
    def test_tag_with_invalid_version(self, config_mock, io_mock):
        config_mock.get_app_config.return_value = {"workflow": ["master", "staging", "production"]}
        io_mock.execute.side_effect = ["", "", "1ab2c3d", ""]

        with pytest.raises(RuntimeError):
            git.tag("/path_to/a_git_repository", "my-app", "1.0")

    @patch('nestor_api.lib.git.update_repository', autospec=True)
    @patch('nestor_api.lib.git.config', autospec=True)
    def test_update_pristine_repository(self, config_mock, update_repository_mock, io_mock):
        config_mock.get_app_config.return_value = {"git": {"origin": "git@github.com:org/repo.git"}}
        update_repository_mock.return_value = ""
        io_mock.get_pristine_path.return_value = "/fixtures-nestor-pristine/my-app"

        repository_dir = git.update_pristine_repository("my-app")

        config_mock.get_app_config.assert_called_once_with("my-app")
        update_repository_mock.assert_called_once_with(
            "/fixtures-nestor-pristine/my-app",
            "git@github.com:org/repo.git"
        )
        assert repository_dir == "/fixtures-nestor-pristine/my-app"

    def test_update_repository_clone_if_not_existing_default_revision(self, io_mock):
        io_mock.exists.return_value = False
        io_mock.execute.side_effect = ["", ""]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls([
            call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
            call("git reset --hard origin/master", "/path_to/a_git_repository"),
        ])

    def test_update_repository_clone_if_not_existing_branch_revision(self, io_mock):
        io_mock.exists.return_value = False
        io_mock.execute.side_effect = ["", ""]

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/repo.git", "feature/branch"
        )

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls([
            call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
            call("git reset --hard feature/branch", "/path_to/a_git_repository"),
        ])

    def test_update_repository_remote_mismatch(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = ["git@github.com:org/repo.git", "", ""]

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/another_repo_url.git"
        )

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.remove.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls([
            call("git remote get-url origin", "/path_to/a_git_repository"),
            call("git clone git@github.com:org/another_repo_url.git /path_to/a_git_repository"),
            call("git reset --hard origin/master", "/path_to/a_git_repository"),
        ])

    def test_update_repository_remote_match_update(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = ["git@github.com:org/repo.git", "", "", ""]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls([
            call("git remote get-url origin", "/path_to/a_git_repository"),
            call("git clean -dfx", "/path_to/a_git_repository"),
            call("git fetch --all", "/path_to/a_git_repository"),
            call("git reset --hard origin/master", "/path_to/a_git_repository"),
        ])

    def test_update_repository_directory_is_not_repository(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = [
            subprocess.CalledProcessError(1, "git remote get-url origin"),
            "",
            ""
        ]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.remove.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls([
            call("git remote get-url origin", "/path_to/a_git_repository"),
            call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
            call("git reset --hard origin/master", "/path_to/a_git_repository"),
        ])

    def test_clone(self, io_mock):
        """Should send the right command to io lib."""
        git.clone('some/path', 'ssh://some-external-address/project.git', 'step-1')
        io_mock.execute.assert_called_once_with('git clone ssh://some-external-address/project.git -b step-1',
                                                'some/path')

    def test_clone_with_default_branch(self, io_mock):
        """Should send the right command to io lib using master as default branch."""
        git.clone('some/path', 'ssh://some-external-address/project.git')
        io_mock.execute.assert_called_once_with('git clone ssh://some-external-address/project.git -b master',
                                                'some/path')

    def test_get_branch_hash(self, io_mock):
        """Should send the right command to io lib."""
        git.get_branch_hash('ssh://some-external-address/project.git', 'master')
        io_mock.execute.assert_called_once_with('git ls-remote ssh://some-external-address/project.git master')
