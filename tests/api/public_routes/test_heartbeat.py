"""Test nestor_api.api.public_routes.heartbeat."""
from flask.testing import FlaskClient
import pytest

from nestor_api.api.flask_app import create_app


def test_heartbeat_success():
    """Should return a 200 without restriction."""
    app = create_app()
    response = app.test_client().get("/heartbeat")
    expected = (200, b'{"state":"up"}\n')
    assert (response.status_code, response.data) == expected
