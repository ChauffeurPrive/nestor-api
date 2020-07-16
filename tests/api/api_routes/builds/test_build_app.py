from unittest import TestCase
from unittest.mock import MagicMock, call, patch

from nestor_api.api.flask_app import create_app


def _mock_thread(target, args):
    mock = MagicMock()
    mock.start.side_effect = lambda: target(*args)
    return mock


# pylint: disable=bad-continuation
@patch("nestor_api.api.api_routes.builds.build_app.Thread", side_effect=_mock_thread)
@patch("nestor_api.api.api_routes.builds.build_app.Logger", autospec=True)
@patch("nestor_api.api.api_routes.builds.build_app.app", autospec=True)
@patch("nestor_api.api.api_routes.builds.build_app.config", autospec=True)
@patch("nestor_api.api.api_routes.builds.build_app.docker", autospec=True)
@patch("nestor_api.api.api_routes.builds.build_app.git", autospec=True)
@patch("nestor_api.api.api_routes.builds.build_app.io", autospec=True)
class TestApiBuildApp(TestCase):
    def setUp(self):
        self.app_client = create_app().test_client()

    @patch("nestor_api.api.api_routes.builds.build_app.Configuration", autospec=True)
    def test_build_app(
        self,
        configuration_mock,
        io_mock,
        git_mock,
        docker_mock,
        config_mock,
        app_mock,
        logger_mock,
        _thread_mock,
    ):
        # Mock
        configuration_mock.get_config_default_branch.return_value = "default"

        app_config = {
            "git": {"origin": "git@github.com:my-org/my-app.git"},
            "workflow": ["master", "production"],
        }
        config_mock.create_temporary_config_copy.return_value = "/tmp/config"
        config_mock.get_app_config.return_value = app_config

        git_mock.create_working_repository.return_value = "/tmp/working/repo"

        app_mock.get_version.return_value = "1.0.0"
        git_mock.tag.return_value = "1.0.0-sha-a1b2c3d4"

        docker_mock.build.return_value = "my-app@1.0.0-sha-a1b2c3d4"

        # Tests
        response = self.app_client.post("/api/builds/my-app")
        (status_code, text) = (response.status_code, response.get_data(as_text=True))

        # Assertions
        self.assertEqual(status_code, 202)
        self.assertEqual(text, "Build processing")

        config_mock.create_temporary_config_copy.assert_called_once()
        config_mock.change_environment.assert_called_once_with("default", "/tmp/config")
        config_mock.get_app_config.assert_called_once_with("my-app", "/tmp/config")

        git_mock.create_working_repository.assert_called_once_with(
            "my-app", "git@github.com:my-org/my-app.git"
        )
        git_mock.branch.assert_called_once_with("/tmp/working/repo", "master")

        app_mock.get_version.assert_called_once_with("/tmp/working/repo")
        git_mock.tag.assert_called_once_with("/tmp/working/repo", "1.0.0")

        docker_mock.build.assert_called_once_with("my-app", "/tmp/working/repo", app_config)
        docker_mock.push.assert_called_once_with("my-app", "my-app@1.0.0-sha-a1b2c3d4", app_config)

        git_mock.push.assert_called_once_with("/tmp/working/repo")

        io_mock.remove.assert_has_calls([call("/tmp/config"), call("/tmp/working/repo")])

        logger_mock.warn.assert_not_called()
        logger_mock.error.assert_not_called()

    def test_build_app_warn_if_tag_already_exists(
        self, _io_mock, git_mock, _docker_mock, config_mock, _app_mock, logger_mock, _thread_mock
    ):
        # Mock
        app_config = {
            "git": {"origin": "git@github.com:my-org/my-app.git"},
            "workflow": ["master", "production"],
        }
        config_mock.get_app_config.return_value = app_config

        exception = Exception("Tag already exists")
        git_mock.tag.side_effect = exception

        # Tests
        response = self.app_client.post("/api/builds/my-app")
        (status_code, text) = (response.status_code, response.get_data(as_text=True))

        # Assertions
        self.assertEqual(status_code, 202)
        self.assertEqual(text, "Build processing")

        logger_mock.warn.assert_called_once_with(
            {"app": "my-app", "err": exception}, "[/api/builds/:app] Error while tagging the app",
        )
        logger_mock.error.assert_not_called()

    def test_build_app_handle_errors(
        self, io_mock, git_mock, docker_mock, config_mock, _app_mock, logger_mock, _thread_mock
    ):
        # Mock
        app_config = {
            "git": {"origin": "git@github.com:my-org/my-app.git"},
            "workflow": ["master", "production"],
        }
        config_mock.get_app_config.return_value = app_config
        config_mock.create_temporary_config_copy.return_value = "/tmp/config"
        git_mock.create_working_repository.return_value = "/tmp/working/repo"

        exception = Exception("Build error")
        docker_mock.build.side_effect = exception

        # Tests
        response = self.app_client.post("/api/builds/my-app")
        (status_code, text) = (response.status_code, response.get_data(as_text=True))

        # Assertions
        self.assertEqual(status_code, 202)
        self.assertEqual(text, "Build processing")

        docker_mock.push.assert_not_called()
        git_mock.push.assert_not_called()

        io_mock.remove.assert_has_calls([call("/tmp/config"), call("/tmp/working/repo")])

        logger_mock.warn.assert_not_called()
        logger_mock.error.assert_called_once_with(
            {"app": "my-app", "err": exception},
            "[/api/builds/:app] Error while tagging and building the app",
        )

    def test_build_app_error_during_cleanup(
        self, io_mock, _git_mock, _docker_mock, config_mock, _app_mock, logger_mock, _thread_mock
    ):
        # Mock
        app_config = {
            "git": {"origin": "git@github.com:my-org/my-app.git"},
            "workflow": ["master", "production"],
        }
        config_mock.get_app_config.return_value = app_config

        exception = Exception("Could not remove directory")
        io_mock.remove.side_effect = exception

        # Tests
        response = self.app_client.post("/api/builds/my-app")
        (status_code, text) = (response.status_code, response.get_data(as_text=True))

        # Assertions
        self.assertEqual(status_code, 202)
        self.assertEqual(text, "Build processing")

        logger_mock.warn.assert_not_called()
        logger_mock.error.assert_called_once_with(
            {"app": "my-app", "err": exception}, "[/api/builds/:app] Error during cleanup",
        )
