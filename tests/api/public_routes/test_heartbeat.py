"""Test nestor_api.api.public_routes.heartbeat."""
from nestor_api.api.flask_app import create_app


def test_heartbeat_success():
    """Should return a 204 without restriction."""
    app = create_app()
    response = app.test_client().get("/heartbeat")
    expected = 204
    assert (response.status_code) == expected
