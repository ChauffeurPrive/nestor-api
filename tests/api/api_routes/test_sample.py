"""Test nestor_api.api.api_routes.sample."""
from nestor_api.api.flask_app import create_app


def test_hello_world_sample():
    """Should answer with an hello world on the sample route"""
    app = create_app()
    response = app.test_client().get("/api/sample")
    expected = (200, {"sample": "Hello, world!"})
    assert (response.status_code, response.json) == expected
