"""Test nestor_api.api.api_routes.sample."""
from unittest import TestCase

from nestor_api.api.flask_app import create_app


class TestApiRoutes(TestCase):
    def test_hello_world_sample(self):
        """Should answer with an hello world on the sample route"""
        app = create_app()
        response = app.test_client().get("/api/sample")
        expected = (200, {"sample": "Hello, world!"})
        self.assertEqual((response.status_code, response.json), expected)
