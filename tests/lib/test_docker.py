import subprocess
from unittest import TestCase
from unittest.mock import call, patch

import nestor_api.lib.docker as docker


# pylint: disable=no-self-use
class TestDockerLib(TestCase):
    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    def test_build_already_built(self, git_mock, has_docker_image_mock):
        # Mocks
        has_docker_image_mock.return_value = True
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}

        # Tests
        image_tag = docker.build("my-app", context)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        self.assertEqual(image_tag, "1.0.0-sha-a2b3c4")

    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.config", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    def test_build(self, io_mock, config_mock, git_mock, has_docker_image_mock):
        # Mocks
        app_config = {"build": {"variables": {"var1": "val1", "var2": "val2"}}}
        has_docker_image_mock.return_value = False
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        config_mock.get_app_config.return_value = app_config
        io_mock.execute.return_value = ""

        # Tests
        context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}
        image_tag = docker.build("my-app", context)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        config_mock.get_app_config.assert_called_once_with("my-app")
        io_mock.execute.assert_called_once_with(
            "docker build"
            " --tag my-app:1.0.0-sha-a2b3c4"
            " --build-arg var1=val1"
            " --build-arg var2=val2"
            " --build-arg COMMIT_HASH=a2b3c4"
            " /path_to/a_git_repository"
        )
        self.assertEqual(image_tag, "1.0.0-sha-a2b3c4")

    @patch("nestor_api.lib.docker.Logger", autospec=True)
    @patch("nestor_api.lib.docker.has_docker_image", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.config", autospec=True)
    @patch("nestor_api.lib.docker.io", autospec=True)
    # pylint: disable=too-many-arguments disable=bad-continuation
    def test_build_failure(
        self, io_mock, config_mock, git_mock, has_docker_image_mock, logger_mock
    ):
        # Mocks
        app_config = {"build": {"variables": {"var1": "val1", "var2": "val2"}}}
        has_docker_image_mock.return_value = False
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        config_mock.get_app_config.return_value = app_config

        exception = subprocess.CalledProcessError(1, "Docker build failed")
        io_mock.execute.side_effect = [exception]

        # Test
        context = {"commit_hash": "a2b3c4", "repository": "/path_to/a_git_repository"}
        with self.assertRaisesRegex(Exception, "Docker build failed"):
            docker.build("my-app", context)

        # Assertions
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        has_docker_image_mock.assert_called_once_with("my-app", "1.0.0-sha-a2b3c4")
        config_mock.get_app_config.assert_called_once_with("my-app")
        io_mock.execute.assert_called_once_with(
            "docker build"
            " --tag my-app:1.0.0-sha-a2b3c4"
            " --build-arg var1=val1"
            " --build-arg var2=val2"
            " --build-arg COMMIT_HASH=a2b3c4"
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

    @patch("nestor_api.lib.docker.io", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.config", autospec=True)
    def test_push_no_image(self, config_mock, git_mock, io_mock):
        # Mocks
        config_mock.get_app_config.return_value = {
            "docker": {"registry": {"organization": "my-organization"}}
        }
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        io_mock.execute.return_value = ""

        # Test
        with self.assertRaisesRegex(RuntimeError, "Docker image not available"):
            docker.push("my-app", "/path_to/a_git_repository")

        # Assertions
        config_mock.get_app_config.assert_called_once_with("my-app")
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_called_once_with("docker images my-app:1.0.0-sha-a2b3c4 --quiet")

    @patch("nestor_api.lib.docker.io", autospec=True)
    @patch("nestor_api.lib.docker.git", autospec=True)
    @patch("nestor_api.lib.docker.config", autospec=True)
    def test_push(self, config_mock, git_mock, io_mock):
        # Mocks
        config_mock.get_app_config.return_value = {
            "docker": {"registry": {"organization": "my-organization"}}
        }
        git_mock.get_last_tag.return_value = "1.0.0-sha-a2b3c4"
        io_mock.execute.side_effect = ["001122334455", "", ""]

        # Test
        docker.push("my-app", "/path_to/a_git_repository")

        # Assertions
        config_mock.get_app_config.assert_called_once_with("my-app")
        git_mock.get_last_tag.assert_called_once_with("/path_to/a_git_repository")
        io_mock.execute.assert_has_calls(
            [
                call("docker images my-app:1.0.0-sha-a2b3c4 --quiet"),
                call("docker tag my-app:1.0.0-sha-a2b3c4 my-organization/my-app:1.0.0-sha-a2b3c4"),
                call("docker push my-organization/my-app:1.0.0-sha-a2b3c4"),
            ]
        )
