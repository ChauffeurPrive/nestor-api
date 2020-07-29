import subprocess
from unittest import TestCase
from unittest.mock import call, patch

import nestor_api.lib.docker as docker


class TestDockerLib(TestCase):
    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_build_already_built(self, io_mock, git_mock, has_docker_image_mock):
        # Mocks
        has_docker_image_mock.return_value = True
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"

        # Tests
        repository = "/path_to/a_git_repository"
        app_config = {}

        image_tag = docker.build("my-app", repository, app_config)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_not_called()
        self.assertEqual(image_tag, "1.0.0-sha-a2b3c4")

    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_build(self, io_mock, git_mock, has_docker_image_mock):
        # Mocks
        has_docker_image_mock.return_value = False
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        git_mock.get_commit_hash_from_tag.return_value = "a2b3c4d5e6"
        io_mock.execute.return_value = ""

        # Tests
        repository = "/path_to/a_git_repository"
        app_config = {"docker": {"build": {"variables": {"var1": "val1", "var2": "val2"}}}}

        image_tag = docker.build("my-app", repository, app_config)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        git_mock.get_commit_hash_from_tag.assert_called_once_with(
            "/path_to/a_git_repository", "1.0.0-sha-a2b3c4"
        )
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_called_once_with(
            "docker build"
            " --tag my-app:1.0.0-sha-a2b3c4"
            " --build-arg var1=val1"
            " --build-arg var2=val2"
            " --build-arg COMMIT_HASH=a2b3c4d5e6"
            " /path_to/a_git_repository"
        )
        self.assertEqual(image_tag, "1.0.0-sha-a2b3c4")

    @patch("nestor_api.lib.docker.Logger", autospec=True)
    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_build_failure(self, io_mock, git_mock, has_docker_image_mock, logger_mock):
        # Mocks
        has_docker_image_mock.return_value = False
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        git_mock.get_commit_hash_from_tag.return_value = "a2b3c4d5e6"

        exception = subprocess.CalledProcessError(1, "Docker build failed")
        io_mock.execute.side_effect = [exception]

        # Test
        repository = "/path_to/a_git_repository"
        app_config = {}
        with self.assertRaisesRegex(Exception, "Docker build failed"):
            docker.build("my-app", repository, app_config)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        git_mock.get_commit_hash_from_tag.assert_called_once_with(
            "/path_to/a_git_repository", "1.0.0-sha-a2b3c4"
        )
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_called_once_with(
            "docker build"
            " --tag my-app:1.0.0-sha-a2b3c4"
            " --build-arg COMMIT_HASH=a2b3c4d5e6"
            " /path_to/a_git_repository"
        )
        logger_mock.error.assert_called_once_with(
            {"err": exception}, "Error while building Docker image"
        )

    def test_get_registry_image_tag(self):
        registry_image_tag = docker.get_registry_image_tag(
            "my-app", "my-tag", {"organization": "my-organization"}
        )
        self.assertEqual(registry_image_tag, "my-organization/my-app:my-tag")

    def test_get_version_from_image_tag(self):
        image_tag = "organization/project-name:0.0.0-sha-1a2bc34d"
        version = docker.get_version_from_image_tag(image_tag)
        self.assertEqual(version, "0.0.0-sha-1a2bc34d")

    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_has_docker_image_existing(self, io_mock):
        io_mock.execute.return_value = "001122334455"

        has_image = docker.has_docker_image("my-app", "my-tag")

        io_mock.execute.assert_called_once_with("docker images my-app:my-tag --quiet")
        self.assertTrue(has_image)

    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_has_docker_image_not_existing(self, io_mock):
        io_mock.execute.return_value = ""

        has_image = docker.has_docker_image("my-app", "my-tag")

        io_mock.execute.assert_called_once_with("docker images my-app:my-tag --quiet")
        self.assertFalse(has_image)

    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_push_no_image(self, io_mock, has_docker_image_mock):
        # Mocks
        has_docker_image_mock.return_value = False

        # Test
        app_config = {}

        with self.assertRaisesRegex(RuntimeError, "Docker image not available"):
            docker.push("my-app", "1.0.0-sha-a2b3c4", app_config)

        # Assertions
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_not_called()

    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_push(self, io_mock, has_docker_image_mock):
        # Mocks
        has_docker_image_mock.return_value = True
        io_mock.execute.side_effect = ["001122334455", "", ""]

        # Test
        app_config = {
            "docker": {"registries": {"docker.com": [{"organization": "my-organization"}]}}
        }

        docker.push("my-app", "1.0.0-sha-a2b3c4", app_config)

        # Assertions
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        io_mock.execute.assert_has_calls(
            [
                call("docker tag my-app:1.0.0-sha-a2b3c4 my-organization/my-app:1.0.0-sha-a2b3c4"),
                call("docker push my-organization/my-app:1.0.0-sha-a2b3c4"),
            ]
        )
