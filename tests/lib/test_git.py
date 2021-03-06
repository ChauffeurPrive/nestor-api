import subprocess
from unittest import TestCase
from unittest.mock import call, patch

import nestor_api.lib.git as git


@patch("nestor_api.lib.git.io", autospec=True)
class TestGitLibrary(TestCase):
    @patch("nestor_api.lib.git.is_branch_existing", autospec=True)
    def test_branch_existing(self, is_branch_existing_mock, io_mock):
        io_mock.execute.side_effect = ["* feature/branch remotes/origin/feature/branch", ""]
        is_branch_existing_mock.return_value = True

        git.branch("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_called_with(
            "git checkout feature/branch", "/path_to/a_git_repository"
        )

    @patch("nestor_api.lib.git.is_branch_existing", autospec=True)
    def test_branch_not_existing(self, is_branch_existing_mock, io_mock):
        io_mock.execute.side_effect = ["", ""]
        is_branch_existing_mock.return_value = False

        git.branch("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_called_with(
            "git checkout -b feature/branch", "/path_to/a_git_repository"
        )

    def test_is_branch_existing_with_existing_branch(self, io_mock):
        io_mock.execute.return_value = "* feature/branch remotes/origin/feature/branch"

        result = git.is_branch_existing("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_has_calls(
            [call("git branch --list feature/branch", "/path_to/a_git_repository"),]
        )
        self.assertEqual(result, True)

    def test_is_branch_existing_with_non_existing_branch(self, io_mock):
        io_mock.execute.return_value = ""

        result = git.is_branch_existing("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_has_calls(
            [call("git branch --list feature/branch", "/path_to/a_git_repository"),]
        )
        self.assertEqual(result, False)

    @patch("nestor_api.lib.git.update_pristine_repository", autospec=True)
    def test_create_working_repository(self, update_pristine_repository_mock, io_mock):
        update_pristine_repository_mock.return_value = "/fixtures-nestor-pristine/my-app"
        io_mock.create_temporary_copy.return_value = "/fixtures-nestor-work/my-app-11111111111111"

        repository_dir = git.create_working_repository("my-app", "git@github.com:org/repo.git")

        update_pristine_repository_mock.assert_called_once_with(
            "my-app", "git@github.com:org/repo.git"
        )
        io_mock.create_temporary_copy.assert_called_once_with(
            "/fixtures-nestor-pristine/my-app", "my-app"
        )
        self.assertEqual(repository_dir, "/fixtures-nestor-work/my-app-11111111111111")

    def test_get_commits_between_tags(self, io_mock):
        io_mock.execute.return_value = (
            "a1b1c1d Last known revision\n"
            + "a2b2c2d An older revision\n"
            + "a3b3c3d An even older revision\n"
        )

        commits = git.get_commits_between_tags("/path_to/a_git_repository", "old_tag", "new_tag")

        io_mock.execute.assert_called_once_with(
            "git log --oneline --no-decorate refs/tags/old_tag..refs/tags/new_tag",
            "/path_to/a_git_repository",
        )
        self.assertEqual(
            commits,
            [
                {"hash": "a1b1c1d", "message": "Last known revision"},
                {"hash": "a2b2c2d", "message": "An older revision"},
                {"hash": "a3b3c3d", "message": "An even older revision"},
            ],
        )

    def test_get_last_commit_hash_without_reference(self, io_mock):
        io_mock.execute.return_value = "1ab2c3d"

        last_commit_hash = git.get_last_commit_hash("/path_to/a_git_repository")

        self.assertEqual(last_commit_hash, "1ab2c3d")
        io_mock.execute.assert_called_once_with(
            "git rev-parse --short HEAD", "/path_to/a_git_repository"
        )

    def test_get_last_commit_hash_with_reference(self, io_mock):
        io_mock.execute.return_value = "1ab2c3d"

        last_commit_hash = git.get_last_commit_hash("/path_to/a_git_repository", "master")

        assert last_commit_hash == "1ab2c3d"
        io_mock.execute.assert_called_once_with(
            "git rev-parse --short master", "/path_to/a_git_repository"
        )

    def test_get_last_tag(self, io_mock):
        io_mock.execute.return_value = "1.0.0-sha-a2b3c4"

        last_tag = git.get_last_tag("/path_to/a_git_repository")

        self.assertEqual(last_tag, "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_called_once_with(
            "git describe --always --abbrev=0", "/path_to/a_git_repository"
        )

    def test_get_commit_hash_from_tag(self, io_mock):
        io_mock.execute.return_value = "a2b3c4d5e6f7g8h9"

        commit_hash = git.get_commit_hash_from_tag("/path_to/a_git_repository", "1.0.0-sha-a2b3c4")

        self.assertEqual(commit_hash, "a2b3c4d5e6f7g8h9")
        io_mock.execute.assert_called_once_with(
            "git rev-list -1 1.0.0-sha-a2b3c4", "/path_to/a_git_repository"
        )

    def test_get_remote_url_with_default_remote_name(self, io_mock):
        io_mock.execute.return_value = "git@github.com:org/repo.git"

        remote_url = git.get_remote_url("/path_to/a_git_repository")

        self.assertEqual(remote_url, "git@github.com:org/repo.git")
        io_mock.execute.assert_called_once_with(
            "git remote get-url origin", "/path_to/a_git_repository",
        )

    def test_get_remote_url_with_remote_name(self, io_mock):
        io_mock.execute.return_value = "git@github.com:org/repo.git"

        remote_url = git.get_remote_url("/path_to/a_git_repository", "custom_remote_name")

        self.assertEqual(remote_url, "git@github.com:org/repo.git")
        io_mock.execute.assert_called_once_with(
            "git remote get-url custom_remote_name", "/path_to/a_git_repository",
        )

    def test_push(self, io_mock):
        git.push("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_called_once_with(
            "git push origin feature/branch --tags --follow-tags", "/path_to/a_git_repository",
        )

    def test_rebase(self, io_mock):
        git.rebase("/path_to/a_git_repository", "feature/branch")

        io_mock.execute.assert_called_once_with(
            "git rebase feature/branch --keep-empty", "/path_to/a_git_repository",
        )

    def test_rebase_with_onto_ref(self, io_mock):
        git.rebase("/path_to/a_git_repository", "feature/branch", onto="tag")

        io_mock.execute.assert_called_once_with(
            "git rebase --onto tag feature/branch --keep-empty", "/path_to/a_git_repository",
        )

    @patch("nestor_api.lib.git.get_last_commit_hash", autospec=True)
    def test_tag(self, get_last_commit_hash_mock, io_mock):
        get_last_commit_hash_mock.return_value = "1ab2c3d"

        tag = git.tag("/path_to/a_git_repository", "1.0.0")

        io_mock.execute.assert_called_once_with(
            "git tag -a 1.0.0-sha-1ab2c3d 1ab2c3d -m 'NESTOR_AUTO_TAG'", "/path_to/a_git_repository"
        )
        self.assertEqual(tag, "1.0.0-sha-1ab2c3d")

    @patch("nestor_api.lib.git.get_last_commit_hash", autospec=True)
    def test_tag_with_invalid_version(self, get_last_commit_hash_mock, _io_mock):
        get_last_commit_hash_mock.return_value = "1ab2c3d"

        with self.assertRaises(RuntimeError):
            git.tag("/path_to/a_git_repository", "my-app", "1.0")

    @patch("nestor_api.lib.git.update_repository", autospec=True)
    def test_update_pristine_repository(self, update_repository_mock, io_mock):
        io_mock.get_pristine_path.return_value = "/fixtures-nestor-pristine/my-app"

        repository_dir = git.update_pristine_repository("my-app", "git@github.com:org/repo.git")

        update_repository_mock.assert_called_once_with(
            "/fixtures-nestor-pristine/my-app", "git@github.com:org/repo.git"
        )
        self.assertEqual(repository_dir, "/fixtures-nestor-pristine/my-app")

    def test_update_repository_clone_if_not_existing_default_revision(self, io_mock):
        io_mock.exists.return_value = False
        io_mock.execute.side_effect = ["", ""]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_clone_if_not_existing_branch_revision(self, io_mock):
        io_mock.exists.return_value = False
        io_mock.execute.side_effect = ["", ""]

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/repo.git", "feature/branch"
        )

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard feature/branch", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_remote_mismatch(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = ["git@github.com:org/repo.git", "", ""]

        git.update_repository(
            "/path_to/a_git_repository", "git@github.com:org/another_repo_url.git"
        )

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.remove.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clone git@github.com:org/another_repo_url.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_remote_match_update(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = ["git@github.com:org/repo.git", "", "", ""]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clean -dfx", "/path_to/a_git_repository"),
                call("git fetch --all", "/path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )

    def test_update_repository_directory_is_not_repository(self, io_mock):
        io_mock.exists.return_value = True
        io_mock.execute.side_effect = [
            subprocess.CalledProcessError(1, "git remote get-url origin"),
            "",
            "",
        ]

        git.update_repository("/path_to/a_git_repository", "git@github.com:org/repo.git")

        io_mock.exists.assert_called_once_with("/path_to/a_git_repository")
        io_mock.remove.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("git remote get-url origin", "/path_to/a_git_repository"),
                call("git clone git@github.com:org/repo.git /path_to/a_git_repository"),
                call("git reset --hard origin/master", "/path_to/a_git_repository"),
            ]
        )
