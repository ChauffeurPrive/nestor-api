from http import HTTPStatus
from unittest import TestCase
from unittest.mock import patch

from nestor_api.api.api_routes.workflow.advance import _get_status_and_message
from nestor_api.api.flask_app import create_app
from nestor_api.lib.workflow import WorkflowAdvanceStatus


@patch("nestor_api.api.api_routes.workflow.advance.Logger", autospec=True)
class TestWorkflow(TestCase):
    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.app_client = app.test_client()

    @patch("nestor_api.api.api_routes.workflow.advance.non_blocking_clean", autospec=True)
    @patch(
        "nestor_api.api.api_routes.workflow.advance.workflow_lib.advance_workflow", autospec=True
    )
    @patch("nestor_api.api.api_routes.workflow.advance.config_lib", autospec=True)
    def test_advance_workflow(
        self, config_mock, advance_workflow_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should properly return success response containing report."""
        # Mock
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        fake_config = {"workflow": ["master", "staging", "production"]}
        config_mock.get_project_config.return_value = fake_config
        advance_workflow_mock.return_value = (
            WorkflowAdvanceStatus.SUCCESS,
            [
                {
                    "name": "app-1",
                    "tag": "0.0.0-sha-cf021d1",
                    "step": "staging",
                    "processes": [],
                    "cron_jobs": [],
                }
            ],
        )

        # Tests
        response = self.app_client.post("/api/workflow/progress/master")
        data = response.get_json()

        # Assertions
        config_mock.create_temporary_config_copy.assert_called_once()
        config_mock.change_environment.assert_called_once_with("staging", "fake-path")
        advance_workflow_mock.assert_called_once_with("fake-path", fake_config, "master")
        non_blocking_clean_mock.assert_called_once_with(
            "fake-path", message_prefix="[/api/workflow/progress/<current_step>]"
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            data,
            {
                "current_step": "master",
                "message": "Workflow advance succeeded",
                "report": [
                    {
                        "name": "app-1",
                        "tag": "0.0.0-sha-cf021d1",
                        "step": "staging",
                        "processes": [],
                        "cron_jobs": [],
                    }
                ],
            },
        )

    @patch("nestor_api.api.api_routes.workflow.advance.non_blocking_clean", autospec=True)
    @patch(
        "nestor_api.api.api_routes.workflow.advance.workflow_lib.advance_workflow", autospec=True
    )
    @patch("nestor_api.api.api_routes.workflow.advance.config_lib", autospec=True)
    def test_advance_workflow_with_status_failed(
        self, config_mock, advance_workflow_mock, non_blocking_clean_mock, _logger_mock
    ):
        """Should properly return success response containing report."""
        # Mock
        config_mock.create_temporary_config_copy.return_value = "fake-path"
        fake_config = {"workflow": ["master", "staging", "production"]}
        config_mock.get_project_config.return_value = fake_config
        advance_workflow_mock.return_value = (
            WorkflowAdvanceStatus.FAIL,
            [
                {
                    "name": "app-1",
                    "tag": "0.0.0-sha-cf021d1",
                    "step": "staging",
                    "processes": [],
                    "cron_jobs": [],
                }
            ],
        )

        # Tests
        response = self.app_client.post("/api/workflow/progress/master")
        data = response.get_json()

        # Assertions
        config_mock.create_temporary_config_copy.assert_called_once()
        config_mock.change_environment.assert_called_once_with("staging", "fake-path")
        advance_workflow_mock.assert_called_once_with("fake-path", fake_config, "master")
        non_blocking_clean_mock.assert_called_once_with(
            "fake-path", message_prefix="[/api/workflow/progress/<current_step>]"
        )
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(
            data,
            {
                "current_step": "master",
                "message": "Workflow advance failed",
                "report": [
                    {
                        "name": "app-1",
                        "tag": "0.0.0-sha-cf021d1",
                        "step": "staging",
                        "processes": [],
                        "cron_jobs": [],
                    }
                ],
            },
        )

    @patch("nestor_api.api.api_routes.workflow.advance.config_lib", autospec=True)
    def test_advance_workflow_failing(self, config_mock, _logger_mock):
        """Should properly return success response containing report."""
        # Mock
        config_mock.create_temporary_config_copy.side_effect = Exception("fake-error")

        # Tests
        response = self.app_client.post("/api/workflow/progress/master")
        data = response.get_json()

        # Assertions
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(
            data,
            {"current_step": "master", "message": "Workflow advance failed", "err": "fake-error"},
        )

    def test_get_status_and_message_for_success(self, _logger_mock):
        """Should properly return status and message."""

        # Tests
        status, message = _get_status_and_message(WorkflowAdvanceStatus.SUCCESS)

        # Assertions
        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(message, "Workflow advance succeeded")

    def test_get_status_and_message_for_fail(self, _logger_mock):
        """Should properly return status and message."""

        # Tests
        status, message = _get_status_and_message(WorkflowAdvanceStatus.FAIL)

        # Assertions
        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(message, "Workflow advance failed")
