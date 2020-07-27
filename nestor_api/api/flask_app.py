"""Return an initialized Flask application with the API."""
from flask import Flask

from nestor_api.api.api import get_apis
from nestor_api.api.public_routes import heartbeat


def create_app() -> Flask:
    """Initialize a Flask app."""
    app = Flask(__name__)

    # Note: heartbeat is exposed without authentication
    app.register_blueprint(heartbeat.blueprint)

    for api in get_apis():
        app.register_blueprint(api)

    return app
