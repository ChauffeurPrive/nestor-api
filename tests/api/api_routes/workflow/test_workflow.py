from http import HTTPStatus
from unittest import TestCase
from unittest.mock import MagicMock, patch

from nestor_api.adapters.git.abstract_git_provider import AbstractGitProvider
from nestor_api.api.flask_app import create_app


@patch("nestor_api.api.api_routes.workflow.workflow.Logger", autospec=True)
@patch("nestor_api.api.api_routes.workflow.workflow.io_lib", autospec=True)
class TestWorkflow(TestCase):
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.app_client = app.test_client()

    @patch("nestor_api.api.api_routes.workflow.workflow.get_git_provider", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.workflow_lib", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.config_lib", autospec=True)
    def test_init_workflow(
        self, config_mock, workflow_lib_mock, get_git_provider_mock, io_mock, _logger_mock
    ):
        """Should properly return success response containing report."""
        # Mock
        fake_config = {"git": {"provider": "some-provider"}}
        config_mock.get_project_config.return_value = fake_config
        get_git_provider_mock.return_value = MagicMock(spec=AbstractGitProvider)
        workflow_lib_mock.init_workflow.return_value = (
            "success",
            {"integration": {"created": (True, True), "protected": (True, True)}},
        )

        # Tests
        response = self.app_client.post("/api/workflow/init/my-org/my-app")
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            data,
            {
                "organization": "my-org",
                "message": "Workflow initialization succeeded",
                "app": "my-app",
                "report": {"integration": {"created": [True, True], "protected": [True, True]}},
            },
        )

        config_mock.get_project_config.assert_called_once_with("fake-path")
        get_git_provider_mock.assert_called_with(fake_config)
        io_mock.remove.assert_called_with("fake-path")

    @patch("nestor_api.api.api_routes.workflow.workflow.get_git_provider", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.workflow_lib", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.config_lib", autospec=True)
    def test_init_workflow_failing(
        self, config_mock, workflow_lib_mock, get_git_provider_mock, io_mock, _logger_mock
    ):
        """Should properly return fail response containing report."""
        # Mock
        fake_config = {"git": {"provider": "some-provider"}}
        config_mock.get_project_config.return_value = fake_config
        get_git_provider_mock.return_value = MagicMock(spec=AbstractGitProvider)
        workflow_lib_mock.init_workflow.return_value = ("fail", {})

        # Tests
        response = self.app_client.post("/api/workflow/init/my-org/my-app")
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(
            data,
            {
                "organization": "my-org",
                "message": "Workflow initialization failed",
                "app": "my-app",
                "report": {},
            },
        )

        config_mock.get_project_config.assert_called_once_with("fake-path")
        get_git_provider_mock.assert_called_with(fake_config)
        io_mock.remove.assert_called_with("fake-path")

    @patch("nestor_api.api.api_routes.workflow.workflow.get_git_provider", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.workflow_lib", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.config_lib", autospec=True)
    def test_init_workflow_return_unexpected_status(
        self, config_mock, workflow_lib_mock, get_git_provider_mock, io_mock, _logger_mock
    ):
        """Should properly return fail response containing error."""
        # Mock
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        fake_config = {"git": {"provider": "some-provider"}}
        config_mock.get_project_config.return_value = fake_config
        get_git_provider_mock.return_value = MagicMock(spec=AbstractGitProvider)
        workflow_lib_mock.init_workflow.return_value = ("unexpected-status", {})

        # Tests
        response = self.app_client.post("/api/workflow/init/my-org/my-app")
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(
            data,
            {
                "app": "my-app",
                "err": "Unexpected status: 'unexpected-status'",
                "message": "Workflow initialization failed",
                "organization": "my-org",
            },
        )

        config_mock.get_project_config.assert_called_once_with("fake-path")
        get_git_provider_mock.assert_called_with(fake_config)
        io_mock.remove.assert_not_called()

    @patch("nestor_api.api.api_routes.workflow.workflow.get_git_provider", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.workflow_lib.init_workflow", autospec=True)
    @patch("nestor_api.api.api_routes.workflow.workflow.config_lib", autospec=True)
    def test_init_workflow_with_fail_during_cleaning(
        self, config_mock, init_workflow_mock, get_git_provider_mock, io_mock, _logger_mock
    ):
        """Should not prevent the server to respond properly."""
        # Mock
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        fake_config = {"git": {"provider": "some-provider"}}
        config_mock.get_project_config.return_value = fake_config
        get_git_provider_mock.return_value = MagicMock(spec=AbstractGitProvider)
        init_workflow_mock.return_value = (
            WorkflowInitStatus.SUCCESS,
            {"integration": {"created": (True, True), "protected": (True, True)}},
        )
        io_mock.remove.side_effect = Exception("Some error during cleaning")

        # Tests
        response = self.app_client.post("/api/workflow/init/my-org/my-app")
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            data,
            {
                "organization": "my-org",
                "message": "Workflow initialization succeeded",
                "app": "my-app",
                "report": {"integration": {"created": [True, True], "protected": [True, True]}},
            },
        )

        config_mock.get_project_config.assert_called_once_with("fake-path")
        get_git_provider_mock.assert_called_with(fake_config)
        io_mock.remove.assert_called_with("fake-path")
